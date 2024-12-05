# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.healthcare.healthcare_utils import update_item_rate,create_new_item


class RoomType(Document):
	def before_save(self):
		if frappe.db.exists('Item',self.item):
			update_item_rate(self.item,self.rate)
		else:
			create_new_item(item_name=self.type,item_group=self.item_group,rate=self.rate)
		self.item=self.type
		self.name=self.type


