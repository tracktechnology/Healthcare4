# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from erpnext.accounts.doctype.patient_due.patient_due import set_patient_due
from erpnext.accounts.doctype.company_due.company_due import set_company_due
from datetime import timedelta,datetime
from erpnext.controllers.myutils import get_dic_from_str,get_dic_from_doc
from healthcare.healthcare.healthcare_utils import set_observation_request,get_medical_insurance_percent,get_item_price,get_medical_insurance_room_percent,get_item_practitioner_type
from healthcare.healthcare.reservation_accounts import set_insurance_company_sales_invoice,set_contract_invoice
from healthcare.healthcare.doctype.room.room import calculate_booking_room,delete_room_patient
from frappe.utils import now

class NursingTool(Document):

	@frappe.whitelist()
	def set_clinical_procedure_items(self):
		price=0
		items=[]
		for i in self.clinical_procedure:
			procedure=frappe.get_doc("Clinical Procedure Template",i.clinical_procedure)
			if procedure.items:
				for item in procedure.items:
					items.append({"item_name":item.item_name,"qty":item.qty*i.qty,"doctor":self.doctor_procedure})

			if procedure.reuse_by_count:
				items.append({"item_name":procedure.name,"qty":i.qty,"doctor":self.doctor_procedure})

			else:
				items.append({"item_name":procedure.name,"qty":1,"doctor":self.doctor_procedure})

			

		self.set_patient_items(self.patient_name,items,items_type="clinical_procedure",department="Clinical Procedure")

			# self.output=str(price)

	@frappe.whitelist()
	def set_checkout_room(self,room,check_in,name):
		frappe.db.set_value("Inpatient Record",self.patient,"status","Discharged")

		patient_percentage=company_percentage=hospital_percentage=0
		patient_qty,patient_rate,patient_room_type=calculate_booking_room(room=room,check_in=check_in)
		if self.health_insurance:
			insurance_room_type=get_insurance_room(self.medical_insurance_company,self.reservation_type)

			patient_percentage,company_percentage,hospital_percentage=get_medical_insurance_room_percent(self.medical_insurance_company,insurance_room_type)
		
			
			qty,rate,room_type=calculate_booking_room(room_type=insurance_room_type,check_in=check_in)

			patient_rate=patient_rate-rate+ (rate*patient_percentage/100)


			items = [{
				"item_name": room_type,
				"service": room_type,
				"qty": qty,
				"rate":rate,
				"grand_total":rate,
				'reservation_type': self.reservation_type,
				'inpatient_record': self.patient
			}]

			if company_percentage:
				set_company_due(self.patient_name,self.medical_insurance,items,company_percentage)
			if hospital_percentage:
				set_contract_invoice(insurance_company=self.medical_insurance,
										percentage=hospital_percentage,items=items, inpatient_record=self.patient)



		items = [{
			"item_name": patient_room_type,
			"service": patient_room_type,
			"qty": patient_qty,
			"rate":patient_rate,
			"grand_total":patient_rate,
			'reservation_type': self.reservation_type,
			'inpatient_record': self.patient
		}]
		set_patient_due(
				patient=self.patient_name,
				items=items,
				)
							
		delete_room_patient(self.patient_name,room)
		frappe.db.sql(f"UPDATE `tabInpatient Room Details` SET invoiced=1 , check_out='{now()}' where name='{name}'")

		frappe.db.commit()


	@frappe.whitelist()
	def load_medical_services(self):
		frappe.msgprint(str("loading services"))

		self.medical_services = []
		if not self.medical_service_patient:
			return
		inpatient = frappe.get_doc("Inpatient Record", self.medical_service_patient)
		for service in inpatient.medical_services:
			if service.ended == 0:
				service_dict = get_dic_from_doc(service)
				service_dict["source"] = service.name
				frappe.msgprint(str(service_dict))
				self.append("medical_services",service_dict)


	@frappe.whitelist()
	def set_observation_request(self, observation_type,imaging_type=None):
		patient_percentage=company_percentage=hospital_percentage=doctor_percentage=0
		if  self.health_insurance:
			patient_percentage,company_percentage,hospital_percentage,doctor_percentage=get_medical_insurance_percent(self.medical_insurance_company,observation_type,self.reservation_type)
		if self.patient_name:
			set_observation_request(patient_name=self.patient_name	,observation_category=observation_type,
							reservation_type="Emergency",imaging_type=imaging_type,
							company_percentage=company_percentage,hospital_percentage=hospital_percentage,
							patient_percentage=patient_percentage,medical_insurance=self.medical_insurance)

		

	@frappe.whitelist()
	def set_patient_items(self,patient_name,items,items_type,department):
		patient_percentage=company_percentage=hospital_percentage=doctor_discount=0
		if  self.health_insurance:
			patient_percentage,company_percentage,hospital_percentage,doctor_discount=get_medical_insurance_percent(self.medical_insurance_company,department,self.reservation_type)
		

		items_list=[]
		for i in items:
			i['item_name']=get_item_practitioner_type(i.get("doctor"),item=i.get('item_name'),
											 item_group=i.get('item_group'),reservation_type=self.reservation_type)
			# frappe.throw(str(i['item_name']))
			rate =get_item_price(i['item_name'],reservation_type=self.reservation_type)
			items_list.append({
				"service": i.get("item_name"),
				"item_name": i.get("item_name"),
				"qty":  i.get("qty") or 1,
				"grand_total":rate,
				"rate":rate,
				'reservation_type':self.reservation_type,
				"inpatient_record":self.patient,
				"doctor":i.get("doctor"),
			})
		self.set_inpatient_record(items,items_type)

		set_patient_due(patient_name,items_list,patient_percentage,doctor_discount,department)
		if company_percentage :
			set_company_due(patient_name,self.medical_insurance,items_list,company_percentage)
			
		if hospital_percentage:
			set_contract_invoice(insurance_company=self.medical_insurance,
						percentage=hospital_percentage,items=items_list, inpatient_record=self.patient)
			

	def set_inpatient_record(self,items,items_type):
		doc=frappe.get_doc("Inpatient Record",self.patient)

		if items_type=="observation":
			set_patient_record_items(doc,items,"lab_test_prescription","observation_template")
		elif items_type=="request_doctor":
			for i in items:
				doc.append("items", {
							"item": i['item_name'],
							"description": i['doctor'],
						})
				
				doc.save(ignore_permissions=True)

		elif items_type=="clinical_procedure":
			# set_patient_record_items(doc,items,"procedure_prescription","procedure")
			for i in items:
				doc.append("procedure_prescription", {
							"procedure": i['item_name'],
							"qty": i['qty'],
							"practitioner":i['doctor']
						})
				
			doc.save(ignore_permissions=True)

		elif items_type=="medication":
			set_patient_record_items(doc,items,"drug_prescription","medication")

		return doc.reservation_type


	@frappe.whitelist()
	def get_patient_history(self):
		doc=frappe.get_doc("Inpatient Record",self.patient_history)
		self.patient_name=doc.patient
		self.reservation_type=doc.reservation_type
		if doc.medical_insurance_company:

			self.medical_insurance_company=doc.medical_insurance_company
			self.health_insurance=1
			self.medical_insurance=doc.medical_insurance
		# self.room=doc.room
		self.room=[]
		for i in doc.room:
			if not i.invoiced:
				self.append("room",
				i.as_dict()
				)

		doc=doc.as_dict()

		self.history_items=[]
		invoice_items=frappe.db.sql(f"""select grand_total,qty,item_name,I.reservation_type from 
					`tabSales Invoice Item` I,`tabSales Invoice`SI where I.parent=SI.name and 
					SI.patient='{self.patient_name}'and SI.status='Paid' order by SI.posting_date DESC""",as_dict=1)
		if frappe.db.exists('Patient Due',self.patient_name):
			patient_due=frappe.get_doc("Patient Due",self.patient_name)
			self.history_items=patient_due.due_details
		for  i in invoice_items:
			self.append("history_items",{
				"item_code":i.item_name,
				"qty":i.qty,
				"amount":i.grand_total,
				"reservation_type":i.reservation_type
			})
		
