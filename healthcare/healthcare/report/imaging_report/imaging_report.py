# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_to_date
from healthcare.healthcare.healthcare_utils import get_practitioner_full_name


def execute(filters=None):
	columns=get_columns(filters)
	data = get_data(filters)
	return columns, data



def get_data(filters=None):
	res=[]
	lower_invoice_date=lower_encounter_date=True	
	upper_invoice_date=upper_encounter_date=True	

	if filters.get("from_date"):
		lower_invoice_date=f""" due_date>='{filters.get("from_date")}'"""
		lower_encounter_date=f""" encounter_date>='{filters.get("from_date")}'"""

	if  filters.get("to_date"):
		# date=add_to_date(filters.get("to_date"), days=1, as_string=True, as_datetime=True)
		# upper_invoice_date=f""" due_date<='{date}'"""
		upper_encounter_date=f""" encounter_date<='{filters.get("to_date")}'"""
	

	patient_encounters=frappe.db.sql(f"Select name,patient,reservation_type,practitioner,medical_department from`tabPatient Encounter` where {upper_encounter_date} and {lower_encounter_date}  and docstatus=1 and reservation_type='Imaging' ",as_dict=1 )
	for i in patient_encounters:
		observation=frappe.db.sql(f"select `observation_template` from`tabLab Prescription` where parenttype='Patient Encounter' and parent='{i['name']}' ",as_list=1)

		practitioner_name=get_practitioner_full_name(i['practitioner'])
		invoice=frappe.db.sql(f""" select name
			, COALESCE(SUM(grand_total),0) as grand_total,is_medical_insurance
			,status 
			from`tabSales Invoice` 
			where patient_encounter='{i['name']}' and patient!='None' """,as_dict=1)
		if invoice:
			invoice=invoice[0]
			invoice['medical_insurance']=None
			invoice['medical_insurance']=frappe.db.get_value("Sales Invoice",{"patient_encounter":i['name'],'patient':None},['customer'])
			mobile,age_years,address=frappe.db.sql(f"select mobile,age_years,address from`tabPatient` where name='{i['patient']}'",as_list=1)[0]
			paper_receipts=frappe.db.sql(f"select paper_receipt from `tabPayment Entry` where patient_encounter='{i.name}'",as_list=1)
			
			res.append([
				i['patient'],
				age_years,
				address,
				mobile,
				practitioner_name,
				i['medical_department'],
				invoice['grand_total'],
				str(paper_receipts),
				invoice['status'],
				invoice['medical_insurance'],
				str(observation),
				i['name']
				])
	return res

def get_columns(filters=None):
	columns= [
                "المريض:Data:180",
                "السن:Data:75",
                "العنوان:Data:120",
                "موبايل:Data:120",
                "الطبيب:Data:120",
                "التخصص:Data:120",
                "القيمة:Currency:120",
				"سند قبض:Data:100",
				"الحالة:Data:120",
				"ملاحظة:Data:120",
				"التحاليل:120",
				"PE:Data:180",
	]
	return columns