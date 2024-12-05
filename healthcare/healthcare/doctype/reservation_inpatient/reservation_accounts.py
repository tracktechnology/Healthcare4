import frappe
from frappe.utils import add_days, getdate
import copy


def make_payment(patient, insurance_company=None, percentage=None,company_percentage=None,hospital_percentage=None ,is_healthcare_insurance=False, patient_encounter=None,paper_receipt=None,is_consultation=None,doctor=None,paid_amount=0,items=None,total=0):
	# if total:
	# 	check_min_payment(paid_amount,total)
	invoice_item =  copy.deepcopy(items)
	# frappe.throw(str(percentage))
	if percentage > 0  or not is_healthcare_insurance:
		invoice_item, reference_dt = set_sales_invoice(patient=patient, percentage=percentage, patient_encounter=patient_encounter,paper_receipt=paper_receipt,is_consultation=is_consultation,doctor=doctor,paid_amount=paid_amount,items=invoice_item,is_healthcare_insurance=is_healthcare_insurance)
	else:
		reference_dt = None
	if is_healthcare_insurance:
		insurance_company_percent = float(company_percentage)
		hospital_percentage = float(hospital_percentage)

		if insurance_company_percent:
			set_insurance_company_sales_invoice(patient=patient, reference_dt=reference_dt, insurance_company=insurance_company, percentage=insurance_company_percent, patient_encounter=patient_encounter,paper_receipt=paper_receipt,is_consultation=is_consultation,doctor=doctor,paid_amount=paid_amount,items=items)
		if hospital_percentage:
			set_contract_invoice(insurance_company=insurance_company,percentage=float(hospital_percentage),items=items, patient_encounter=patient_encounter)


	# frappe.msgprint(str("تم الحجز بنجاح"))
	return invoice_item


def set_sales_invoice(patient, company="Track INT'l Trad (Demo)", insurance_company=None, percentage=None, items=None,
					  reference_dt=None, patient_encounter=None,paper_receipt=None,is_consultation=0,doctor=None,paid_amount=0,is_healthcare_insurance=0):
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
			i['grand_total']=i['rate']
			# if is_consultation=='1' :
			# 	service="أستشارة"
			# paid_amount = i['rate']
			percentage=0  #percentage set in reservation doc that is execption for this service
			item,rate,rate_before_discount=get_item(i,percentage)


		else:
			item,rate,rate_before_discount=get_item(i,percentage)
			
		doc.append("items",item)
		
		total+=rate
		total_before_discount+=rate_before_discount



		invoices.append({
			"service": service,
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
	# doc.paper_receipt=paper_receipt
	
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
	return [invoices, doc.name]



def set_contract_invoice(insurance_company,percentage,items,patient_encounter):
	doc=frappe.new_doc("Contract Invoice")
	doc.company_percentage=percentage
	doc.medical_insurance=insurance_company
	total = 0
	total_before_discount = 0
	for i in items:
		item,rate,rate_before_discount=get_item(i,percentage)
		total+=rate
		total_before_discount+=rate_before_discount
		doc.append("items",item)
	doc.grand_total = total_before_discount
	doc.total =total
	doc.patient_encounter = patient_encounter
	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)


	
def set_payment_entry(invoice):

	doc = frappe.new_doc("Payment Entry")
	doc.party_type = "Customer"
	doc.party = invoice.customer
	doc.mode_of_payment = "Cash"
	doc.payment_type = "Receive"
	doc.paid_amount = invoice.paid
	doc.received_amount = invoice.grand_total
	doc.target_exchange_rate = 1
	doc.paid_from = invoice.debit_to
	doc.paid_to = "1110 - Cash - TITD"
	doc.party_account = invoice.debit_to

	doc.paid_to_account_type = "Cash"
	doc.patient_encounter = invoice.patient_encounter
	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)

	doc.submit()
	return True






def get_item_price(item):
	return frappe.db.get_value("Item Price", {"item_code": item, "price_list": "Standard Selling"}, ['price_list_rate'])



def get_doctor_fees(doctor,is_consultation):
	field="out_patient_booking_charge"
	if  is_consultation:
		field="op_consulting_charge"
	# frappe.throw(is_consultation)
	return  frappe.db.get_value("Healthcare Practitioner", {"name": doctor}, [field])



def print_receipt(invoice_items, doctor_name, patient_name, service_type, medical_dep, company_insurance=None,
				  insurane_percentage=None):
	template = "healthcare/healthcare/doctype/reservation/template.html"
	base_template_path = "healthcare/healthcare/doctype/reservation/print_preview.html"
	items = []
	# invoice_items = []
	# frappe.msgprint(str(invoice_items))
	total = 0.0
	for item in invoice_items:
		item_print = {
			"item_name": item.get("service"),
			"paid": item.get("print_rate"),
			"item_price": item.get("rate")
		}
		items.append(item_print)
		total += item.get("print_rate")
	current_time = frappe.utils.now_datetime()
	formatted_time = current_time.strftime(" %H:%M")
	from frappe.www.printview import get_letter_head
	html = frappe.render_template(template, {
		"patient_name": patient_name,
		"service_type": service_type,
		# "items": items,
		"total": total,
		"date": getdate(),
		"time": formatted_time,
		"medical_department": medical_dep,
		"doctor_name": get_doctor_title(doctor_name),
		"company_insurance": company_insurance,
		"insurane_percentage": insurane_percentage,
		"patient_code":get_patient_code(patient_name),
		"items":items
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






def set_insurance_company_sales_invoice(patient, company="Track INT'l Trad (Demo)", insurance_company=None, percentage=None, items=None,
					  reference_dt=None, patient_encounter=None,
					  paper_receipt=None,is_consultation=0,doctor=None,paid_amount=0,inpatient_record=None):
	invoices = []
	total = 0
	doc = frappe.new_doc("Sales Invoice")
	total_before_discount = 0
	doc.customer = insurance_company

	for i in items:
		item,rate,rate_before_discount=get_item(i,percentage)
		total+=rate
		total_before_discount+=rate_before_discount
		doc.append("items",item)

	doc.hub_manager = "ahmed.khalifa@track-eg.com"
	doc.total_before_discount = total_before_discount
	doc.base_grand_total = total
	doc.reference_dt = reference_dt
	doc.paid_amount=float(total)
	doc.paid=float(total)
	doc.base_paid_amount = float(total)
	doc.patient_encounter = patient_encounter
	doc.inpatient_record=inpatient_record
	doc.due_date = getdate()

	doc.is_medical_insurance=1
	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
	doc.submit()

	set_payment_entry(doc)

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
	qty = 1
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
		i['rate']=frappe.db.get_single_value("Hospital Setting","emergency_doctor_fees")
		service="طلب أستشاري"

	else:
		i['rate'] = get_item_price(i['observation'])
		service=i['observation']
	if i['rate'] is None:
		frappe.throw(str("لا يوجد سعر للبند"))

	rate_before_discount = float(i['rate'])
	if percentage:
		i['rate'] = float(i['rate']) * float(percentage) / 100

	if not i.get("reference_name"):
		i['reference_name'] = None
	if not i.get("reference_type"):
		i['reference_type'] = None
	if i.get("income_account"):
		income_account = i['income_account']
	item_dict={

		"reference_dn": i['reference_name'],
		"reference_dt": i['reference_type'],
		"item_name": service,
		"rate": i['rate'],
		"qty": qty,
		"income_account": income_account,

	}
	return [item_dict,i['rate'],rate_before_discount]

