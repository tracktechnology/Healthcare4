# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
# from frappe.model.document import Document
from erpnext.controllers.myutils import get_dic_from_doc, copy_doc_no_ct


def create_supplier_account(supplier):
    parent_account = "2100 - Accounts Payable - TITD"
    account = create_account_by_parent_account(supplier.name,parent_account)
    return account


def create_account_by_parent_account(member_name, parent_account):
    max_account_number = get_max_account_number(parent_account)
    # frappe.throw(str(parent_account))
    account = frappe.new_doc("Account")
    set_account_default(account, parent_account)
    if max_account_number:
        account.account_number = int(max_account_number) + 1
    else:
        # account.account_parent=parent_account
        account.account_number = int(str(account.account_number) + "000001")
    account.account_name = member_name
    # frappe.msgprint(str(account.as_dict()))
    account.insert(ignore_permissions=True)
    return account.name


def set_account_default(doc, paren_account, currency="EGP"):
    parent_account_doc = frappe.get_doc("Account", paren_account)
    # copy_doc_no_ct(parent_account_doc,doc)
    doc.root_type = parent_account_doc.root_type
    doc.report_type = parent_account_doc.report_type
    doc.account_currency = parent_account_doc.account_currency
    doc.company = parent_account_doc.company
    doc.account_number = parent_account_doc.account_number
    doc.is_group = 0
    doc.parent_account = parent_account_doc.name
    doc.account_type = parent_account_doc.account_type
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
