# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from pypdf import PdfWriter
import os
from frappe.utils.pdf import get_pdf
from PyPDF2 import PdfMerger
from io import BytesIO
from erpnext.controllers.myutils import get_dic_from_doc,open_new_single_doc,copy_doc,copy_doc_no_ct
from healthcare.healthcare.doctype.reservation.reservation import set_observation_patient_encounter
from healthcare.healthcare.reservation_accounts import make_payment,print_receipt,set_insurance_company_sales_invoice,set_contract_invoice
from healthcare.healthcare.healthcare_utils import create_lab_test
from erpnext.accounts.doctype.patient_due.patient_due import set_patient_due
from erpnext.accounts.doctype.company_due.company_due import set_company_due

from healthcare.healthcare.doctype.nursing_tool.nursing_tool import set_patient_record_items
class LabTestTool(Document):

	@frappe.whitelist()
	def add_external_lab(self,observation,external_lab):
		price = get_external_lab_price(observation,external_lab)
		self.append("external_labs",{
			"observation": observation,
			"external_lab": external_lab,
			"price": price
		})


	@frappe.whitelist()
	def get_lab_test(self):
		status="Draft"
		if self.edit:
			status="Completed"
		data=frappe.db.sql(f"""select template
		,name,observation_request,status ,is_external_lab
		from`tabLab Test` 
		where patient='{self.patient}' and is_printed=0 and status='{status}' """,as_dict=1)
		return data
	
	@frappe.whitelist()
	def get_lab_items(self):
		doc = frappe.get_doc("Lab Test",self.lab_test)
		self.items=doc.normal_test_items
		self.custom_result=doc.custom_result



	@frappe.whitelist()
	def update_lab_items(self):
		doc = frappe.get_doc("Lab Test",self.lab_test)
		doc.normal_test_items=[]
		for i in self.items:
			doc.append('normal_test_items', i)
		doc.custom_result=self.custom_result
		doc.save()
		frappe.db.commit()
		doc.submit()

		
	@frappe.whitelist()
	def get_print_test(self):
		# doc = frappe.get_doc("Observation Request",self.print_observation_request)
		if self.reprint:
			tests = frappe.db.sql(f"""
				SELECT template, name,is_printed,observation_request
				FROM `tabLab Test` lt
				WHERE creation = (
					SELECT MAX(creation)
					FROM `tabLab Test`
					WHERE template = lt.template  and patient='{self.print_patient}' and is_printed=1
				)
			""", as_dict=True)
		else:
			# tests = frappe.get_all("Lab Test",{'patient':self.print_patient,'status':"Completed","is_printed":1},['name','template','is_printed','observation_request'])
		
		
			tests=frappe.db.sql(f"""SELECT LT.name,LT.template,LT.is_printed,LT.observation_request from `tabLab Test` LT,`tabObservation Request` R WHERE R.name= LT.observation_request and LT.is_printed=0 and LT.status= 'Completed' and LT.patient='{self.print_patient}' and R.status='Paid'""",as_dict=True)	


		return tests


	@frappe.whitelist()
	def get_lab_test_details(self):
		doc = frappe.get_doc("Lab Test",self.print_lab_test)
		self.print_items=doc.normal_test_items
		self.print_custom_result=doc.custom_result
		
		# from frappe import get_print
		



	@frappe.whitelist()
	def get_pdf_test(self):

		grouped_data = {}

		for item in self.print_items:
			key = item.event_group
			if key not in grouped_data:
				grouped_data[key] = []
			grouped_data[key].append(item.as_dict())

		template = "healthcare/healthcare/doctype/lab_test_tool/template.html"
		base_template_path = "healthcare/healthcare/doctype/lab_test_tool/print_preview.html"
		items = []
		# invoice_items = []
		# frappe.msgprint(str(invoice_items))
		total = 0.0
		# current_time = frappe.utils.now_datetime()
		# formatted_time = current_time.strftime(" %H:%M")
		from frappe.www.printview import get_letter_head
		html = frappe.render_template(template, {
			"items":grouped_data,
			'patient':self.print_patient,
			'date_reported': frappe.utils.today(),
			'referred_by':"",
			"test":self.print_test,
		})
		final_template = frappe.render_template(base_template_path, {"body": html, "title": "Lab Report"})

		frappe.db.set_value("Lab Test",self.print_lab_test,"is_printed",True)

		return final_template
		# frappe.throw(str(grouped_data))

		# html_docs = []
		# if not self.reprint:
		# 	docnames = frappe.get_all("Lab Test",{'patient':self.print_patient,'status':"Completed","is_printed":'0'},pluck='name')
		# else:
		# 	docnames=[self.print_lab_test]
		# for name in docnames:
		# 	print_pdf = frappe.get_doc("Lab Test", name)
		# 	html_content = frappe.get_print(
		# 		doc=print_pdf,
		# 		print_format='Lab Test Print',
		# 		no_letterhead=0
		# 	)
		# 	html_docs.append(f'<div style="page-break-after: always;">{html_content}</div>')
	
		# return html_docs
	@frappe.whitelist()
	def get_observation_request(self):

		requests=frappe.db.sql("""select name,patient,creation,reservation_type,observation_date from `tabObservation Request` 
						 where status ='Pending' and docstatus=1 and observation_category='Laboratory'
						  ORDER BY  CASE  WHEN reservation_type = 'Emergency' THEN 1  ELSE 2 END, creation ASC """,as_dict=1)
		self.requests=[]

		for i in requests:
			self.append("requests",{	
				"patient":i.patient,
				"observation_request":i.name,
				"reservation_type":i.reservation_type,
				"observation_date":i.observation_date
			})


	def set_observation_invoice(self,request):
		item_print=[]
		# for i in requests:
		observation=[]
		for i in request.observation:
			observation.append(i.observation)
		
		patient_encounter= set_observation_patient_encounter(self.r_patient, request.doctor,
												request.medical_department,observation, "Laboratory",self.encounter_id,request.observation_date)
		
		is_healthcare_insurance=0
		if self.company_percentage:
			is_healthcare_insurance=1
		
		items=make_payment(patient=self.r_patient, insurance_company=self.medical_insurance,
			percentage=float(self.patient_percentage),company_percentage=float(self.company_percentage), 
			is_healthcare_insurance=is_healthcare_insurance, patient_encounter= patient_encounter,
			doctor=request.doctor,items=self.observation,hospital_percentage=self.hospital_percentage,posting_date=request.observation_date)

		# items=make_payment(patient=self.r_patient,  
		# 		patient_encounter=patient_encounter,
		# 		doctor=request.doctor,items=self.observation,total=self.amount_due,percentage=self.patient_percentage)
		return patient_encounter

	@frappe.whitelist()
	def reset_external_labs_on_change_in_observation(self):
		observations = [item.observation for item in self.observation]
		idx = 0
		new_labs = []
		for lab in self.external_labs:
			if lab.observation in observations:
				idx += 1
				lab.idx = idx
				new_labs.append(lab)
		self.external_labs = new_labs



	def validate_before_confirm(self):
		observations = [item.observation for item in self.observation]
		are_unique = len(observations) == len(set(observations))
		if not are_unique:
			frappe.throw("يوجد تكرار للتحاليل")
		externals = [lab.observation for lab in self.external_labs]
		for external in externals:
			if external not in observations:
				frappe.throw("Lab : "+ str(external) + " can't be in external labs and not in patient labs" )
		are_unique = len(externals) == len(set(externals))
		if not are_unique:
			frappe.throw("يوجد تكرار للتحاليل الخارجية")

	@frappe.whitelist()
	def set_observation_request(self):
		self.validate_before_confirm()
		# frappe.throw("For test")
		doc = frappe.get_doc("Observation Request",self.r_observation_request)
		doc.observation=self.observation
		doc.status="Unpaid"
		doc.total=self.total
		doc.remaining_amount=self.total
		if self.amount_due==0 :
			doc.status="Paid"
			create_lab_test(doc)
		
		if self.reservation_type=="Outpatient":

			doc.patient_encounter=self.set_observation_invoice(doc)

		elif self.reservation_type=="Emergency":
			self.set_emergency_observation()
			doc.status="Paid"
			create_lab_test(doc)
					
		self.set_external_labs_in_observation_request(doc)
		doc.save()
		self.create_purchase_invoice_for_external_labs(doc.name)


	def set_emergency_observation(self):
		items=[]
		doc=frappe.get_doc("Inpatient Record",{"patient":self.r_patient})

		for i in self.observation_details:
			items.append({
				"item_name": i.get("observation"),
				"service": i.get("observation"),
				"qty": 1,
				"rate": i.get("price"),
				'reservation_type':self.reservation_type,
				"inpatient_record":doc.name
			})

		set_patient_record_items(doc,items,"lab_test_prescription","observation_template")

		set_patient_due(self.r_patient,items,self.patient_percentage)

		if self.company_percentage:
			# set_insurance_company_sales_invoice(
			# 			insurance_company=self.medical_insurance,
			# 		percentage=self.company_percentage, inpatient_record=doc.name,
			# 		items=self.observation)
			set_company_due(self.r_patient,self.medical_insurance,items,self.company_percentage)

		if self.hospital_percentage:
			set_contract_invoice(insurance_company=self.medical_insurance,
						percentage=self.hospital_percentage,items=self.observation, inpatient_record=doc.name)



	def set_external_labs_in_observation_request(self,request_doc):
		from erpnext.controllers.myutils import get_dic_from_doc
		if not self.external_labs:
			return

		for lab in self.external_labs:
			lab_dic = get_dic_from_doc(lab)
			# frappe.throw(str(lab_dic))
			request_doc.append("external_labs",lab_dic)
	def create_purchase_invoice_for_external_labs(self,request_name):
		if not self.external_labs:
			return
		labs_details = {}
		for lab in self.external_labs:
			if labs_details.get(lab.external_lab):
				labs_details[lab.external_lab].append([lab.observation,lab.price])
			else:
				labs_details[lab.external_lab] = [[lab.observation,lab.price]]
		for key,value in labs_details.items():
			create_single_purchase_invoice(key,value,request_name)


	@frappe.whitelist()
	def cancel_observation_request(self,observation_request):
		doc = frappe.get_doc("Observation Request",observation_request)
		doc.cancel()		



