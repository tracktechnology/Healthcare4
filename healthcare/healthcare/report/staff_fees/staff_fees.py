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
	lower_invoice_date=lower_encounter_date=lower_surger_date=True	
	upper_invoice_date=upper_encounter_date=upper_surger_date=True	
	upper_date=True
	if filters.get("from_date"):
		lower_invoice_date=f""" due_date>='{filters.get("from_date")}'"""
		lower_encounter_date=f""" encounter_date>='{filters.get("from_date")}'"""
		lower_surger_date=f""" surger_date>='{filters.get("from_date")}'"""
	if  filters.get("to_date"):
		# date=add_to_date(filters.get("to_date"), days=1, as_string=True, as_datetime=True)
		upper_invoice_date=f""" due_date<='{filters.get("to_date")}'"""
		upper_encounter_date=f""" encounter_date<='{filters.get("to_date")}'"""
		upper_surger_date=f""" surger_date<='{filters.get("to_date")}'"""
	
	if filters.get("medical_department"):
		dict_filter["department"]= filters["medical_department"]
	if filters.get("doctor"):
		dict_filter["name"]= filters["doctor"]
	doctors=frappe.get_all('Healthcare Practitioner',filters=dict_filter,fields=['name','department','practitioner_name'])
	res=[]
	for i in doctors:
		doctor_percent= frappe.db.sql(f"select booking_percent,consulting_percent from`tabClinic Fees Details` where healthcare_practitioner='{i.name}' ",as_dict=1)
		
		

		total_clinics,count_clinics = frappe.db.sql(f"select COALESCE(SUM(grand_total),0) ,COUNT(DISTINCT patient_encounter)   from `tabSales Invoice`si where  si.docstatus=1 and patient_encounter IN (select name from `tabPatient Encounter` where practitioner='{i.name}' and is_consulting=0 and reservation_type='Clinics' and docstatus=1 and {lower_encounter_date} and {upper_encounter_date}) ",as_list=1)[0]
		total_consulting,count_consulting = frappe.db.sql(f"select COALESCE(SUM(grand_total), 0),COUNT(DISTINCT patient_encounter)   from `tabSales Invoice`si where  si.docstatus=1 and patient_encounter IN (select name from `tabPatient Encounter` where practitioner='{i.name}' and is_consulting=1 and reservation_type='Clinics' and docstatus=1 and {lower_encounter_date} and {upper_encounter_date}) ",as_list=1)[0]




		# frappe.throw(str[count_clinics])

		surgery = frappe.db.sql(f"select S.surgery_total_fees from`tabSurgical Staff Detail` SSD,`tabSurgery`S where SSD.parent=S.name and SSD.healthcare_practitioner='{i.name}' and {lower_surger_date} and {upper_surger_date} ",as_list=1)


		profit_clinics=0
		percent_clinics=0
		percent_observation=0
		profit_observation=0
		# percent_surgery=0
		profit_surgery=0
		total_surgery=0
		min_profit_surgery=0
		percent_profit_surgery=0
		if doctor_percent:

			doctor_percent=doctor_percent[0]
			percent_clinics=doctor_percent.booking_percent
			percent_observation=doctor_percent.consulting_percent
			profit_clinics=percent_clinics*(total_clinics)/100
			profit_observation=percent_observation*(total_consulting)/100
			min_profit_surgery=doctor_percent.minimum_surgery
			percent_profit_surgery=doctor_percent.percent_surgery
		for j in surgery:
			total_surgery+=j[0]
			if j[0]*percent_profit_surgery/100 < min_profit_surgery:
				profit_surgery+=min_profit_surgery
			else:
				profit_surgery+=j[0]*percent_profit_surgery/100



		total_profit=profit_clinics+profit_observation+profit_surgery
		# total_clinical_procedure=frappe.db.sql(f"select COALESCE(SUM(grand_total),0)   from`tabSales Invoice` WHERE patient_encounter IN (select name from `tabPatient Encounter` where practitioner='{i.name}' and reservation_type='Clinical Procedure') ",as_list=1)
		res.append([i.practitioner_name,i.department,
			  count_clinics,total_clinics,percent_clinics,profit_clinics,
			  count_consulting,total_consulting,percent_observation,profit_observation,
			  total_surgery,profit_surgery,
			  total_profit
			  ])

	# frappe.throw(str(res))
	return res


def get_columns(filters=None):
	columns= [
                "Doctor:Data:180",
                "Medical Department:Data:120",
                "Count Clinics:Data:120",
                "Total Clinics:Currency:120",
                "Percent Clinics:Percent:120",
                "Profit Clinics:Currency:120",

                "Count Observation:Data:120",
                "Total Observation:Currency:120",
                "Percent Observation:Percent:120",
                "Profit Observation:Currency:120",

                "Total Surgery:Currency:120",
                "Profit Surgery:Currency:120",

                "Total Profit:Currency:120",



            ]
	return columns

