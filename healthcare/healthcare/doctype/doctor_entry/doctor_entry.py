# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

from healthcare.healthcare.reservation_accounts import set_payment_entry,print_receipt,make_doctor_entry

class DoctorEntry(Document):
	pass


def create_entry_from_sales_invoice_insurance():

	date_string = "2024-09-8"
	posting_date = datetime.strptime(date_string, "%Y-%m-%d").date()

	# insurance_invoices= frappe.db.sql(f"select name from `tabSales Invoice` where patient IS NULL and docstatus=1 and posting_date<='{posting_date}' and updated=0 limit 10",as_dict=1)
	insurance_invoices= frappe.db.sql(f"select name from `tabSales Invoice` where patient IS NULL and docstatus=1 and posting_date<='{posting_date}' and is_updated=0 limit 20 ",as_dict=1)

	for i in insurance_invoices:
		doc = frappe.get_doc("Sales Invoice",i.name)

		paper_receipt=doc.paper_receipt

		pe=frappe.get_doc("Patient Encounter",doc.patient_encounter)
		paid_amount=doc.grand_total
		if  pe.practitioner and not pe.cancel_doctor_fees:

			total_ratio=paid_amount/doc.total_before_discount
			make_doctor_entry(doctor=pe.practitioner,patient_encounter=pe.name,doctor_discount=pe.doctor_discount,
					reservation_type=pe.reservation_type,items=doc.items,sales_invoice=doc.name,grand_total=paid_amount,total_ratio=total_ratio,paper_receipt=paper_receipt,posting_date=doc.posting_date)
				
		doc.db_set('is_updated',1) # update field in  doc




def create_entry_from_sales_invoice():
	date_string = "2024-09-8"
	posting_date = datetime.strptime(date_string, "%Y-%m-%d").date()

	insurance_invoices= frappe.db.sql(f"select name from `tabSales Invoice` where patient IS NOT NULL and docstatus=1 and is_updated=0 and posting_date<='{posting_date}' limit 20",as_dict=1)
	for i in insurance_invoices:
		doc = frappe.get_doc("Sales Invoice",i.name)

		paper_receipt=doc.paper_receipt
		pe=frappe.get_doc("Patient Encounter",doc.patient_encounter)
		paid_amount=doc.paid_amount
		if  pe.practitioner and not pe.cancel_doctor_fees:
			total_ratio=paid_amount/doc.total_before_discount
			make_doctor_entry(doctor=pe.practitioner,patient_encounter=pe.name,doctor_discount=pe.doctor_discount,
					reservation_type=pe.reservation_type,items=doc.items,sales_invoice=doc.name,grand_total=paid_amount,total_ratio=total_ratio,paper_receipt=paper_receipt,posting_date=doc.posting_date)
					
		doc.db_set('is_updated',1) # update field in  doc

		