@frappe.whitelist()
def get_item_price(items):
	
	items = list(eval(items))
	items_list = [""]
	for i in items:
		items_list.append(i['observation'])
	items = tuple(items_list)
	res = frappe.db.sql(f"""SELECT item_code as observation,price_list_rate as price FROM `tabItem Price` 
	where item_code IN {items} and selling = 1 and buying = 0 """, as_dict=1)
	# for i in res:

	return res
	# return [item,frappe.db.get_value("Item Price", {"item_code": item, "price_list": "Standard Selling"}, ['price_list_rate'])]



def get_external_lab_price(observation,external_lab):
	sql = f""" select price 
	from `tabExternal Lab Pricing Details` 
	where parent = '{external_lab}' and parenttype = 'External Lab Pricing' 
	and observation = '{observation}'  """
	res = frappe.db.sql(sql, as_list=1)
	if res:
		return res[0][0]
	frappe.throw("Please Set Price for " + str(observation) + " in LAB: " + str(external_lab))


def create_single_purchase_invoice(external_lab,labs,request):
	supplier = frappe.db.get_value("External Lab",external_lab,"supplier")
	if not supplier:
		frappe.throw("Please set supplier for " + str(external_lab))
	purchase_invoice = frappe.new_doc("Purchase Invoice")
	purchase_invoice.supplier = supplier
	purchase_invoice.observation_request = request
	for lab in labs:
		purchase_invoice.append("items",{
			"item_code": lab[0],
			"item_name": frappe.db.get_value("Item",lab[0],"item_name"),
			"rate": lab[1],
			"qty":1,
			"amount": lab[1]
		})
	purchase_invoice.save()





	