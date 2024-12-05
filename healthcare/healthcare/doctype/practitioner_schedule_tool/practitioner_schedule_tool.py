# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PractitionerScheduleTool(Document):
	
	@frappe.whitelist()
	def get_practitioner_details(self):
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
		doc = frappe.get_doc("Practitioner Schedule",self.practitioner_schedule)
		doc.time_slots = self.time_slots
		doc.save()