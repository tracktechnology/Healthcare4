# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now
from frappe.model.document import Document
from frappe.utils import add_to_date, today, date_diff,time_diff_in_hours,now
import math

class Room(Document):
	
	def validate(self):
		# if self.is_busy:
		# 		frappe.throw(str("The room is full capacity"))
		self.check_duplicate_inpatient()
		self.check_room_busy()
		
	


	def check_duplicate_inpatient(self):
		
		for i in self.room_details:
			rooms=frappe.db.sql(f"SELECT parent from `tabRoom Details` WHERE parenttype='Room' and patient='{i.patient}' ",as_list=1)
			if len(rooms)>1:
				frappe.msgprint(str(f"The patient is already in a room => {rooms[0][0]}"))
		
	def check_room_busy(self):
		if  not self.capacity >= len(self.room_details):
				frappe.throw(str("The room is full capacity"))
		if self.capacity == len(self.room_details):
			self.is_busy = True
		else:
			self.is_busy = False
		

			
		

	
def get_room_details(room):
	room = frappe.get_doc("Room",room)
	return room



# def check_room_capacity(room):
# 	room_doc=get_room_details(room)
# 	if room_doc.capacity > len(room_doc.room_details):
# 		return room_doc
# 	return False

@frappe.whitelist()
def set_patient_room(patient,room,reservation_type,medical_insurance_company=None):
	try:
		inpatient_record=set_inpatient_record(patient,reservation_type,medical_insurance_company,room)
		room_doc=frappe.get_doc("Room",room)
		room_doc.append('room_details', {	
				'patient': patient,
				'from_date':now(),
				'inpatient_record':inpatient_record
			})
		room_doc.save(ignore_permissions=True)

		return True
	except:
		return  False
	



def calculate_booking_room(room=None,check_in=None,room_type=None):
	if not room_type:
		room=frappe.get_doc("Room",room)
		room_type=room.room_type

	doc=frappe.get_doc("Room Type",room_type)
	diff=1
	if doc.period=="Hour":
		diff=time_diff_in_hours(now(),check_in)
	
	if  doc.allow_fraction:
		diff=math.ceil(diff)
	return [diff,doc.rate,doc.name]
	return round(diff*doc.rate,2)

def delete_room_patient(patient,room):
	frappe.db.sql(f"DELETE from`tabRoom Details` where parent='{room}' and patient='{patient}'",as_dict=1)


def set_inpatient_record(patient,reservation_type,medical_insurance_company,room):
	doc=frappe.new_doc("Inpatient Record")
	doc.patient=patient
	doc.reservation_type = reservation_type
	doc.medical_insurance_company=medical_insurance_company
	if medical_insurance_company :
		doc.medical_insurance=frappe.db.get_value("Medical insurance company",medical_insurance_company,'company_name')
	doc.append('room', {
				'room': room,
				'check_in':now(),
			})
			
	doc.status ="Admitted"
	doc.insert(ignore_permissions=True)
	return doc.name