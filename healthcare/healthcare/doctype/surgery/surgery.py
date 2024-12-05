# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from erpnext.controllers.myutils import get_dic_from_str,get_dic_from_doc,copy_doc_no_ct
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document


class Surgery(Document):

	def before_save(self):
		self.set_total_items()
		self.set_surgery_profit()

	def before_submit(self):
		self.set_all_doctor_payment()

	@frappe.whitelist()
	def set_all_doctor_payment(self):
		self.set_payment_by_practitoner_type()
		self.set_practitioner_percentage()
		# self.calculate_doctors_payment()
		# self.set_surgeon_payment()
		# self.set_anesthesia_payment()

	@frappe.whitelist()
	def create_surgery_finance(self):
		finance_doc = frappe.new_doc("Surgery Finance")
		tables = get_child_tables()
		copy_doc_no_ct(self,finance_doc,not_allow = tables)
		for table in get_child_tables():
			self.load_table_in_finance_by_name(finance_doc,table)
		finance_doc.surgery = self.name
		finance_doc.insert()

	def load_table_in_finance_by_name(self,finance_doc,table_name):
		if not self.get(table_name): return
		for item in self.get(table_name):
			frappe.msgprint(str(table_name))
			item_dic = get_dic_from_doc(item)
			finance_doc.append(table_name,item_dic)
	def set_payment_by_practitoner_type(self):
		for payment in self.staff_payments:
			type_count = self.get_count_by_practitoner_type(payment.type)
			if payment.for_each == 0 and type_count>0:
				if payment.payment_type == "Value":
					payment.total_value = payment.payment
				else:
					payment.total_value = self.surgery_profit * payment.payment / 100
				payment.value = 1.0 * payment.total_value / type_count
			elif payment.for_each == 1 and type_count>0:
				if payment.payment_type == "Value":
					payment.value = payment.payment
				else:
					payment.value = self.surgery_profit * payment.payment / 100
				payment.total_value = payment.value * type_count

	def set_practitioner_percentage(self):
		for doctor in self.surgical_staff:
			if doctor.has_medical_staff_fees:
				amount_by_per = doctor.percent_surgery * self.surgery_profit / 100
				if amount_by_per > doctor.minimum_surgery:
					doctor_per = amount_by_per
				else: doctor_per = doctor.minimum_surgery
				doctor.doctor_percentage = doctor_per
			else:
				self.set_from_practitioner_type(doctor)

	def set_from_practitioner_type(self,doctor):
		for payment in self.staff_payments:
			if payment.type == doctor.type:
				doctor.doctor_percentage = payment.value
				return

	def get_count_by_practitoner_type(self,type):
		count = 0
		for doctor in self.surgical_staff:
			if doctor.type == type:
				count += 1
		return count

	@frappe.whitelist()
	def get_surgery_type_items(self):
		if not self.surgery_type: return
		doc=frappe.get_doc("Surgery Type",self.surgery_type)
		self.load_items_from_surgery_type(surgery_type_doc=doc)
		self.load_staff_payment_from_surgery_type(doc)


	def load_items_from_surgery_type(self,surgery_type_doc):
		tables = ["medications","consumables","medical_devices"]
		for table in tables:
			self.load_single_table_from_surgery_type(table,surgery_type_doc)

	def load_single_table_from_surgery_type(self,table_name,surgery_type_doc):
		for item in surgery_type_doc.get(table_name):
			item_dic = get_dic_from_doc(item)
			if item_dic:
				self.append(table_name,item_dic)

	def load_staff_payment_from_surgery_type(self,surgery_type_doc):
		for payment in surgery_type_doc.staff_payments:
			payment_dic = get_dic_from_doc(payment)
			self.append("staff_payments",payment_dic)


	def set_total_items(self):
		totals = 0.0
		# load from consumbales table
		# for item in self.items:
		# 	if not item.invoice_separately_as_consumables:
		# 		totals += item.rate * item.qty
		self.items_cost = totals
		self.consumables_cost = totals

	def set_surgery_profit(self):
		self.surgery_profit = self.surgery_total_fees - (self.consumables_cost or 0.0)


	def calculate_doctors_payment(self):
		surgery_type = frappe.get_doc("Surgery Type",self.surgery_type)
		# surgeon
		if surgery_type.surgeon_payment_type == "Percentage":
			self.surgeon_payment_type = "Percentage"
			self.surgeon_percentage = self.surgery_profit * surgery_type.surgeon_payment / 100
		else:
			self.surgeon_payment_type = "Value"
			self.surgeon_percentage = surgery_type.surgeon_payment
		#anesthesia
		if surgery_type.anesthesia_payment_type == "Percentage":
			self.anesthesia_payment_type = "Percentage"
			self.anesthesia_percentage = self.surgery_profit * surgery_type.anesthesia_payment / 100
		else:
			self.anesthesia_payment_type = "Value"
			self.anesthesia_percentage = surgery_type.anesthesia_payment

	def get_surgoens_count(self):
		count =0
		for doctor in self.surgical_staff:
			if doctor.type == "Surgeon":
				count += 1
		if count == 0:
			frappe.msgprint("No Surgeon added to the surgical staff")
		return count

	def get_anesthesias_count(self):
		count =0
		for doctor in self.surgical_staff:
			if doctor.type == "Anesthesia":
				count += 1
		if count == 0:
			frappe.msgprint("No Anesthesia added to the surgical staff")
		return count

	def set_surgeon_payment_per_doctor(self,value):
		for doctor in self.surgical_staff:
			if doctor.type == "Surgeon":
				doctor.doctor_percentage = value

	def get_single_surgeon_payment(self):
		if self.surgeon_payment_type == "Value":
			return self.surgeon_percentage
		else:
			doctors_count = self.get_surgoens_count()
			value = 1.0 * self.surgeon_percentage / doctors_count
			minSurgeon = frappe.db.get_value("Surgery Type",self.surgery_type,"min_surgeon")
			if minSurgeon and minSurgeon > value:
				return minSurgeon
			return value

	def set_surgeon_payment(self):
		value = self.get_single_surgeon_payment()
		self.set_surgeon_payment_per_doctor(value)

	# anesthesia
	def set_anesthesia_payment_per_doctor(self, value):
		for doctor in self.surgical_staff:
			if doctor.type == "Anesthesia":
				doctor.doctor_percentage = value

	def get_single_anesthesia_payment(self):
		if self.anesthesia_payment_type == "Value":
			return self.anesthesia_percentage
		else:
			doctors_count = self.get_surgoens_count()
			value = 1.0 * self.anesthesia_percentage / doctors_count
			minAnesthesia = frappe.db.get_value("Surgery Type",self.surgery_type,"min_anesthesia")
			if minAnesthesia and minAnesthesia > value:
				return minAnesthesia
			return value

	def set_anesthesia_payment(self):
		value = self.get_single_anesthesia_payment()
		self.set_anesthesia_payment_per_doctor(value)



