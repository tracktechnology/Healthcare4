# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExternalLab(Document):

	@frappe.whitelist()
	def create_supplier(self):
		doc = frappe.new_doc("Supplier")
		doc.supplier_name = self.name
		doc.is_external_lab = 1
		doc.insert(ignore_permissions=True)
		doc.create_account()
		doc.save()
		# doc.submit()
		return doc.name

	def before_submit(self):
		self.supplier = self.create_supplier()
