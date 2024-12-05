	# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from healthcare.healthcare.healthcare_utils import get_practitioner_full_name
from frappe.utils import time_diff_in_seconds


def execute(filters=None):
	columns, data = get_columns(filters),get_data(filters)
	return columns, data



def get_data(filters=None):
	res=[]
	encounters=frappe.db.sql("""select * from`tabPatient Encounter` where status='Cancelled' order by creation DESC """,as_dict=True)

	observations=frappe.db.sql("""select patient,observation_category as reservation_type,doctor,
			creation,modified,modified_by
			from`tabObservation Request` where docstatus='2'""",as_dict=True) 
	reservations=encounters+observations
	for i in reservations:
		practitioner_name=get_practitioner_full_name(i.get('practitioner')or i.get('doctor'))
		if practitioner_name and not i.get("medical_department"):
			i['medical_department']=frappe.db.get_value("Healthcare Practitioner",i['doctor'],'department')

		user_name=frappe.db.get_value("User",i['modified_by'],'full_name')

		res.append([
			i['patient'],
			i['reservation_type'],
			# i['modified_by'],
			user_name,
			i['creation'],
			i['modified'],
			format(time_diff_in_seconds(i['modified'], i['creation'])/60,"0.0f"),
			practitioner_name,
			i.get('medical_department')
		])
	return res



def get_columns(filters):
	columns= [
                "المريض:Data:195",
                "نوع الحجز: Data:200",
				"user: Data:180",
				"created: Data:180",
				"Cancel Time: Data:150",
				"Diff MIN : Data:80",
				"الطبيب:Data:118",
                "التخصص:Data:92",

			]
	return columns