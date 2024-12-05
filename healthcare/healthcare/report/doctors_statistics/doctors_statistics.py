# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_to_date


def execute(filters=None):
	# frappe.throw(str(filters))
	# columns, data = [], []
	data=get_data(filters)
	columns=get_columns(filters)
	return columns, data



def get_data(filters=None):
	dict_filter={}

	lower_invoice_date=lower_encounter_date=True	
	upper_invoice_date=upper_encounter_date=True	
	upper_date=True

	if filters.get("medical_department"):
		dict_filter["department"]= filters["medical_department"]
	if filters.get("doctor"):
		dict_filter["name"]= filters["doctor"]

	if filters.get("from_date"):
		lower_invoice_date=f""" due_date>='{filters.get("from_date")}'"""
		lower_encounter_date=f""" encounter_date>='{filters.get("from_date")}'"""

	if  filters.get("to_date"):
		date=add_to_date(filters.get("to_date"), days=1, as_string=True, as_datetime=True)
		upper_invoice_date=f""" due_date<='{date}'"""
		upper_encounter_date=f""" encounter_date<='{date}'"""



	doctors=frappe.get_all('Healthcare Practitioner',filters=dict_filter,fields=['name','department','practitioner_name'])
	res=[]
	for i in doctors:
		# count_clinics=frappe.db.sql(f"select count(name)   from`tabPatient Encounter` WHERE reservation_type='Clinics' and practitioner='{i.name}' and {lower_encounter_date} and {upper_encounter_date} and docstatus=1 and is_consulting=0 ",as_list=1)
		# count_consulting=frappe.db.sql(f"select count(name)   from`tabPatient Encounter` WHERE reservation_type='Clinics' and practitioner='{i.name}' and {lower_encounter_date} and {upper_encounter_date} and docstatus=1 and is_consulting=1 ",as_list=1)
		# count_lab=frappe.db.sql(f"select count(name)   from`tabPatient Encounter` WHERE reservation_type='Laboratory' and practitioner='{i.name}' and {lower_encounter_date} and {upper_encounter_date} and docstatus=1 ",as_list=1)
		# count_imaging=frappe.db.sql(f"select count(name)   from`tabPatient Encounter` WHERE reservation_type='Imaging' and practitioner='{i.name}' and {lower_encounter_date} and {upper_encounter_date} and docstatus=1 ",as_list=1)
		# count_clinical_procedure=frappe.db.sql(f"select count(name)   from`tabPatient Encounter` WHERE reservation_type='Clinical Procedure' and practitioner='{i.name}'  and {lower_encounter_date} and {upper_encounter_date} and docstatus=1 ",as_list=1)
	
		name,count_clinics,total_clinics=frappe.db.sql(f"select name,count(name), COALESCE(SUM(grand_total),0)   from`tabSales Invoice` WHERE patient_encounter IN (select name from `tabPatient Encounter` where practitioner='{i.name}' and reservation_type='Clinics' and docstatus=1 and is_consulting=0 ) and status='Paid' and {lower_invoice_date} and {upper_invoice_date} ",as_list=1)[0]
		frappe.msgprint(str(name))
		count_consulting,total_consulting=frappe.db.sql(f"select count(name),COALESCE(SUM(grand_total),0)   from`tabSales Invoice` WHERE patient_encounter IN (select name from `tabPatient Encounter` where practitioner='{i.name}' and reservation_type='Clinics' and docstatus=1 and is_consulting=1 ) and status='Paid' and {lower_invoice_date} and {upper_invoice_date} ",as_list=1)[0]
		count_lab,total_lab=frappe.db.sql(f"select count(name),COALESCE(SUM(grand_total),0)   from`tabSales Invoice` WHERE patient_encounter IN (select name from `tabPatient Encounter` where practitioner='{i.name}' and reservation_type='Laboratory') and status='Paid' and {lower_invoice_date} and {upper_invoice_date} ",as_list=1)[0]
		count_imaging,total_imaging=frappe.db.sql(f"select count(name),COALESCE(SUM(grand_total),0)   from`tabSales Invoice` WHERE patient_encounter IN (select name from `tabPatient Encounter` where practitioner='{i.name}' and reservation_type='Imaging') and status='Paid' and {lower_invoice_date} and {upper_invoice_date} ",as_list=1)[0]
		count_clinical_procedure,total_clinical_procedure=frappe.db.sql(f"select count(name),COALESCE(SUM(grand_total),0)   from`tabSales Invoice` WHERE patient_encounter IN (select name from `tabPatient Encounter` where practitioner='{i.name}' and reservation_type='Clinical Procedure') and status='Paid' and {lower_invoice_date} and {upper_invoice_date} ",as_list=1)[0]
		res.append([i.practitioner_name,i.department,
			  count_clinics,total_clinics,
			  count_consulting,total_consulting,
			  count_lab,total_lab,
			  count_imaging,total_imaging,
			  count_clinical_procedure,total_clinical_procedure,
			  total_clinics+total_consulting+total_lab+total_imaging+total_clinical_procedure
			  ])

	# frappe.throw(str(res))
	return res


def get_columns(filters=None):
	columns= [
                "Doctor:Data:180",
                "Medical Department:Data:120",
                "Count Clinics:Data:120",
                "Total Clinics:Currency:120",
                "Count Consulting:Data:120",
                "Total Consulting:Currency:120",
                "Count Lab:Data:120",
                "Total Lab:Currency:120",
                "Count Imaging:int:120",
                "Total Imaging:Currency:120",
                "Count Clinical Procedure:int:120",
                "Total Clinical Procedure:Currency:120",
				"Total : Currency:120",

            ]
	return columns