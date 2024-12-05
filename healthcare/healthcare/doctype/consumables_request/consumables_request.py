# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.controllers.stock_utils import make_stock_entry


class ConsumablesRequest(Document):

	@frappe.whitelist()
	def set_to_warehouse(self):
		if self.request_from:
			warehouse_name = ""
			if self.request_from == "Clinic": warehouse_name = "clinc_warehouse"
			elif self.request_from == "Labs": warehouse_name = "labs_warehouse"
			elif self.request_from == "Imaging": warehouse_name = "imaging_warehouse"
			warehouse = frappe.db.get_single_value("Stock Settings", warehouse_name)
			# frappe.msgprint(str(warehouse))
			self.to_warehouse = warehouse

	def on_submit(self):
		self.make_stock_request_entry()
		update_stock_after_submit()

	def make_stock_request_entry(self):
		stoc_entry_name = make_stock_entry(self.doctype,self.name, "Material Transfer"
										   , from_warehouse=self.from_warehouse, to_warehouse=self.to_warehouse
										   ,company="Track INT'l Trad (Demo)"
										   ,posting_date=self.posting_date,posting_time=self.posting_time
										   ,allow_draft=False)
		frappe.db.set_value("Stock Entry", stoc_entry_name, "source_name", self.name)
		frappe.db.set_value("Stock Entry", stoc_entry_name, "source_type", self.doctype)
		self.db_set("stock_entry",stoc_entry_name)

	def on_cancel(self):
		if self.stock_entry:
			stock_entry_doc = frappe.get_doc("Stock Entry",self.stock_entry)
			stock_entry_doc.cancel()
def update_stock_after_submit():
	stock_entries = get_draft_stock_entries()
	for stock_entry_name in stock_entries:
		stock_entry = frappe.get_doc("Stock Entry",stock_entry_name[0])
		if stock_entry.check_balance_before_submit():
			stock_entry.submit()
		else:
			pass

def get_draft_stock_entries():
	res = frappe.db.sql(""" select name from `tabStock Entry` where docstatus =0 and 
	patient_encounter is not null and patient_encounter != "" """, as_list=1)
	return res