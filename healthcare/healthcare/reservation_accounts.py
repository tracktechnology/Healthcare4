import frappe
from frappe.utils import add_days, getdate,today
import copy
from erpnext.controllers.myutils import copy_doc_no_ct


def make_payment(patient, insurance_company=None, percentage=None,company_percentage=None,
				 hospital_percentage=None ,is_healthcare_insurance=False, patient_encounter=None,
				 paper_receipt=None,is_consultation=None,doctor=None,paid_amount=0,items=None,total=0,
				 posting_date=None):
	# if total:
	# 	check_min_payment(paid_amount,total)
	invoice_item =  copy.deepcopy(items)
	# frappe.throw(str(percentage))
	if percentage > 0  or not is_healthcare_insurance:
		invoice_item, invoice_name,invoice_number = set_sales_invoice(patient=patient, percentage=percentage, 
												 patient_encounter=patient_encounter,paper_receipt=paper_receipt,
												 is_consultation=is_consultation,doctor=doctor,paid_amount=paid_amount,
												 items=invoice_item,is_healthcare_insurance=is_healthcare_insurance,posting_date=posting_date)
	else:
		invoice_name = None
	# if is_healthcare_insurance:
	insurance_company_percent = float(company_percentage)
	hospital_percentage = float(hospital_percentage)

	if insurance_company_percent:
		set_insurance_company_sales_invoice(patient=patient, reference_dt=invoice_name, insurance_company=insurance_company, 
									  percentage=insurance_company_percent, patient_encounter=patient_encounter,paper_receipt=paper_receipt,
									  is_consultation=is_consultation,doctor=doctor,paid_amount=paid_amount,items=items,posting_date=posting_date)
	if hospital_percentage:

		set_contract_invoice(insurance_company=insurance_company,percentage=float(hospital_percentage),items=items,
					    patient_encounter=patient_encounter,posting_date=posting_date)

		

	# frappe.msgprint(str("تم الحجز بنجاح"))
	if not  'invoice_number' in locals():
		invoice_number=000000
	# frappe.throw(str(invoice_item[0].as_dict()))
	return invoice_item,invoice_number,invoice_name


def set_sales_invoice(patient, company="Track INT'l Trad (Demo)", insurance_company=None, percentage=None, items=None,
					  reference_dt=None, patient_encounter=None,paper_receipt=None,
					  is_consultation=0,doctor=None,paid_amount=0,is_healthcare_insurance=0,posting_date=None):
	invoices = []
	total = 0
	total_before_discount = 0
	doc = frappe.new_doc("Sales Invoice")
	total_before_discount = 0
	for i in items:
		service = "Unknown"

		if i.get('service')=='كشف' or i.get('service')=='أستشارة':
			# i['rate']=get_doctor_fees(doctor,is_consultation)
			service=i.get('service')
			rate_before_discount=i['grand_total']
			i['grand_total']=i['rate']
			# if is_consultation=='1' :
			# 	service="أستشارة"
			# paid_amount = i['rate']
			percentage=0  #percentage set in reservation doc that is execption for this service
			item,amount,rate=get_item(i,percentage)
			

		else:
			item,amount,rate_before_discount=get_item(i,percentage)
			
		doc.append("items",item)
		
		total+=amount
		total_before_discount+=rate_before_discount



		invoices.append({
			"item_name": item['item_name'],
			"rate": rate_before_discount,
			# "print_rate": i['rate']
		})

	if not insurance_company:
		doc.patient = patient
		doc.customer = patient
	else:
		insurance_company_name = frappe.db.get_value("Medical insurance company",insurance_company, "company_name")
		doc.customer = insurance_company_name
		# frappe.throw(str(doc.customer))

	doc.hub_manager = "ahmed.khalifa@track-eg.com"
	doc.total_before_discount = total_before_discount
	doc.base_grand_total = total
	doc.reference_dt = reference_dt
	# doc.paid_amount=float(paid_amount)
	# doc.paid=float(paid_amount)
	# doc.base_paid_amount = float(paid_amount)
	doc.patient_encounter = patient_encounter
	doc.due_date = getdate()
	doc.posting_date=posting_date
	doc.due_date=posting_date
	# doc.paper_receipt=paper_receipt
	doc.set_posting_time=1	
	if is_healthcare_insurance:
		doc.is_medical_insurance=1
	# doc.save()
	# frappe.throw(str(doc.as_dict()))
	# if total==0:
	# 	return [invoices,None]
	# frappe.throw(str(doc.as_dict()))
	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)


	# doc.submit()
	# if doc.grand_total != 0 and not insurance_company:

	# 	set_payment_entry(doc)

	# invoices_status = "Paid"
	# outstanding_amount = 0

	# if insurance_company:
	# 	invoices_status = "Unpaid"
	# 	outstanding_amount = doc.grand_total

	# doc.db_set('outstanding_amount', outstanding_amount)
	# doc.db_set('status', invoices_status)
	return [invoices, doc.name,doc.invoice_number]



