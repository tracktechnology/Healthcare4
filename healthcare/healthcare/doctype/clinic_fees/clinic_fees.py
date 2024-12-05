# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClinicFees(Document):
	
	@frappe.whitelist()
	def get_all_doctors(self):
		doctors = frappe.db.sql("""
				SELECT name 
				FROM `tabHealthcare Practitioner`
				WHERE name NOT IN (
					SELECT healthcare_practitioner
					FROM `tabClinic Fees Details`
				)
			""", as_dict=True)
							
		# self.a/ppend('doctors ', {doctors})
		for i in doctors:
			self.append('doctors',{
				"healthcare_practitioner":i.name
			})
		self.save()
@frappe.whitelist()
def get_clinic_fees(doctor,total,is_consulting=0):
	total=float(total)
	is_consulting=int(is_consulting)
	amount_field="booking_amount"
	percent_field="booking_percent"
	if  is_consulting:
		amount_field="consulting_amount"
		percent_field="consulting_percent"
	try:
		amount,percent=frappe.db.sql(f"SELECT {amount_field},{percent_field} from`tabClinic Fees Details`where healthcare_practitioner='{doctor}' ",as_list=True)[0]
		
		if percent>0:
			hospitals_percent=100-percent
			return hospitals_percent*total/100
		
		return  total-amount
	except Exception:
		frappe.msgprint(str("Not fount doctor in Clinic Fees "))

	