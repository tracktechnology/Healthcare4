# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.healthcare.doctype.patient_emergency.patient_emergency import set_patient_emergency
from healthcare.healthcare.doctype.room.room import set_patient_room
from erpnext.accounts.doctype.patient_due.patient_due import set_patient_due

from frappe.utils import now


class ReservationInpatient(Document):
	
	@frappe.whitelist()
	def set_patient_emergency(self):
		if self.available_capacity>0:
			status="Start"
		else:
			status="Waiting"
			
		set_patient_emergency(self.emergency_patient,status,self.medical_insurance_company)

	@frappe.whitelist()
	def update_patient_emergency(self,patient,patient_emergency_name,medical_insurance_company):
		if self.available_capacity>0:
			frappe.db.set_value("Patient Emergency",patient_emergency_name,{"status":"Start","datetime":now()})
			set_patient_room(patient=patient,room="Emergency",reservation_type="Emergency",medical_insurance_company=medical_insurance_company)	
		
		else:
			frappe.throw(str("لا يوجد أماكن متاحة في الغرفة"))

	