def set_contract_invoice(insurance_company,percentage,items,patient_encounter=None,inpatient_record=None,posting_date=None):
	doc=frappe.new_doc("Contract Invoice")
	doc.company_percentage=percentage
	doc.medical_insurance=insurance_company
	total = 0
	total_before_discount = 0
	for i in items:
		item,amount,rate_before_discount=get_item(i,percentage)
		total+=amount
		total_before_discount+=rate_before_discount
		doc.append("items",item)
	doc.grand_total = total_before_discount
	doc.total =total
	doc.patient_encounter = patient_encounter
	doc.inpatient_record=inpatient_record
	doc.date=posting_date
	doc.set_posting_time=1	

	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)

	doc.submit()

def set_payment_entry(invoice,paid_amount,posting_date=today(),ip=None):

	doc = frappe.new_doc("Payment Entry")
	doc.party_type = "Customer"
	doc.party = invoice.customer
	doc.mode_of_payment = "Cash"
	doc.payment_type = "Receive"
	doc.paid_amount = paid_amount
	doc.received_amount = invoice.grand_total
	doc.target_exchange_rate = 1
	doc.paid_from = invoice.debit_to
	doc.paid_to = "1110 - Cash - TITD"
	if ip:
		treasury=get_treasury_account_by_ip(ip)
		if treasury:
			set_paid_to_account(doc,treasury.treasury_unit,treasury.account)
	doc.party_account = invoice.debit_to
	doc.sales_invoice = invoice.name
	doc.paid_to_account_type = "Cash"
	doc.patient_encounter = invoice.patient_encounter
	doc.paper_receipt = invoice.paper_receipt
	doc.posting_date =posting_date
	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
	# frappe.throw("after insert:: " +str(doc.paid_to))

	doc.submit()
	return True

def set_paid_to_account(payment_entry,treasury_unit,account):
	payment_entry.treasury_unit = treasury_unit
	# account = get_treasury_account(treasury_unit)
	# frappe.throw(str(account))
	payment_entry.paid_to = account

def get_treasury_account(treasury,currency='EGP'):
	account = frappe.db.sql(f""" select account 
	from `tabTreasury Account` 
	where treasury = '{treasury}' and currency = '{currency}' """, as_list=1)
	if account:
		return account[0][0]
	frappe.msgprint(f"Please set account for treasury:{str(treasury)} and currency: {str(currency)}")

def get_item_price(item):
	return frappe.db.get_value("Item Price", {"item_code": item, "price_list": "Standard Selling"}, ['price_list_rate'])



def get_doctor_fees(doctor,is_consultation):
	field="out_patient_booking_charge"
	if  is_consultation:
		field="op_consulting_charge"
	# frappe.throw(is_consultation)
	return  frappe.db.get_value("Healthcare Practitioner", {"name": doctor}, [field])



