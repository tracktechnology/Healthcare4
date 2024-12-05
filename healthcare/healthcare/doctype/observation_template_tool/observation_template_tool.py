# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.healthcare.healthcare_utils import update_item_rate

class ObservationTemplateTool(Document):
	@frappe.whitelist()
	def set_observation(self):
		self.set_observation_template()
		self.set_lab_test_template()
	
	@frappe.whitelist()
	def update_observation(self):
		doc = frappe.get_doc("Observation Template",self.edit_observation)
		doc.rate = self.edit_rate
		# doc.change_in_item=1
		doc.save(ignore_permissions=True)

		lab_test_doc=frappe.get_doc("Lab Test Template",self.edit_observation)
		lab_test_doc.lab_test_rate=self.edit_rate
		lab_test_doc.normal_test_templates=self.edit_normal_test_templates
		doc.normal_test_templates=[]
		for i in self.edit_normal_test_templates:
			doc.append('normal_test_templates', i)
		lab_test_doc.custom_result=self.edit_custom_result
		lab_test_doc.save(ignore_permissions=True)

		update_item_rate(self.edit_observation,self.edit_rate)
	@frappe.whitelist()
	def update_bulk_observation(self):
		for i in self.bulk_edit_observation:
			doc = frappe.get_doc("Observation Template",i.observation)
			doc.rate = self.bulk_edit_rate

			doc.flags.ignore_mandatory = True

			doc.save(ignore_permissions=True)

			lab_test_doc=frappe.get_doc("Lab Test Template",i.observation)
			lab_test_doc.lab_test_rate=self.bulk_edit_rate
			lab_test_doc.flags.ignore_mandatory = True

			lab_test_doc.save(ignore_permissions=True)
			update_item_rate(i.observation,self.bulk_edit_rate)


	@frappe.whitelist()
	def get_observation_details(self):
		self.edit_rate=frappe.db.get_value("Item Price",{"item_code":self.edit_observation,"price_list": "Standard Selling"},'price_list_rate')
		doc=frappe.get_doc("Lab Test Template",self.edit_observation)
		self.edit_normal_test_templates=doc.normal_test_templates
		# self.edit_normal_test_templates=frappe.db.get_value("Lab Test Template",self.edit_observation,'normal_test_templates')
		self.edit_custom_result=doc.custom_result



	def set_observation_template(self):
		doc=frappe.new_doc("Observation Template")
		doc.observation_category="Laboratory"
		doc.observation=self.observation
		doc.is_billable=1
		doc.rate=self.rate
		# doc.item=self.set_observation
		doc.item_code=self.observation
		doc.item_group=self.item_group
		doc.abbr=self.observation
		doc.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)

	def set_lab_test_template(self):
		doc= frappe.new_doc("Lab Test Template")
		doc.lab_test_group=self.item_group
		doc.lab_test_code=self.observation
		doc.lab_test_name=self.observation
		doc.lab_test_template_type="Compound"
		doc.item=self.observation
		doc.lab_test_rate=self.rate
		doc.normal_test_templates=self.normal_test_templates
		for i in self.normal_test_templates:
			doc.append('normal_test_templates', i)
		doc.custom_result=self.custom_result
		doc.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)





