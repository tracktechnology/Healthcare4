# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.healthcare.doctype.reservation.reservation import set_observation_request,print_receipt
from erpnext.controllers.myutils import copy_doc
from healthcare.healthcare.reservation_accounts import make_payment,print_receipt
from frappe.utils import now

class ReservationEmergency(Document):
	
	@frappe.whitelist()
	def get_patient_emergency(self):
		doc=frappe.get_list("Patient Emergency",{"patient":self.patient,"docstatus":1})
		self.emergency_fees_amount,self.total=frappe.db.get_value("Hospital Setting","Hospital Setting",['emergency_fees','emergency_doctor_fees'])
		self.grand_total=self.total
		self.emergency_fees=0
		if doc:
			self.emergency_fees=1

		

	# @frappe.whitelist()
	# def get_observation_request(self,patient_name,observation_category,mutlti_selecte_field,medical_dep_field,doctor_field,total_field,grand_total_field,is_emergency=False,observation_status=None):
	# 	setattr(self, mutlti_selecte_field, []) 
	# 	request=get_observation_request(patient_name,observation_category,is_emergency=True)
	# 	# obsrevations,total=get_observation_request(requests)
	# 	setattr(self, observation_status, "Open Service")
		
	# 	if request:
	# 		# frappe.throw(str(request))
	# 		for i in request['observation']:
	# 			self.append(mutlti_selecte_field,{
	# 			"observation":i
	# 		})
	# 		# setattr(self, mutlti_selecte_field, request['observation']) 
	# 		# setattr(self, medical_dep_field, doc.medical_department) 
	# 		setattr(self, doctor_field, request['doctor']) 
	# 		setattr(self, total_field,request['total']) 
	# 		setattr(self, grand_total_field, request['grand_total'])
	# 		if request['total']!=request['grand_total']: 
	# 			setattr(self, observation_status, "Complete Payment")
	# 		else:
	# 			setattr(self, observation_status, "Payment")
	# 		return self
	# 	frappe.msgprint(str(getattr(self,observation_status)))
		

	# @frappe.whitelist()
	# def set_lab_reservation(self):
	# 	doc = frappe.new_doc("Reservation")
	# 	doc.laboratory_patient=self.laboratory_patient
	# 	doc.set_lab_reservation(is_emergency=True)
		
	@frappe.whitelist()
	def set_request_emergency_doctor(self,paper_receipt,paid_amount):
		doc = frappe.new_doc("Patient Encounter")
		doc.patient = self.patient
		doc.practitioner = self.doctor
		doc.medical_department = self.medical_department
		doc.reservation_type = "Emergency Doctor"
		doc.is_emergency=1
		doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
		doc.submit()


		items=make_payment(patient=self.patient, insurance_company=self.insurance_company_doctor,
				percentage=float(self.percentage_doctor),company_percentage=float(self.company_percentage_doctor), 
				is_healthcare_insurance=int(self.health_insurance_doctor), patient_encounter= doc.name,
				paper_receipt=paper_receipt,paid_amount=paid_amount,doctor=self.doctor,items=[{"service":"طلب أستشاري","paid_amount":paid_amount}])

		doc.db_set('invoiced', 1)
		return print_receipt(items, doctor_name=self.doctor, patient_name=self.patient, service_type="طوارئ",
						 medical_dep=self.medical_department, company_insurance=self.medical_insurance,
						 insurane_percentage=self.percentage_doctor)


	# @frappe.whitelist()
	# def set_emergency_fees(self,insurance_company=None,percentage=None,company_percentage=None,health_insurance=None,paper_receipt=None,paid_amount=0,patient=None):
	# 	set_patient_emergency(patient)
	# 	items=make_payment(patient=patient, insurance_company=insurance_company,
	# 			percentage=percentage,company_percentage=company_percentage, 
	# 			is_healthcare_insurance=health_insurance,
	# 			paper_receipt=paper_receipt,paid_amount=paid_amount,items=[{"service":"كشف طوارئ"}])


	# 		# return print_receipt(items,self.lab_doctor ,self.patient, "كشف طوارئ",self.lab_department
	# 		# 						, self.insurance_company_lab,self.percentage_lab)


	@frappe.whitelist()
	def set_lab_reservation(self,is_emergency=True,paper_receipt=None,paid_amount=0):
		item_print=[]

		if not self.laboratory_patient:
			frappe.throw(str("Please enter Patient Name"))
		if not self.laboratory:
			set_observation_request(self.laboratory_patient,"Laboratory",self.lab_department,self.lab_doctor,is_emergency=is_emergency)
		# else:
		# 	request=get_observation_request(self.laboratory_patient,"Laboratory",is_emergency=is_emergency)
			# for i in requests:
		# 	if request:
		# 		if not request['patient_encounter']:
		# 			request['patient_encounter'] = set_observation_patient_encounter(self.laboratory_patient, request['doctor'],
		# 																request['medical_department'], request['observation'], "Laboratory")
				

		# 		items=make_payment(patient=self.laboratory_patient, insurance_company=self.insurance_company_lab,
		# 			    percentage=self.percentage_lab,company_percentage=self.company_percentage_lab, 
		# 				is_healthcare_insurance=self.health_insurance_lab, patient_encounter=request['patient_encounter'],
		# 				paper_receipt=paper_receipt,doctor=self.lab_doctor,paid_amount=paid_amount,items=self.laboratory)

		# 		update_observation_request(request['name'],paid_amount,request['patient_encounter'])
		# 	return print_receipt(items,self.lab_doctor ,self.laboratory_patient, "تحاليل",self.lab_department
		# 						, self.insurance_company_lab,self.percentage_lab)
		# return True


	@frappe.whitelist()
	def set_imaging_reservation(self,is_emergency=True,paper_receipt=None,paid_amount=0):
		item_print=[]

		if not self.imaging_patient:
			frappe.throw(str("Please enter Patient Name"))
		if not self.imaging:
			set_observation_request(self.imaging_patient,"Imaging",self.imaging_department,self.imaging_doctor,is_emergency=is_emergency)
		# else:
		# 	request=get_observation_request(self.imaging_patient,"Imaging",is_emergency=is_emergency)
		# 	if request:
		# 		if not request['patient_encounter']:
		# 			request['patient_encounter'] = set_observation_patient_encounter(self.imaging_patient, request['doctor'],
		# 															request['medical_department'], request['observation'], "Imaging")
		# 		items=make_payment(patient=self.imaging_patient, insurance_company=self.insurance_company_imaging,
		# 			    percentage=self.percentage_imaging,company_percentage=self.company_percentage_imaging, 
		# 				is_healthcare_insurance=self.health_insurance_imaging, patient_encounter=request['patient_encounter'],
		# 				paper_receipt=paper_receipt,doctor=self.imaging_doctor,paid_amount=paid_amount,items=self.imaging)

		# 		item_print.append(items)
	
		# 		update_observation_request(request['name'],paid_amount,request['patient_encounter'])

		# 	return print_receipt(item_print,self.imaging_doctor ,self.imaging_patient, "أشعة",self.imaging_department
		# 						, self.insurance_company_imaging,self.percentage_imaging)
		# return True



