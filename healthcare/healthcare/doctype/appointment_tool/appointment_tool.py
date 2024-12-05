# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AppointmentTool(Document):
	@frappe.whitelist()
	def get_appointment_details(self,doctor=False,department=False):
		self.appointment_details=None
		if doctor :
			slots=get_slot(self.doctor)
			for i in slots:
				self.append_to_appointment_details(get_doctor_title(i.parent),i.from_time,i.to_time,i.day)

				
		if department:

			doctors=frappe.get_all('Healthcare Practitioner', filters={"department": self.medical_department})
			for i in doctors:
			
				slots=get_slot(i.name)
				for j in slots:
					self.append_to_appointment_details(get_doctor_title(j.parent),j.from_time,j.to_time,j.day)
		if not self.appointment_details :
			frappe.msgprint("Not Found Appointment")
					
					

	def append_to_appointment_details(self,doctor,from_time,to_time,day):
			self.append('appointment_details', {
									'doctor': doctor,
									'from_time': from_time,
									'to_time': to_time,
									'day': day,
								})



def get_slot(doctor):
	slots=frappe.db.sql(f"select hs.day,from_time,to_time,ps.parent  from `tabPractitioner Service Unit Schedule` ps , `tabHealthcare Schedule Time Slot` hs  where ps.parent ='{doctor}' and ps.schedule=hs.parent and hs.disabled =0  ",as_dict=1)
	return slots


def get_doctor_title(healthcare_practitioner):
	return frappe.db.get_value("Healthcare Practitioner",healthcare_practitioner,'practitioner_name')
