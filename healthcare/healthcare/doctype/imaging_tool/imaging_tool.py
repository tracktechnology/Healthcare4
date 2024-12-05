# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.healthcare.doctype.reservation.reservation import set_observation_patient_encounter
from healthcare.healthcare.reservation_accounts import make_payment,print_receipt	
import itertools
from healthcare.healthcare.reservation_accounts import make_payment,print_receipt,set_insurance_company_sales_invoice,set_contract_invoice
from erpnext.accounts.doctype.patient_due.patient_due import set_patient_due
from erpnext.accounts.doctype.company_due.company_due import set_company_due

from healthcare.healthcare.doctype.nursing_tool.nursing_tool import set_patient_record_items

class ImagingTool(Document):
	@frappe.whitelist()
	def set_observation_request(self):
		# frappe.throw(str(self.observation_request))
		doc = frappe.get_doc("Observation Request",self.observation_request)
		doc.observation=self.observation
		doc.status="Unpaid"
		doc.total=self.total
		# doc.patient_encounter=self.set_observation_invoice(doc)
		if self.amount_due==0:
			doc.status="Paid"

		if self.reservation_type=="Outpatient":
			doc.patient_encounter=self.set_observation_invoice(doc)


		elif self.reservation_type=="Emergency":
			self.set_emergency_observation()
			doc.status="Paid"
		doc.save()


	def set_emergency_observation(self):
		items=[]
		doc=frappe.get_doc("Inpatient Record",{"patient":self.patient})

		for i in self.observation_details:
			items.append({
				"item_name": i.get("observation"),
				"service": i.get("observation"),
				"qty": 1,
				"rate": i.get("price"),
				'reservation_type':self.reservation_type,
				"inpatient_record":doc.name

			})
		set_patient_record_items(doc,items,"lab_test_prescription","observation_template")
		set_patient_due(self.patient,items,self.patient_percentage)

		if self.company_percentage:
			# set_insurance_company_sales_invoice(
			# 			insurance_company=self.medical_insurance,
			# 		percentage=self.company_percentage, inpatient_record=doc.name,
					# items=self.observation)
			set_company_due(self.patient,self.medical_insurance,items,self.company_percentage)

		if self.hospital_percentage:
			set_contract_invoice(insurance_company=self.medical_insurance,
						percentage=self.hospital_percentage,items=self.observation, inpatient_record=doc.name)




	def set_observation_invoice(self,request):
		item_print=[]
		# for i in requests:
		observation=[]
		for i in request.observation:
			observation.append(i.observation)
		
		patient_encounter= set_observation_patient_encounter(self.patient, request.doctor,
												request.medical_department,observation, "Imaging",self.encounter_id,request.observation_date)

		is_healthcare_insurance=0
		if self.company_percentage:
			is_healthcare_insurance=1

		items=make_payment(patient=self.patient, insurance_company=self.medical_insurance,
			percentage=float(self.patient_percentage),company_percentage=float(self.company_percentage), 
			is_healthcare_insurance=is_healthcare_insurance, patient_encounter= patient_encounter,
			doctor=request.doctor,items=self.observation,hospital_percentage=self.hospital_percentage,posting_date=request.observation_date)

		# items=make_payment(patient=self.patient,  
		# 		patient_encounter=patient_encounter,
		# 		doctor=request.doctor,items=self.observation,total=self.amount_due,percentage=self.patient_percentage)
		return patient_encounter

	@frappe.whitelist()
	def get_observation_request(self):

		
		q = f"select imaging_type from `tabImaging Type Details` where parenttype='User' and parent='{frappe.session.user}'"
		main_query = f"select name, patient, creation,reservation_type,imaging_type from `tabObservation Request` where status='Pending' and imaging_type in ({q}) and docstatus=1 and observation_category='Imaging' ORDER BY  CASE  WHEN reservation_type = 'Emergency' THEN 1  ELSE 2 END, creation ASC"
		requests = frappe.db.sql(main_query, as_dict=True)
		
		self.requests=[]
		for i in requests:
		# self.request=requests
			
			self.append("requests",{
				"patient":i.patient,
				"observation_request":i.name,
				"reservation_type":i.reservation_type,
				"imaging_type":i.imaging_type,
			})


	@frappe.whitelist()
	def cancel_observation_request(self,observation_request):
		doc = frappe.get_doc("Observation Request",observation_request)
		doc.cancel()		