@frappe.whitelist()
def get_surger_per_from_medical_staff_fees(practitioner):
	res = frappe.db.sql(
		f"""select minimum_surgery,percent_surgery 
		from`tabMedical Staff Fees Details` where healthcare_practitioner='{practitioner}' """,
		as_dict=1)
	if res:
		return res[0]
	return None


def get_surgery_finance_doc(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Surgery",  # Source DocType
		source_name,    # Source Document (Sales Order Name)
		{
			"Surgery": {  # Mapping for the parent DocType
				"doctype": "Surgery Finance",  # Target DocType
				"field_map": {
					"consumables": "consumables",
					"medical_devices": "medical_devices"
				}
			},
			# "Sales Order Item": {  # Mapping for the child table
			# 	"doctype": "Delivery Note Item",  # Target child table
			# 	"field_map": {
			# 		"rate": "rate",
			# 		"item_code": "item_code",
			# 		"qty": "qty"
			# 	},
			# 	"postprocess": update_item  # A function to modify the child doc
			# }
		},
		target_doc
	)

	return doc

def get_child_tables():
	return {
    "surgical_staff",
    "consumables",
    "medical_devices",
    "staff_payments",
    "medications",
    "extra_medication",
    "extra_consumables",
    "extra_medical_devices",
    "return_medication",
    "return_consumables",
    "return_medical_devices"
}