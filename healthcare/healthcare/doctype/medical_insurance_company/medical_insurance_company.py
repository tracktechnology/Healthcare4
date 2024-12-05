# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Medicalinsurancecompany(Document):

	def validate(self):
		self.validate_sum_percentage()


	def validate_sum_percentage(self):
		for i in self.department_percentage:
			if i.patient_percentage+i.hospital_percentage+i.company_percentage!=100 or i.doctor_percentage>100:
				frappe.throw(str("Invalid Data"))
			