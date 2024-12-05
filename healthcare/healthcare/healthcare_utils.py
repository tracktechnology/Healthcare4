import frappe 
from frappe.utils import today

def get_practitioner_full_name(name):
	return frappe.db.get_value("Healthcare Practitioner",name,"practitioner_name")


def update_observation_by_patient_encounter(patient_encounter):
	frappe.db.set_value("Observation Request", {"patient_encounter":patient_encounter}, {"status":"Paid","remaining_amount":0})
	request = frappe.db.exists("Observation Request",{"patient_encounter":patient_encounter})
	if request:
		doc=frappe.get_doc("Observation Request",request)
		if doc.observation_category=="Laboratory":
			create_lab_test(doc)


def create_lab_test(observation_request):
	if not  frappe.db.exists('Lab Test',{"observation_request":observation_request.name}):
		for i in observation_request.observation:
			doc=frappe.new_doc("Lab Test")
			doc.observation_request=observation_request.name
			doc.template=i.observation
			doc.patient=observation_request.patient	
			doc.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)



def create_inpatient(patient,reservation_type):
	doc =frappe.new_doc("Inpatient Record")
	doc.patient=patient
	doc.reservation_type=reservation_type
	doc.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)



def update_item_rate(item_code,rate):
	frappe.db.set_value("Item Price",{"item_code":item_code,"price_list": "Standard Selling"},"price_list_rate",rate)


def create_new_item(item_name,item_group,rate):
	item=frappe.new_doc("Item")
	item.item_name=item_name
	item.item_code=item_name
	item.item_group=item_group
	item.item_group=item_group
	item.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)

	item_price=frappe.new_doc("Item Price")
	item_price.item_code=item_name
	item_price.price_list="Standard Selling"
	item_price.price_list_rate= rate
	item_price.valid_from= today(),
	item_price.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)





def set_observation_request(patient_name,observation_category,medical_department=None,doctor=None,
							patient_percentage=0,company_percentage=0,imaging_type=None,reservation_type=None,medical_insurance=None,
							hospital_percentage=0,observation_date=None):
	doc = frappe.new_doc("Observation Request")
	doc.patient=patient_name
	doc.observation_category=observation_category
	doc.status="Pending"
	doc.doctor=doctor
	doc.medical_department=medical_department
	doc.reservation_type=reservation_type
	doc.company_percentage=company_percentage
	doc.patient_percentage=patient_percentage
	doc.imaging_type=imaging_type
	doc.medical_insurance=medical_insurance
	doc.hospital_percentage=hospital_percentage
	doc.observation_date=observation_date
	doc.insert(ignore_permissions=True, ignore_mandatory=True,ignore_links=True)
	doc.submit()



@frappe.whitelist()
def get_medical_insurance_percent(insurance_company, department,reservation_type=None,medical_department=None):
	medical_department_check=frappe.db.sql(f"select medical_department from `tabMedical insurance company details` where parent='{insurance_company}' and department='{department}' and (reservation_type='{reservation_type}' or reservation_type='ALL' ) and medical_department='{medical_department}' ",as_dict=1)
	if medical_department_check:
		percent = frappe.db.sql(
			f"select patient_percentage,company_percentage,hospital_percentage,doctor_percentage from `tabMedical insurance company details` where parent='{insurance_company}' and department='{department}' and (reservation_type='{reservation_type}' or reservation_type='ALL' ) and medical_department='{medical_department}'",
				as_list=1)
	else:
		percent = frappe.db.sql(
		f"select patient_percentage,company_percentage,hospital_percentage,doctor_percentage from `tabMedical insurance company details` where parent='{insurance_company}' and department='{department}' and (reservation_type='{reservation_type}' or reservation_type='ALL' ) and medical_department IS NULL",
			as_list=1)
	try:
		return [percent[0][0], percent[0][1],percent[0][2],percent[0][3]]
	except:
		# frappe.msgprint("Not found")
		return [0,0,0,0]
	


def get_medical_insurance_room_percent(insurance_company, room_type):
	percent = frappe.db.sql(
		f"select patient_percentage,company_percentage,hospital_percentage from `tabMedical Insurance Company Room Details` where parent='{insurance_company}' and room_type='{room_type}'",
		as_list=1)
	try:
		return [percent[0][0], percent[0][1],percent[0][2]]
	except:
		# frappe.msgprint("Not found")
		return [0,0,0]
	




def get_doctor_emergency_fees(doctor):
	percentage=frappe.db.sql(f"""select doctor_percentage from`tabEmergency Fees Details` 
				 where clinical_procedure='{doctor}'""",as_list=1)
	try:
		return percentage[0][0]
	except:
		return 0


def get_item_price(item,reservation_type=None,price_list="Standard Selling"):
	if reservation_type:
		price_list=frappe.db.get_value("Price List", {"reservation_type":reservation_type},['name'])
	rate=frappe.db.get_value("Item Price", {"item_code": item, "price_list": price_list},
							 ['price_list_rate'])
	if not rate : #if not find item in price list get standard price list 
		rate=frappe.db.get_value("Item Price", {"item_code": item, "price_list": "Standard Selling"},
							 ['price_list_rate'])
	return rate
	




def get_item_practitioner_type(doctor,item=None,item_group=None,reservation_type=None):
	if not doctor:
		return
	practitioner_type=get_practitioner_type(doctor)
	if item: #if fint item get practice type
		type_procedure=frappe.db.get_value("Item", item, ['healthcare_practitioner_type'])
	
	if item_group: #if fint item group get item name 
		# item,type_procedure=frappe.db.get_value("Item",
		# 		{"item_group":item_group,"reservation_type":["in", [reservation_type, "All", None]],
		# 		"healthcare_practitioner_type":practitioner_type},['name','healthcare_practitioner_type'])
		price_list=frappe.db.get_value("Price List",{"reservation_type":reservation_type})
		item,type_procedure=frappe.db.sql(f"""select I.name,I.healthcare_practitioner_type from `tabItem`I,`tabItem Price`IP 
					where item_group='{item_group}'and IP.price_list='{price_list}' and IP.item_code=I.name
					and I.healthcare_practitioner_type='{practitioner_type}'""",as_list=1)[0]
	
	if type_procedure and practitioner_type!=type_procedure:
		frappe.throw(str(f"""هذا الإجراء "{item}" غير مخصص لهذا الطبيب"""))
	return item
def get_practitioner_type(practitioner):
	return frappe.db.get_value("Healthcare Practitioner", practitioner, ['healthcare_practitioner_type'])