def print_receipt(invoice_items,doctor_name=None,patient_name=None,medical_dep=None,paid=0,
			   total=0,queue_number=1,patient_percentage=0,insurance_company=None,invoice_number=None):
	template = "healthcare/healthcare/doctype/reservation/template.html"
	base_template_path = "healthcare/healthcare/doctype/reservation/print_preview.html"
	items = []
	total=0
	# invoice_items = []
	# frappe.throw(str(invoice_items))
	# TODO: set rate here by item_price fn
	for item in invoice_items:
		item_print = {
			"item_name": item.get("item_name")or item.get("service"),
			"item_price": item.get("rate"),
			"qty": int(item.get("qty") or 1),
		}
		items.append(item_print)
		total += item.get("rate")
	current_time = frappe.utils.now_datetime()
	formatted_time = current_time.strftime(" %H:%M")
	from frappe.www.printview import get_letter_head

	user_name=frappe.db.get_value("User",frappe.session.user,'full_name')
	paid=float(paid)
	if paid and not patient_percentage:
		patient_percentage = format(1.0 * paid / total * 100,".2f")
	
	invoice_note=""
	if paid==0:
		invoice_note="لا يوجد مدفوعات للفاتورة"
	elif not insurance_company and paid!=total:
		invoice_note=" دفع جزئي من الفاتورة"
	
	# if medical_dep=='':
	
	total_patient_amount=(float(patient_percentage)or 100)/100*total
	html = frappe.render_template(template, {
		"patient_name": patient_name,
		# "items": items,	
		"total": total,
		"date": getdate(),
		"time": formatted_time,
		"paid":paid or (1.0 * patient_percentage * total / 100),
		"medical_department": medical_dep  or 'undefined',
		"patient_percentage": patient_percentage,
		"doctor_name": get_doctor_title(doctor_name)  or 'undefined',
		"patient_code":get_patient_code(patient_name),
		"items":items,
		"insurance_company":insurance_company or 'undefined',
		"queue_number":queue_number,
		"invoice_number":invoice_number,
		"user_name":user_name,
		"invoice_note":invoice_note,
		# "total_patient_amount":format(total_patient_amount,".2f"),
	})
	final_template = frappe.render_template(base_template_path, {"body": html, "title": "Report Card"})

	return final_template



def get_doctor_title(healthcare_practitioner):
	return frappe.db.get_value("Healthcare Practitioner",healthcare_practitioner,'practitioner_name')




def get_patient_code(patient_name):
	return frappe.db.get_value("Patient",patient_name,'patient_code')




def check_min_payment(paid,total):
	min_payment_percent=frappe.db.get_single_value("Hospital Setting","min_payment_percent")
	percent_paid=paid/total*100
	if percent_paid<min_payment_percent:
		frappe.throw(f"لا يمكن تحصيل أقل من {min_payment_percent}% من الاجمالي ")






def set_insurance_company_sales_invoice(patient=None, company="Track INT'l Trad (Demo)", insurance_company=None, percentage=None, items=None,
					  reference_dt=None, patient_encounter=None,paper_receipt=None,
					  is_consultation=0,doctor=None,paid_amount=0,inpatient_record=None,posting_date=None):
	invoices = []
	total = 0
	doc = frappe.new_doc("Sales Invoice")
	total_before_discount = 0
	doc.customer = insurance_company

	for i in items:
		item,amount,rate_before_discount=get_item(i,percentage)
		total+=amount
		total_before_discount+=rate_before_discount
		doc.append("items",item)

	doc.hub_manager = "ahmed.khalifa@track-eg.com"
	doc.total_before_discount = total_before_discount
	doc.base_grand_total = total
	doc.reference_dt = reference_dt
	# doc.paid_amount=float(total)
	# doc.paid=float(total)
	# doc.base_paid_amount = float(total)
	doc.patient_encounter = patient_encounter
	doc.inpatient_record = inpatient_record
	doc.paper_receipt = paper_receipt
	doc.due_date = getdate()
	doc.posting_date = posting_date
	doc.due_date=posting_date
	doc.is_medical_insurance=1
	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
	doc.submit()

	# set_payment_entry(doc)

	invoices_status = "Unpaid"
	outstanding_amount = doc.grand_total

	doc.db_set('outstanding_amount', outstanding_amount)
	doc.db_set('status', invoices_status)
	return [invoices, doc.name]




