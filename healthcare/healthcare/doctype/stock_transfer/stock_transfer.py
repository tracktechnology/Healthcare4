# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.controllers.stock_utils import make_stock_entry


class StockTransfer(Document):


	def on_submit(self):
		self.make_stock_request_entry()

	def make_stock_request_entry(self):
		stoc_entry_name = make_stock_entry(self.doctype,self.name, "Material Transfer"
										   , from_warehouse=self.from_warehouse, to_warehouse=self.to_warehouse
										   ,company="Track INT'l Trad (Demo)"
										   ,posting_date=self.posting_date,posting_time=self.posting_time
										   ,allow_draft=False)
		frappe.db.set_value("Stock Entry",stoc_entry_name,"source_name",self.name)
		frappe.db.set_value("Stock Entry",stoc_entry_name,"source_type",self.doctype)
		self.db_set("stock_entry",stoc_entry_name)

	def on_cancel(self):
		if self.stock_entry:
			stock_entry_doc = frappe.get_doc("Stock Entry",self.stock_entry)
			stock_entry_doc.cancel()