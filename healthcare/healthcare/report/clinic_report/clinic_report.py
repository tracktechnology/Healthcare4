# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_to_date


def execute(filters=None):
	columns=get_columns(filters)
	data = get_data(filters)
	return columns, data



def get_data(filters=None):
	res=[]
	lower_invoice_date=lower_encounter_date=True	
	upper_invoice_date=upper_encounter_date=True
	doctor=medical_department=True	
	# frappe.msgprint(str(filters))
	if filters.get("from_date"):
		lower_invoice_date=f""" due_date>='{filters.get("from_date")}'"""
		lower_encounter_date=f""" encounter_date>='{filters.get("from_date")}'"""
		# frappe.msgprint(str(lower_encounter_date))

	if  filters.get("to_date"):
		# date=add_to_date(filters.get("to_date"), days=1, as_string=True, as_datetime=True)
		date = filters.get("to_date")
		upper_invoice_date=f""" due_date<='{date}'"""
		upper_encounter_date=f""" encounter_date<='{date}'"""
		# frappe.msgprint(str(upper_encounter_date))
	if  filters.get("doctor"):
		doctor=f""" practitioner='{filters.get("doctor")}'"""
	if  filters.get("medical_department"):
	
		medical_department=f""" medical_department='{filters.get("medical_department")}'"""

	

	patient_encounters=frappe.db.sql(f"""Select name,patient,reservation_type,practitioner,medical_department,is_consulting 
	from`tabPatient Encounter` 
	where {upper_encounter_date} and {lower_encounter_date}  and {doctor} and {medical_department}
	and docstatus!=0 and reservation_type='Clinics' """,as_dict=1 )
	for i in patient_encounters:
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
			type="كشف"
			if i['is_consulting']:
				type="متابعة"
			res.append([
				i['patient'],
				age_years,
				address,
				mobile,
				practitioner_name,
				i['medical_department'],
				invoice['grand_total'],
				type,
				str(paper_receipts),
				invoice['status'],
				invoice['medical_insurance'],
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
				"كشف/متابعة : Data:120",
				"سند قبض:Data:100",
				"الحالة:Data:120",
				"ملاحظة:Data:120",
				"PE:Data:180",

	]
	return columns



def get_practitioner_full_name(name):
	return frappe.db.get_value("Healthcare Practitioner",name,"practitioner_name")
