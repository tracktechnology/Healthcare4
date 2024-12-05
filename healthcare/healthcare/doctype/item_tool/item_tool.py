# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class ItemTool(Document):
	@frappe.whitelist()
	def get_item_price_list(self):
		self.edit_price_list=[]	
		items=frappe.get_all('Item Price', filters={"item_code": self.edit_item},
				  fields=['price_list_rate','price_list'])
		for i in items:
			self.append("edit_price_list",{
				"price_list":i.price_list,
				"rate":i.price_list_rate,
			})
	@frappe.whitelist()
	def update_item_price_list(self):
		frappe.db.sql(f"DELETE FROM `tabItem Price` WHERE item_code='{self.edit_item}'")
		frappe.db.commit()
		for i in self.edit_price_list:
			make_item_price(self.edit_item,i.rate,i.price_list)
	@frappe.whitelist()
	def update_practitioner(self):
		doc=frappe.get_doc("Healthcare Practitioner",self.practitioner)
		doc.practitioner_name=self.practitioner_name
		doc.mobile_phone=self.practitioner_mobile
		doc.healthcare_practitioner_type=self.edit_practitioner_type
		doc.department=self.edit_practitioner_department
		# doc.practitioner_schedules=self.practitioner_schedules
		doc.out_patient_booking_charge=self.edit_booking_charge
		doc.op_consulting_charge=self.edit_consulting_charge
		doc.save(ignore_permissions=True)

	@frappe.whitelist()
	def set_item(self):
		if self.department=="Laboratory":
			self.set_observation_template()
			self.set_lab_test_template()
		elif self.department=="Imaging":
			self.set_observation_template()
		elif self.department=="Clinical Procedure": 
			self.set_clinical_procedure()
	@frappe.whitelist()
	def set_practitioner(self):
		self.set_healthcare_practitioner()




	def set_observation_template(self):
		doc=frappe.new_doc("Observation Template")
		doc.observation_category=self.department
		doc.observation=self.item
		# doc.is_billable=0
		# doc.rate=self.rate
		doc.item_code=self.item
		doc.item_group=self.item_group
		doc.abbr=self.item
		doc.price_list=self.price_list
		doc.medical_department=self.medical_department
		doc.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)
		self.create_item_from_template(doc)
		
	def set_lab_test_template(self):
		doc= frappe.new_doc("Lab Test Template")
		doc.lab_test_group=self.item_group
		doc.lab_test_code=self.item
		doc.lab_test_name=self.item
		doc.lab_test_template_type="Compound"
		doc.item=self.item
		doc.lab_test_rate=self.rate
		doc.normal_test_templates=self.normal_test_templates
		# for i in self.normal_test_templates:
		# 	doc.append('normal_test_templates', i)
		doc.custom_result=self.custom_result
		doc.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)


	def set_clinical_procedure(self):
		doc=frappe.new_doc("Clinical Procedure Template")
		doc.template=self.item
		doc.medical_department=self.medical_department
		doc.reuse_by_count=self.reuse_by_count
		# doc.is_billable=1
		# doc.rate=self.rate
		doc.item_code=self.item
		doc.item=self.item
		doc.item_group=self.item_group
		doc.consume_stock=self.consume_stock
		doc.items=self.items
		doc.price_list=self.price_list
		doc.healthcare_practitioner_type=self.healthcare_practitioner_type
		doc.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)
		self.create_item_from_template(doc)

	def set_healthcare_practitioner(self):
		doc=frappe.new_doc("Healthcare Practitioner")
		full_name=(self.full_name).split(" ")
		doc.first_name=full_name[0]
		doc.last_name=" ".join(full_name[1:])
		doc.practitioner_name=self.full_name
		doc.gender=self.gender
		doc.mobile_phone=self.mobile_phone
		doc.healthcare_practitioner_type=self.practitioner_type
		doc.department=self.practitioner_department
		doc.practitioner_schedules=self.practitioner_schedules
		doc.out_patient_booking_charge=self.out_patient_booking_charge
		doc.op_consulting_charge=self.op_consulting_charge
		doc.op_consulting_charge_item="كشف"
		doc.save(ignore_permissions=True)


	def create_item_from_template(self,doc):
		create_item(doc)
		for i in self.price_list:
			make_item_price(doc.item_code,i.rate,i.price_list)


def create_item(doc):
	disabled = doc.disabled
	if doc.is_billable and not doc.disabled:
		disabled = 0

	uom = frappe.db.exists("UOM", "Unit") or frappe.db.get_single_value("Stock Settings", "stock_uom")
	item = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": doc.item_code,
			"item_name": doc.template,
			"item_group": doc.item_group,
			"description": doc.description,
			"is_sales_item": 1,
			"is_service_item": 1,
			"is_purchase_item": 0,
			"is_stock_item": 0,
			"show_in_website": 0,
			"is_pro_applicable": 0,
			"disabled": disabled,
			"stock_uom": uom,
		}
	).insert(ignore_permissions=True, ignore_mandatory=True)

	doc.db_set("item", item.name)



def make_item_price(item, item_price,price_list=None):
	price_list_name = frappe.db.get_value(
		"Selling Settings", None, "selling_price_list"
	) or frappe.db.get_value("Price List", {"selling": 1})
	frappe.get_doc(
		{
			"doctype": "Item Price",
			"price_list": price_list or  price_list_name,
			"item_code": item,
			"price_list_rate": item_price,
			"valid_from": today(),
		}
	).insert(ignore_permissions=True, ignore_mandatory=True)



