# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.utils import now
import frappe
from frappe.model.document import Document
from healthcare.healthcare.doctype.room.room import set_patient_room

class PatientEmergency(Document):
	pass

@frappe.whitelist()
def set_patient_emergency(patient,status,medical_insurance_company):
	set_patient_room(patient=patient,room="Emergency",reservation_type="Emergency",medical_insurance_company=medical_insurance_company)	
	doc=frappe.new_doc("Patient Emergency")
	doc.status=status	
	doc.patient=patient
	doc.medical_insurance_company=medical_insurance_company
	doc.datetime=now()
	doc.submit()


@frappe.whitelist()
def get_wating_patient_emergency():
	wating_list=frappe.get_all('Patient Emergency', filters={"status":'Waiting' }, fields=['name','patient','datetime','medical_insurance'],order_by='creation asc')
	room_doc=frappe.get_doc("Room","Emergency")
	available_capacity=room_doc.capacity-len(room_doc.room_details)
	return [wating_list,available_capacity]