def set_patient_record_items(doc,items,ct_name,label):
		for i in items:
			doc.append(ct_name, {
						label: i['item_name'],
					})
		doc.save(ignore_permissions=True)



@frappe.whitelist()
def get_check_out_time(check_in,period,period_count,service_count):
	if not check_in:
		frappe.throw("Please set check in first")
	in_hours = frappe.db.get_value("Period",period,"in_hours")
	hours_to_add = float(service_count) * in_hours
	date_obj = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S")
	return date_obj + timedelta(hours=hours_to_add)


@frappe.whitelist()
def get_service_count(check_in,check_out,period,period_count):
	if not check_in:
		frappe.throw("Please set check in first")
	in_time = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S")
	out_time = datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S")
	time_difference = out_time - in_time
	difference_in_hours = time_difference.total_seconds() / 3600
	in_hours = frappe.db.get_value("Period",period,"in_hours")
	service_count= 1.0 * difference_in_hours / in_hours
	return service_count


@frappe.whitelist()
def add_medical_service(inpatient_record,medical_service_row,reservation_type,patient,health_insurance,medical_insurance_company=None,
                		medical_insurance=None):
	
	inpatient = frappe.get_doc("Inpatient Record",inpatient_record)
	service = get_dic_from_str(medical_service_row)
	if service.get("by_period") == 0 or service.get("ended") == 1:
		service["ended"] = 1
		# add_medical_service_due(inpatient.patient,service,inpatient.reservation_type)
		add_medical_service_due(service=service,reservation_type=reservation_type,
						  inpatient_record=inpatient.name,health_insurance=health_insurance,
						  medical_insurance=medical_insurance,
						  medical_insurance_company=medical_insurance_company,patient=patient)

	inpatient.append("medical_services", service)
	inpatient.save()



