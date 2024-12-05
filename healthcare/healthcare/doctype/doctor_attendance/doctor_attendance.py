# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DoctorAttendance(Document):
	# def validate(self):
	# 	self.replace_doctor()
	@frappe.whitelist()
	def replace_doctor(self,slot_name,from_time,to_time,replacement_doctor=None):
		frappe.db.sql(f"UPDATE   `tabHealthcare Schedule Time Slot` SET disabled=1  where name='{slot_name}'")
		if replacement_doctor:
			self.append('doctor_attendance_details', {
									'healthcare_practitioner': replacement_doctor,
									'from_time': from_time,
									'to_time': to_time,
								})
			
			doctor=frappe.get_doc("Healthcare Practitioner",replacement_doctor)
			doctor=doctor.as_dict()
			schedule=doctor['practitioner_schedules'][0]['schedule']
			doc=frappe.get_doc("Practitioner Schedule",schedule)
			doc.append('time_slots', {
											'healthcare_practitioner': replacement_doctor,
											'from_time': from_time,
											'to_time': to_time,
											"for_once":1,
										})

			doc.save()
	@frappe.whitelist()
	def get_slots(self):
		slots=frappe.db.sql(f"select hs.name,from_time,to_time,ps.parent  from `tabPractitioner Service Unit Schedule` ps , `tabHealthcare Schedule Time Slot` hs  where  ps.schedule=hs.parent and hs.day='{self.day}' ",as_dict=1)
		for i in slots:
			self.append('doctor_attendance_details', {
							'healthcare_practitioner': i.parent,
							'from_time': i.from_time,
							'to_time': i.to_time,
							'slot_name': i.name,
						})