def get_item(item,percentage ):
	i=item
	try:
		i=i.as_dict()
	except Exception:
		i=i
	income_account = "4110 - Sales - TITD"
	qty = i.get("qty") or  1
	if i.get('service')=='كشف' or i.get('service')=='أستشارة':
		# i['rate']=get_doctor_fees(doctor,is_consultation)
		i['rate']=i['grand_total']
		service=i.get('service')
		# if is_consultation :
		# 	service="أستشارة"
		# paid_amount = i['rate']

	elif i.get('service')=='كشف طوارئ':	
		i['rate']=frappe.db.get_single_value("Hospital Setting","emergency_fees")


	elif i.get('service')=='طلب أستشاري':	
		# i['rate']=frappe.db.get_single_value("Hospital Setting","emergency_doctor_fees")
		# service="طلب أستشاري"
		i['rate']=i['grand_total']
		service=i.get('service')

	elif i.get('observation'):
		i['rate'] = get_item_price(i['observation'])
		service=i['observation']

	else:
		service=i.get('service')
		i['rate']=i['grand_total']


	if i['rate'] is None or not service:
		frappe.throw(str("لا يوجد سعر للبند"))

	rate_before_discount = float(i['rate'])
	# frappe.throw(str(i['rate']))
	if percentage:
		i['rate'] = float(i['rate']) * float(percentage) / 100

	if not i.get("reference_name"):
		i['reference_name'] = None
	if not i.get("reference_type"):
		i['reference_type'] = None
	if i.get("income_account"):
		income_account = i['income_account']

	amount=qty*i['rate']
	item_dict={

		"reference_dn": i['reference_name'],
		"reference_dt": i['reference_type'],
		"item_name": service,
		"rate": i['rate'],
		"qty": qty,
		"income_account": income_account,
		"amount":amount,
	}
	return [item_dict,amount,rate_before_discount]




def make_doctor_entry(doctor,patient_encounter=None,inpatient_record=None,
					  sales_invoice=None,items=None,reservation_type=None,grand_total=0,doctor_discount=0,
					  total_ratio=1,paper_receipt=None,posting_date=None,total_before_discount=0):
	doc = frappe.new_doc("Doctor Entry")

	# if patient_encounter:
	# 	doc.patient_encounter = patient_encounter
	# 	patient_encounter = frappe.get_doc("Patient Encounter",patient_encounter)
	# 	reservation_type=patient_encounter.reservation_type
	
	# if inpatient_recorder:
	# 	doc.inpatient_recorder = inpatient_recorder
	# 	inpatient_recorder = frappe.get_doc("Inpatient Record",inpatient_recorder)
	total=0
	if reservation_type in ["Clinical Procedure","Dental"] and patient_encounter:
		for i in items:
			try:
				i=i.as_dict()
			except Exception:
				i=i
			item_name=i.get('item_name')or i.get("observation")
			rate=get_item_price(item_name)
			doctor_percentage,cost_percent=get_item_clinical_procedure(item_name,doctor)
			
			set_clinical_procedure_cost(item_name,cost_percent,rate,
								total_ratio,sales_invoice=sales_invoice,inpatient_record=inpatient_record,patient_encounter=patient_encounter,healthcare_practitioner=doctor)
			# frappe.throw(str(f"{rate}...{doctor_percentage}....{total_ratio}"))
			total+=rate*doctor_percentage/100*total_ratio
	# frappe.throw(str(total))	
	if reservation_type =="Clinics" and patient_encounter :
		# frappe.msgprint(str(patient_encounter))
		is_consulting = frappe.db.get_value("Patient Encounter",patient_encounter,"is_consulting")

		rate= grand_total
		# if doctor_discount:
		# 	rate=total_before_discount
		
		total,doctor_ratio=get_doctor_profit(is_consulting,rate,doctor)

	elif reservation_type =="Request Doctor" :
		rate=grand_total	
		request_doctor_amount,request_doctor_percent= frappe.db.sql(f"select request_doctor_amount,request_doctor_percent from`tabMedical Staff Fees Details` where healthcare_practitioner='{doctor}' ",as_list=1)[0]
		total=(rate*request_doctor_percent/100) or request_doctor_amount
		
	elif reservation_type == "Clinical Procedure" and inpatient_record:
		
		for i in items:
			try:
				i=i.as_dict()
			except Exception:
				i=i
			doctor_percentage= frappe.db.sql(f"""select doctor_percentage from`tabEmergency Fees Details`
											where item='{i['item_name']}' """,as_list=1)
			if doctor_percentage:
				total+=(doctor_percentage[0][0]/100)*i["rate"]*i["qty"]

	# frappe.throw(str(total))
	if doctor_discount:
		# frappe.throw(str(total))
		# total=total-(total*doctor_discount/100)
		# doctor_discount=doctor_discount/100
		# discount_rate=doctor_discount*doctor_ratio*total_before_discount
		# total=((grand_total+discount_rate)*doctor_ratio)-discount_rate
		total=total*doctor_discount/100
	doc.patient_encounter = patient_encounter

	doc.doctor = doctor
	doc.department = reservation_type 
	doc.amount = total
	doc.sales_invoice=sales_invoice
	doc.grand_total = grand_total
	doc.inpatient_record=inpatient_record
	# doc.department = department
	# doc.percentage = percentage
	doc.paper_receipt=paper_receipt
	doc.posting_date=posting_date
	# frappe.throw(str(total))
	if total > 0:
		doc.submit()




