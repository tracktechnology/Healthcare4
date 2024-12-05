# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.healthcare.healthcare_utils import get_practitioner_full_name
from healthcare.healthcare.reservation_accounts import set_return_doctor_entry

class ReservationInquiry(Document):



	@frappe.whitelist()
	def get_reservation_details(self):
		practitioner_query=True
		patient_query=True
		if self.reservation_doctor:
			practitioner_query=f"pe.practitioner='{self.reservation_doctor}'"
		if self.reservation_patient:
			patient_query=f"pe.patient='{self.reservation_patient}'" 
		data = frappe.db.sql(f"""
			select si.name,si.patient_encounter,pe.patient,si.grand_total,pe.encounter_date,pe.practitioner from
			`tabSales Invoice`si,`tabPatient Encounter`pe
			where pe.name=si.patient_encounter and reservation_type='{self.reservation_type}' and
			{patient_query} and {practitioner_query} and pe.encounter_date>='{self.from_date}' and 
			pe.encounter_date<='{self.to_date}' and si.status!='Cancelled' and reference_dt is  NULL and
		si.cancel_request=0""",as_dict=1)

		self.reservation_deatils=[]
		self.reservation_deatils=None
		for i in data:
			self.append('reservation_deatils', {
				'patient_encounter': i.patient_encounter,
				'patient_name':i.patient,
				'sales_invoice':i.name,
				'fees':i.grand_total,
				"date":i.encounter_date,
				"doctor":get_practitioner_full_name(i.practitioner),
				
			})


		

	@frappe.whitelist()
	def cancel_reservation(self,items):
		for i in items:
			invoice=frappe.get_doc("Sales Invoice",i['sales_invoice'])
			invoice.db_set('cancel_request',1) # update field in  doc
			if not invoice.patient: #if inurance invoice 100% 
				if frappe.db.exists("Doctor Entry",{"patient_encounter":i['patient_encounter'],"has_return":0,"is_return":0}):
					doc = frappe.get_doc("Doctor Entry",{"patient_encounter":i['patient_encounter']})
					set_return_doctor_entry(doc)
					invoice.cancel()
		
			last_payment = frappe.get_all('Payment Entry',filters={"patient_encounter":i['patient_encounter']}, fields=['name'], order_by='creation desc', limit=1)
			if last_payment:
				frappe.db.set_value("Payment Entry",last_payment[0].name,"cancel_request",1)
				

			# frappe.db.set_value("Sales Invoice",i['sales_invoice'],"cancel_request",1)
			if invoice.paid==0:
				doc=frappe.get_doc("Patient Encounter",i['patient_encounter'])
				doc.cancel()
				# if insurance percent with patient is cost invoice
				if frappe.db.exists("Sales Invoice",{"reference_dt":invoice.name}):
					insurance_invoice=frappe.get_doc("Sales Invoice",{"reference_dt":invoice.name})
					insurance_invoice.cancel()

				if frappe.db.exists('Contract Invoice',{"patient_encounter":invoice.patient_encounter}):
					contract_invoice=frappe.get_doc("Contract Invoice",{"patient_encounter":invoice.patient_encounter})
					contract_invoice.cancel()					






@frappe.whitelist()
def replace_doctor(rows,replace_doctor):
	rows = list(eval(rows))
	if  not rows:
		frappe.throw(str("Please select patients"))
	for i in rows:
		doc=frappe.get_doc("Patient Encounter",i['patient_encounter'])
		doc.db_set('practitioner',replace_doctor)
	frappe.msgprint("Successfully replaced ")
