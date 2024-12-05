# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe.model.naming import make_autoname

class ObservationRequest(Document):

	def autoname(self):
		current_year = frappe.utils.now_datetime().year
		type=None
		if self.observation_category=="Imaging":
			type="IMG"
		if self.observation_category=="Laboratory":
			type="LAB"
		
		self.name=make_autoname(f"{type}-{current_year}-.####")



	@frappe.whitelist()
	def get_duplicate_observation(self,observation):
		if frappe.db.exists("Lab Test",{"patient":self.patient,"template":observation,"status":"Draft"}):
			return observation
		
	# def before_save():


	def before_insert(self):
		self.validate_dulicate()

	def validate_dulicate(self):
		# frappe.throw(str("in"))
		from frappe.utils import now,add_to_date
		time_threshold = add_to_date(now(), seconds=-10, as_string=True)
		records = frappe.get_all('Observation Request', 
								filters={'creation': ['>=', time_threshold],'patient':self.patient},
								fields=['*'])
		# frappe.throw(str(len(records)==0))
		if records:
			frappe.throw(str("please try again"))