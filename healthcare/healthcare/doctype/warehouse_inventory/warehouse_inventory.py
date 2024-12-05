# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import get_stock_balance
from healthcare.controllers.stock_utils import make_stock_entry_materail_consumption
# import operator


class WarehouseInventory(Document):

	def make_stock_entry(self):
		stoc_entry_name = make_stock_entry_materail_consumption(self.doctype,self.name,self.from_warehouse)
		frappe.db.set_value("Stock Entry", stoc_entry_name, "source_type", self.doctype)
		frappe.db.set_value("Stock Entry", stoc_entry_name, "source_name", self.name)
		self.db_set("stock_entry",stoc_entry_name)


	def before_save(self):
		self.set_items_consumed()

	def on_submit(self):
		self.make_stock_entry()

	def set_items_consumed(self):
		self.items = []
		items = self.get_items_difference()
		frappe.msgprint(str(items))
		for item in items:
			uom = frappe.db.get_value("Item",item["item_code"],"stock_uom")
			item["uom"] = uom
			item["stock_uom"] = uom
			self.append("items",item)

	def get_items_difference(self):
		res= []
		for item in self.items_inventory:
			if item.balance_qty > item.actual_qty:
				res.append({
					# 's_warehouse' : self.from_warehouse,
					"item_code" : item.item_code,
					"item_name" : item.item_name,
					"qty": item.balance_qty - item.actual_qty,
					# "basic_rate": item.valuation_rate,
					# "uom":"Unit"
				})
			elif item.actual_qty > item.balance_qty :
				res.append({
					# 't_warehouse' : self.warehouse,
					"item_code" : item.item_code,
					"item_name" : item.item_name,
					"qty": item.actual_qty - item.balance_qty,
					# "basic_rate": item.valuation_rate,
					# "uom":"Unit"
				})
		return res

	def on_cancel(self):
		if self.stock_entry:
			stock_entry_doc = frappe.get_doc("Stock Entry",self.stock_entry)
			stock_entry_doc.cancel()

	@frappe.whitelist()
	def load_items(self):
		self.items_inventory = []
		items = get_items(self.from_warehouse,self.posting_date,self.posting_time,"Track INT'l Trad (Demo)")
		for item in items:
			if item.get("balance_qty") > 0:
				self.append("items_inventory",item)



	@frappe.whitelist()
	def set_to_warehouse(self):
		if self.request_from:
			warehouse_name = ""
			if self.request_from == "Clinic":
				warehouse_name = "clinc_warehouse"
			elif self.request_from == "Labs":
				warehouse_name = "labs_warehouse"
			elif self.request_from == "Imaging":
				warehouse_name = "imaging_warehouse"
			warehouse = frappe.db.get_single_value("Stock Settings", warehouse_name)
			# frappe.msgprint(str(warehouse))
			self.from_warehouse = warehouse



@frappe.whitelist()
def get_items(warehouse, posting_date, posting_time,company):
	lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
	items = frappe.db.sql(f"""
		select i.name, i.item_name, bin.warehouse
		from tabBin bin, tabItem i
		where i.name=bin.item_code and i.disabled=0 and i.is_stock_item = 1
		and i.has_variants = 0 
		and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=bin.warehouse)
	""", (lft, rgt))

	items += frappe.db.sql(f"""
		select i.name, i.item_name, id.default_warehouse
		from tabItem i, `tabItem Default` id
		where i.name = id.parent
			and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=id.default_warehouse)
			and i.is_stock_item = 1 
			and i.has_variants = 0 
		group by i.name
	""", (lft, rgt))
	#and i.disabled = 0 and id.company=%s and i.has_serial_no = 0 and i.has_batch_no = 0

	res = []
	# frappe.msgprint(str(posting_date) + "::" + str(posting_time))
	for d in set(items):
		stock_bal = get_stock_balance(d[0], d[2], posting_date, posting_time,
			with_valuation_rate=True)
		# frappe.msgprint(str(stock_bal))
		item_creation = frappe.db.get_value("Item",d[0],"creation")
		if frappe.db.get_value("Item", d[0], "disabled") == 0:
			item_dic = {
				"item_code": d[0],
				"item_name": d[1],
				"valuation_rate": stock_bal[1],
				"balance_qty": stock_bal[0],
				"actual_qty": stock_bal[0],
				# "creation": item_creation
			}
			res.append(item_dic)
			# frappe.msgprint(str(item_dic))
			# frappe.msgprint("====================")
	# res.sort(key=operator.itemgetter('creation'))
	# frappe.msgprint(str(res))
	return res
