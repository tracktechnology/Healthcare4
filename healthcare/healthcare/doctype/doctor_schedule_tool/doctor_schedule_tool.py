# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DoctorScheduleTool(Document):
	
	@frappe.whitelist()
	def get_practitioner_details(self):
		self.time_slots=[]
		data=frappe.db.sql(f"select parent,from_time,to_time,maximum_appointments,maximum_consultation,for_once,disabled from `tabHealthcare Schedule Time Slot` WHERE parenttype='Practitioner Schedule' and day ='{self.day}' ",as_dict=1)
		for i in data:
			self.append('time_slots', {
				'doctor': i.parent,
				'disabled': i.disabled,
				'for_once': i.for_once,
				'maximum_consultation': i.maximum_consultation,
				'maximum_appointments': i.maximum_appointments,
				'to_time': i.to_time,
				'from_time':   i.from_time,
			})			
	@frappe.whitelist()
	def set_practitioner_details(self):
		frappe.db.sql(f"Delete from `tabHealthcare Schedule Time Slot` where day='{self.day}'")
		for  i in self.time_slots:
			practitioner_schedule=frappe.db.exists('Practitioner Schedule',i.doctor)
			if practitioner_schedule:
				doc = frappe.get_doc("Practitioner Schedule", practitioner_schedule)
				doc.append("time_slots", {
					'disabled': i.disabled,
					'for_once': i.for_once,
					'maximum_consultation': i.maximum_consultation,
					'maximum_appointments': i.maximum_appointments,
					'to_time': i.to_time,
					'from_time':   i.from_time,
					'day':self.day
				})
				doc.save()

			else:
				doc = frappe.new_doc("Practitioner Schedule")
				doc.schedule_name=i.doctor
				doc.append("time_slots", {
									'disabled': i.disabled,
									'for_once': i.for_once,
									'maximum_consultation': i.maximum_consultation,
									'maximum_appointments': i.maximum_appointments,
									'to_time': i.to_time,
									'from_time':   i.from_time,
									'day':self.day

								})
				doc.save()

				practitioner=frappe.get_doc("Healthcare Practitioner",i.doctor)
				practitioner.append("practitioner_schedules",{
					"schedule":i.doctor,
				})
				practitioner.save()

		