def get_item_clinical_procedure(item,doctor):
	percentage=cost_percent=0
	result=frappe.db.sql(f"select clinical_procedure,cost_percent from `tabClinical Procedure Name` where clinical_procedure='{item}' and parent='Clinical Procedure Fees'",as_list=1)
	if result:
		clinical_procedure,cost_percent=result[0]

		doctor_percentage=frappe.db.sql(f"select doctor_percentage from `tabClinical Procedure Fees Details` where doctor='{doctor}' and parent='Clinical Procedure Fees'",as_list=1)
		if doctor_percentage:
			percentage=doctor_percentage[0][0]-cost_percent
		# if cost_percent:
	return  [percentage,cost_percent]


def set_clinical_procedure_cost(clinical_procedure,cost_percent,rate,
								total_ratio,sales_invoice=None,inpatient_record=None,patient_encounter=None,healthcare_practitioner=None):
	amount=rate*cost_percent/100*total_ratio

	doc = frappe.new_doc("Clinical Procedure Cost")
	doc.clinical_procedure=clinical_procedure
	doc.percentage=cost_percent
	doc.rate=rate
	doc.ratio=total_ratio
	doc.amount=amount
	doc.sales_invoice=sales_invoice
	doc.inpatient_record=inpatient_record
	doc.patient_encounter=patient_encounter
	doc.healthcare_practitioner=healthcare_practitioner

	doc.save(ignore_permissions=True)



@frappe.whitelist()
def get_doctor_profit(is_consulting,rate,doctor):
	rate=float(rate)
	is_consulting=int(is_consulting)

	if not is_consulting:
		clinic_amount,clinic_percent= frappe.db.sql(f"""
				select clinic_amount,clinic_percent from`tabMedical Staff Fees Details` where 
				healthcare_practitioner='{doctor}' """,as_list=1)[0]

		# total=(rate*clinic_percent/100) or clinic_amount
			# frappe.throw("Not consulting")
	else:
		clinic_amount, clinic_percent = frappe.db.sql(
			f"select consultation_amount,consultation_percent "
			f"from`tabMedical Staff Fees Details` where healthcare_practitioner='{doctor}' ",
			as_list=1)[0]
		# total = (rate * clinic_percent/100) or clinic_amount
	
	ratio=(clinic_percent/100) or clinic_amount
	
	total = rate * ratio

	return [total,ratio]




def set_return_doctor_entry(doc_entry):
	doctor_entry=frappe.new_doc("Doctor Entry")
	copy_doc_no_ct(doc_entry,doctor_entry)
	doctor_entry.amount = doctor_entry.amount * -1
	doctor_entry.posting_date=getdate()
	doctor_entry.is_return=1
	doctor_entry.return_against=doc_entry.name
	doctor_entry.submit()
	frappe.db.set_value("Doctor Entry",doc_entry.name,"has_return",1)

	

def get_treasury_account_by_ip(ip):
	treasury=frappe.db.sql(f"""Select TD.parent as treasury_unit,TA.account,TA.currency from`tabTreasury IP Details`TD,`tabTreasury Account`TA 
				 where parenttype='Treasury Unit' and ip='{ip}' and TA.treasury=TD.parent """,as_dict=1)
	if treasury:
		return treasury[0]
	return None