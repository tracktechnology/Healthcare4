# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MedicalInsurance(Document):

	def before_save(self):
		by_medical_insurance_type = frappe.db.get_single_value("Medical Insurance Setting", "by_medical_insurance_type")
		if by_medical_insurance_type and self.is_customer:
			if not self.medical_insurance_type:
				frappe.throw("Please Set Medical Insurance Type")

	def on_submit(self):
		if self.is_customer:

			self.create_customer()

	def create_customer(self):
		customer = frappe.new_doc("Customer")
		customer.customer_name = self.name
		customer.customer_type = "Company"
		by_medical_insurance_type = frappe.db.get_single_value("Medical Insurance Setting","by_medical_insurance_type")
		if not by_medical_insurance_type:
			account = self.create_account()
			company = frappe.db.get_value("Account",account,"company")
			customer.append("accounts", {
				'account': account,
				'company': company # "Track INT'l Trad (Demo)"
			})
		customer.insert(ignore_permissions=True)


	def create_account(self):
		# parent_account = "1320 - Health Insurance Companies - TITD"
		parent_account = frappe.db.get_single_value("Medical Insurance Setting","parent_accout")
		account_doc_name = create_member_account_by_parent_account(self.name, parent_account)
		return account_doc_name


def create_member_account_by_parent_account(member_name, parent_account):
	max_account_number = get_max_account_number(parent_account)
	# frappe.throw(str(parent_account))
	account = frappe.new_doc("Account")
	set_account_default(account, parent_account)
	if max_account_number:
		account.account_number = int(max_account_number) + 1
	else:
		# account.account_parent=parent_account
		account.account_number = int(str(account.account_number) + "00001")
	account.account_name = member_name
	frappe.msgprint(str(account.as_dict()))
	account.insert(ignore_permissions=True)
	return account.name


def set_account_default(doc, paren_account, currency="EGP"):
	parent_account_doc = frappe.get_doc("Account", paren_account)
	# copy_doc_no_ct(parent_account_doc,doc)
	doc.root_type = parent_account_doc.root_type
	doc.report_type = parent_account_doc.report_type
	doc.account_type = parent_account_doc.account_type
	doc.account_currency = parent_account_doc.account_currency
	doc.company = parent_account_doc.company
	doc.account_number = parent_account_doc.account_number
	doc.is_group = 0
	doc.parent_account = parent_account_doc.name
	doc.currency = currency


def get_max_account_number(parent_account):
	sql = f"""
	  select max(account_number) from `tabAccount` where parent_account = '{parent_account}'
	  """
	res = frappe.db.sql(sql, as_list=1)
	if res[0][0]:
		return res[0][0]
	else:
		return None