@frappe.whitelist()
def update_medical_service(inpatient_record,medical_service_row,reservation_type,patient,health_insurance,medical_insurance_company=None,
                		medical_insurance=None):
	service = get_dic_from_str(medical_service_row)
	service_item = frappe.get_doc("Medical Service Prescription",service["source"])
	skip_keys = ["source","name"]
	for key,value in service.items():
		if key not in skip_keys:
			# frappe.msgprint(key + "::" + str(value))
			service_item.db_set(key,value)
	if service_item.ended == 1:
		# patient = frappe.get_value("Inpatient Record",service_item.parent,"patient")
		# frappe.throw(str(service_item.parent))
		# add_medical_service_due(patient=patient,service=service_item,reservation_type=reservation_type,inpatient_record=service_item.parent)
		add_medical_service_due(service=service,reservation_type=reservation_type,
						  inpatient_record=inpatient_record,health_insurance=health_insurance,
						  medical_insurance=medical_insurance,
						  medical_insurance_company=medical_insurance_company,patient=patient)



@frappe.whitelist()
def remove_medical_service(source):
	if source:
		frappe.delete_doc("Medical Service Prescription",source)


def add_medical_service_due(service,reservation_type,inpatient_record,patient,health_insurance,medical_insurance=None,medical_insurance_company=None):
	rate=get_item_price(service.get("service"))
	items = [{
		"item_name": service.get("service"),
		"service": service.get("service"),
		"qty": service.get("service_count"),
		"rate":rate,
		"grand_total":rate,
		'reservation_type': reservation_type,
		'inpatient_record': inpatient_record
	}]
	patient_percentage=company_percentage=hospital_percentage=0
	
	if health_insurance:
		patient_percentage,company_percentage,hospital_percentage,doctor_percentage=get_medical_insurance_percent(medical_insurance_company
																								,"Medical Services",reservation_type)
	
	set_patient_due(patient,items,patient_percentage)
	if company_percentage:
		set_company_due(patient,medical_insurance,items,company_percentage)
	if hospital_percentage:

		set_contract_invoice(insurance_company=medical_insurance,
								percentage=hospital_percentage,items=items, inpatient_record=inpatient_record)
					
	# frappe.throw("After due")
		


def get_insurance_room(medical_insurance,reservation_type):
	room_type = frappe.db.sql(
	f"select room_type from `tabMedical Insurance Company Room Details` where parent='{medical_insurance}' and  reservation_type='{reservation_type}'",
	as_list=1)
	try:
		return room_type[0][0]
	except:
		# frappe.msgprint("Not found")
		return None
	
