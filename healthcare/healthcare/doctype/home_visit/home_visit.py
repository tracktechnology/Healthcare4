# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Homevisit(Document):

	@frappe.whitelist()
	def get_total(self):
		total=0
		for i in self.items:
			qty=0
			if i.used_qty!=None:
				qty=float(i.used_qty)
			else:
				qty=i.qty
			price=frappe.db.get_value("Item Price", {"item_code": i.item, "price_list": "Standard Selling"}, ['price_list_rate'])*qty
			if price:
				total+=price
		return total


	@frappe.whitelist()
	def get_visit_fees(self):
		return frappe.db.get_single_value("Hospital Setting","home_visit_price")
