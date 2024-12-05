from calendar import prcal

import frappe
from frappe.model.document import Document
from healthcare.healthcare.doctype.service_request.service_request import make_observation
from healthcare.healthcare.utils import get_healthcare_services_to_invoice
from frappe.utils import add_days, getdate,today
from frappe.utils import now
from healthcare.healthcare.doctype.patient_appointment.patient_appointment import update_status
from frappe.model.mapper import get_mapped_doc
from healthcare.healthcare.healthcare_utils import set_observation_request
from healthcare.healthcare.reservation_accounts import make_payment,print_receipt,make_doctor_entry,get_doctor_profit


class Reservation(Document):
	
	@frappe.whitelist()
	def get_patient_dental_procedure(self):
		invoices=frappe.db.sql(f"""SELECT SI.name,SI.invoice_number,grand_total,
						 SI.patient_encounter,outstanding_amount,paid,PE.name as patient_encounter
						  FROM `tabSales Invoice` SI,`tabPatient Encounter` PE WHERE SI.patient_encounter=PE.name
						  and SI.outstanding_amount>=0 and SI.patient='{self.patient}' and 
						  SI.cancel_request =0 and PE.reservation_type='Dental' and 
						  PE.practitioner='{self.doctor}' order by SI.posting_date DESC """,as_dict=True)
		self.reservation_invoices=[]
		# grand_total=paid=outstanding_amount=0
		for invoice in invoices:
			self.append("reservation_invoices",{
					"sales_invoice":invoice.name,
					"grand_total":invoice.grand_total,
					"remaining_amount":invoice.outstanding_amount,
					"paid_amount":invoice.paid,
					"invoice_number":invoice.invoice_number,
					"patient_encounter":invoice.patient_encounter
			})
	@frappe.whitelist()
	def get_dental_ivoice_details(self,sales_invoice):
		self.dental_procedure=[]
		self.payments=[]
		self.reservation_follow_up_details=[]
		invoice=frappe.get_doc("Sales Invoice",sales_invoice)
		follow_up=frappe.db.get_list("Patient Follow Up",filters={"patient_encounter":invoice.patient_encounter},fields=['creation'])
		for i in follow_up:
			self.append("reservation_follow_up_details",{
				"date":i.creation
			})
		
		# grand_total+=invoice.grand_total
		# paid+=invoice.paid
		# outstanding_amount+=invoice.outstanding_amount
		pe=frappe.get_doc("Patient Encounter",invoice.patient_encounter)
		payments=frappe.db.get_list("Payment Entry",filters={"patient_encounter":invoice.patient_encounter,"docstatus":1},fields=['paid_amount','posting_date'])
		
		for i in pe.procedure_prescription:
			self.append("dental_procedure",{
				"observation":i.procedure
			})
		for i in payments:
			self.append("payments",{
				"paid_amount":i.paid_amount,
				'date':i.posting_date,
				'invoice_number':invoice.invoice_number,
				'patient_encounter':invoice.patient_encounter

			})
		# self.dental_total=grand_total
		# self.dental_paid=paid
		# self.dental_remaining=outstanding_amount
		
	@frappe.whitelist()
	def print_request(self,sales_invoice,paper_receipt,paid_amount,date=today()):
		invoice = frappe.get_doc("Sales Invoice",sales_invoice)
		request=frappe.get_doc("Observation Request",{"patient_encounter":invoice.patient_encounter})
		queue = frappe.db.sql(f"""SELECT name,
									ROW_NUMBER() OVER (PARTITION BY DATE(creation) ORDER BY creation) AS row_number
										FROM `tabObservation Request`
										WHERE 
											DATE(creation) = DATE('{request.creation}')
											and observation_category='{request.observation_category}'
										ORDER BY 
											creation """,as_dict=1)
		for i in queue:
			if i.name==request.name:
				queue_number=i.row_number
				break


		patient_percentage=request.patient_percentage
		paid = invoice.outstanding_amount
		print_items = []
		for item in invoice.items:
			print_items.append({
				"item_name": item.get("item_name"),
				"rate": get_item_price(item.get("item_name"))
			})
		pay_invoice(sales_invoice,paper_receipt,paid_amount,date)

		return print_receipt(invoice_items=print_items,doctor_name=request.doctor,patient_name=request.patient,
						patient_percentage=patient_percentage,medical_dep=None,paid=paid_amount,
						total=invoice.grand_total,queue_number=queue_number,
						insurance_company=request.medical_insurance,invoice_number=invoice.invoice_number)


	@frappe.whitelist()
	def get_consulting(self):
		valid_days=frappe.db.get_single_value("Hospital Setting","consulting_days")
		data= frappe.db.sql(f"""select name,encounter_date,got_consulting from `tabPatient Encounter`
					   where patient='{self.patient}' and practitioner='{self.doctor}' and reservation_type='Clinics'
						and docstatus=1 and is_consulting=0 ORDER BY encounter_date DESC,creation DESC LIMIT 1 """
						,as_list=1)
		# return False
		try:
			if data[0][2]==1:
				return False
			delta=getdate()-data[0][1]
			if delta.days < valid_days:
				return data[0][0]
		except:
			# pass
			return False

	def get_zero_invoice_encounters(self):

		zero_invoices = frappe.db.sql(f"""SELECT PE.name,PE.reservation_type
		FROM `tabPatient Encounter` PE
		WHERE PE.patient='{self.request_patient}'
					and PE.reservation_type IN('Imaging','Laboratory') and PE.request_confirmed = 0
					and PE.name not in ( select SI.patient_encounter from `tabSales Invoice` SI where
					  SI.cancel_request =0 
					and SI.patient = '{self.request_patient}'
					and SI.docstatus!=2)  order by PE.encounter_date DESC """, as_list=True)
		# frappe.throw(str(zero_invoices))
		self.zero_invoices = []
		for zinvoice in zero_invoices:
			insurance = get_customer_by_encounter(zinvoice[0])
			hosbital_discount = get_hosbital_discount_type(zinvoice[0])
			self.append("zero_invoices",{
					"patient_encounter":zinvoice[0],
					"reservation_type": zinvoice[1],
					"insurance": insurance,
					"hosbital_discount_type": hosbital_discount
				})

	@frappe.whitelist()
	def get_observation_invoice(self):
		self.request_invoices=[]
		invoices=frappe.db.sql(f"""SELECT SI.name,SI.invoice_number,grand_total,SI.patient_encounter,
			outstanding_amount,paid,PE.name as patient_encounter FROM `tabSales Invoice` SI,
			`tabPatient Encounter` PE WHERE   SI.patient_encounter=PE.name and SI.outstanding_amount>0
			and SI.patient='{self.request_patient}' and SI.cancel_request =0 and PE.reservation_type IN('Imaging','Laboratory')
			and SI.docstatus!=2  order by SI.posting_date DESC """,as_dict=True)


		for invoice in invoices:
			self.append("request_invoices",{
					"sales_invoice":invoice.name,
					"grand_total":invoice.grand_total,
					"remaining_amount":invoice.outstanding_amount,
					"paid_amount":invoice.paid,
					"invoice_number":invoice.invoice_number,
					"patient_encounter":invoice.patient_encounter
				})
		self.get_zero_invoice_encounters()
		

	@frappe.whitelist()
	def get_appointment_details(self, doctor=False, department=False):
		self.appointment_details = None
		if doctor:
			slots = get_slot(self.doctor)
			for i in slots:
				self.append_to_appointment_details(i.parent, i.from_time, i.to_time, i.day)

		if department:

			doctors = frappe.get_all('Healthcare Practitioner', filters={"department": self.medical_department})
			for i in doctors:

				slots = get_slot(i.name)
				for j in slots:
					self.append_to_appointment_details(j.parent, j.from_time, j.to_time, j.day)
		if not self.appointment_details:
			frappe.msgprint("Not Found Appointment")

	def append_to_appointment_details(self, doctor, from_time, to_time, day):
		self.append('appointment_details', {
			'doctor': doctor,
			'from_time': from_time,
			'to_time': to_time,
			'day': day,
		})

	
		

	@frappe.whitelist()
	def set_lab_reservation(self):
		if not self.patient:
			frappe.throw(str("Please enter Patient Name"))
		self.check_previous_observation("Laboratory")
		set_observation_request(self.patient,"Laboratory",self.medical_department,self.doctor,
						  self.percentage,self.company_percentage,reservation_type="Outpatient",
						  medical_insurance=self.medical_insurance,
						  hospital_percentage=self.hospital_percentage,observation_date=self.reservation_date)
		return True

	@frappe.whitelist()
	def set_imaging_reservation(self):
		if not self.patient:
			frappe.throw(str("Please enter Patient Name"))
		self.check_previous_observation("Imaging")		
		if not self.imaging_type:
			frappe.throw(str("برجاء ادخال نوع الاشعة"))
		set_observation_request(self.patient,"Imaging",self.medical_department,self.doctor,
						  self.percentage,self.company_percentage,self.imaging_type,reservation_type="Outpatient",
						  medical_insurance=self.medical_insurance,
						  hospital_percentage=self.hospital_percentage,observation_date=self.reservation_date)
		return True


	@frappe.whitelist()
	def check_previous_observation(self,observation_category):
		data=frappe.db.sql(f"""select name from `tabObservation Request` where patient='{self.patient}'
				    and status!='Pending' and observation_category='{observation_category}' 
						and ((remaining_amount-total)/total*100)<60 and remaining_amount >0 """)

		if data:
			frappe.throw(str("الرجاء دفع على الأقل 60% من قيمة الطلب السابق "))

	@frappe.whitelist()
	def pay_observation(self):
		frappe.throw(str(getattr(self, "observation_request")))
	@frappe.whitelist()
	def set_clinical_procedure_reservation(self,paper_receipt,paid_amount):

		if not self.patient:
			frappe.throw(str("Please enter Patient Name"))
		queue_number=get_doctor_queue_number(self.doctor,self.reservation_date)

		patient_encounter = set_observation_patient_encounter(self.patient,
													self.doctor,
													self.medical_department,
													self.clinical_procedure, "Clinical Procedure",
													self.encounter_id,self.reservation_date,self.doctor_percentage)
		invoice_item,invoice_number,invoice_name=make_payment(patient=self.patient, 
					insurance_company=self.medical_insurance,
				percentage=self.percentage,company_percentage=self.company_percentage,hospital_percentage=self.hospital_percentage,
				is_healthcare_insurance=self.health_insurance, patient_encounter=patient_encounter,
				doctor=self.doctor,items=self.clinical_procedure,posting_date=self.reservation_date)
		if not self.percentage and self.health_insurance :
			make_doctor_entry(doctor=self.doctor,patient_encounter=patient_encounter,doctor_discount=self.doctor_percentage,
							reservation_type="Clinical Procedure",items=self.clinical_procedure,
							grand_total=float(self.grand_total),
							posting_date=self.reservation_date)
		procedures_items = get_procedure_items(self.clinical_procedure)
		print_items = get_print_items(procedures_items)

		pay_invoice(invoice_name,paper_receipt,paid_amount,self.reservation_date)
		return print_receipt(invoice_items=print_items,doctor_name=self.doctor,
					   patient_name=self.patient,
					   patient_percentage=self.percentage,
					   medical_dep=self.medical_department,paid=paid_amount,total=self.grand_total,
					   insurance_company=self.medical_insurance,
					   invoice_number=invoice_number,queue_number=queue_number)
	
	
	@frappe.whitelist()
	def set_dental_procedure_reservation(self,paper_receipt,paid_amount):

		if not self.patient:
			frappe.throw(str("Please enter Patient Name"))
		if not self.doctor:
			frappe.throw(str("Please enter Doctor Name"))
		queue_number=get_doctor_queue_number(self.doctor,self.reservation_date)
		patient_encounter = set_observation_patient_encounter(self.patient,
																self.doctor,
															  'أسنان',
															  self.dental_procedure, "Dental",self.encounter_id,self.reservation_date)
		items,invoice_number,invoice_name=make_payment(patient=self.patient, insurance_company=self.medical_insurance,
				percentage=self.percentage,company_percentage=self.company_percentage,
				hospital_percentage=self.hospital_percentage,
				is_healthcare_insurance=self.health_insurance, patient_encounter=patient_encounter,
				doctor=self.doctor,items=self.dental_procedure,posting_date=self.reservation_date)
		# if not self.percentage_dental and self.health_insurance_dental :
		# 	make_doctor_entry(doctor=self.dental_doctor,patient_encounter=patient_encounter,doctor_discount=self.doctor_percentage_clinical_procedure,
		# 					reservation_type="Clinical Procedure",items=self.clinical_procedure,grand_total=float(self.clinical_procedure_grand_total))
		procedures_items = get_procedure_items(self.dental_procedure)
		print_items = get_print_items(procedures_items)
		pay_invoice(invoice_name,paper_receipt,paid_amount,self.reservation_date)
	
		return print_receipt(invoice_items=print_items,doctor_name=self.doctor,
					   patient_name=self.patient,
					   patient_percentage=self.percentage,
					   medical_dep="اسنان",paid=self.request_paid_amount,total=self.grand_total,
					   insurance_company=self.medical_insurance,
					   invoice_number=invoice_number,queue_number=queue_number)
	
	@frappe.whitelist()
	def set_patient_follow_up(self,patient_encounter,paid_amount,paper_receipt,sales_invoice):
		queue_number=get_doctor_queue_number(self.doctor,today())

		doc=frappe.new_doc("Patient Follow Up")
		doc.patient=self.patient
		doc.patient_encounter=patient_encounter
		doc.doctor=self.doctor
		doc.save()
		items=[]
		invoice=frappe.get_doc("Sales Invoice",{"patient_encounter":patient_encounter})
		pay_invoice(sales_invoice,paper_receipt,paid_amount,self.reservation_date)

		return print_receipt(invoice_items=invoice.items,doctor_name=self.doctor,patient_name=self.patient,
					patient_percentage=self.percentage,medical_dep=self.medical_department,
					paid=paid_amount,
					total=invoice.grand_total,queue_number=queue_number,
					# insurance_company=medical_insurance,
					invoice_number=invoice.invoice_number)


	@frappe.whitelist()
	def get_patient_invoices(self):
		self.reservations=[]
		# invoices= frappe.get_list("Sales Invoice",{"patient":self.patient,"status":"Draft"},["name","grand_total"])
		invoices=frappe.db.sql(f"""SELECT P.paper_receipt,SI.name,grand_total,reservation_type,PE.medical_department,SI.patient_encounter
				FROM `tabSales Invoice` SI,`tabPatient Encounter` PE,`tabPayment Entry` P 
				WHERE P.patient_encounter=PE.name and  SI.patient_encounter=PE.name and SI.paid>0 
				and SI.patient='{self.cancel_patient}' and SI.cancel_request =0 and SI.posting_date = '{today()}' """,as_dict=True)

		for invoice in invoices:
			# paper_receipts=frappe.db.sql(f"select paper_receipt from `tabPayment Entry`  where patient_encounter='{invoice.patient_encounter}'",as_list=True)
			self.append('reservations', {
				'sales_invoice': invoice.name,
				'total':invoice.grand_total,
				'reservation_type':invoice.reservation_type,
				'paper_receipt':invoice.paper_receipt,
				'medical_department':invoice.medical_department
			})
		
		draft_invoices=frappe.db.sql(f"SELECT SI.name,grand_total,reservation_type,SI.paper_receipt,PE.medical_department FROM `tabSales Invoice` SI,`tabPatient Encounter` PE WHERE SI.patient_encounter=PE.name and SI.status='Draft' and SI.patient='{self.cancel_patient}'  and SI.posting_date = '{today()}' ",as_dict=True)

		for invoice in draft_invoices:
			self.append('invoices', {
				'sales_invoice': invoice.name,
				'total':invoice.grand_total,
				'reservation_type':invoice.reservation_type,
				'paper_receipt':invoice.paper_receipt,
				'medical_department':invoice.medical_department
			})
	@frappe.whitelist()
	def cancel_reservation(self,items):
		for i in items:
			frappe.db.set_value("Payment Entry",{"paper_receipt":i['paper_receipt']},"cancel_request",1)
		return  True
	@frappe.whitelist()
	def delete_invoices(self,items):
		for i in items:
			doc=frappe.get_doc("Sales Invoice",i['sales_invoice'])
			doc.delete() 
			
			patient_encounter = frappe.get_doc("Patient Encounter",doc.patient_encounter)
			patient_encounter.cancel()	
			frappe.db.set_value("Patient Encounter",patient_encounter.reservation,"got_consulting",0)

			if frappe.db.exists("Patient Appointment",{"patient_encounter":patient_encounter.name}):
				patient_appointment = frappe.get_doc("Patient Appointment",{"patient_encounter":patient_encounter.name})
				update_status(patient_appointment.name,"Cancelled")



@frappe.whitelist()
def set_patient_encounter(patient, doctor, medical_department,is_consultation,patient_encounter,
						  cancel_doctor_fees,doctor_percentage_clinics,encounter_id,encounter_date):
	# if frappe.db.exists('Patient Encounter',{"patient":patient,'encounter_date':getdate(),
	# 									  "practitioner":doctor,"docstatus":1,"reservation_type":"Clinics"}):
	# 	frappe.throw("غير مسموح بتكرار الحجز")

	doc = frappe.new_doc("Patient Encounter")
	doc.patient = patient
	doc.practitioner = doctor
	doc.cancel_doctor_fees=cancel_doctor_fees
	doc.medical_department = medical_department
	doc.doctor_discount=doctor_percentage_clinics
	doc.reservation_type = "Clinics"
	doc.encounter_id=encounter_id
	doc.encounter_date=encounter_date
	if is_consultation: 
		doc.is_consulting=is_consultation
		doc.reservation = patient_encounter
		frappe.db.set_value("Patient Encounter",patient_encounter,"got_consulting",1)


	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
	doc.submit()
	# items = make_payment(patient, insurance_company_clinics, float(percentage_clinics),float(company_percentage_clinics), int(is_healthcare_insurance),
	# 					 doc.name,paper_receipt,is_consultation,doctor)

	doc.db_set('invoiced', 1)
	return doc.name

@frappe.whitelist()
def set_observation_patient_encounter(patient, doctor, medical_department, list_of_observations, reservation_type,encounter_id,encounter_date,doctor_discount=0):
	doc = frappe.new_doc("Patient Encounter")
	doc.patient = patient
	doc.practitioner = doctor
	doc.medical_department = medical_department
	doc.reservation_type = reservation_type
	doc.encounter_id=encounter_id
	doc.encounter_date=encounter_date
	doc.doctor_discount=doctor_discount
	if reservation_type in ["Clinical Procedure","Dental"] :
		for i in list_of_observations:
			doc.append("procedure_prescription", {"procedure": i.observation})
	else:
		for i in list_of_observations:
			doc.append("lab_test_prescription", {"observation_template": i})
	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
	
	doc.submit()
	doc.db_set('invoiced', 1)


	service_requests = get_service_request(doc)
	create_observation(service_requests)
	return doc.name

def get_service_request(doc):
	service_request = []
	for i in doc.lab_test_prescription:
		service_request.append(i.service_request)
	return service_request


def create_observation(service_request):
	for i in service_request:
		doc = frappe.get_doc("Service Request", i)
		make_observation(doc)
		submit_observation(i)


def submit_observation(service_request):
	doc = frappe.get_doc("Observation", {"service_request": service_request})
	doc.submit()


@frappe.whitelist()
def create_new_patient(patient_name, mobile, age, gender,uid,address=None):
	doc = frappe.new_doc("Patient")
	doc.first_name = patient_name
	doc.full_name = patient_name
	doc.mobile = mobile
	doc.age_years = age
	doc.sex = gender
	doc.uid = uid
	doc.address = address
	doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)



def get_insurance_company(insurance_company):
	doc = frappe.get_doc("Medical insurance company", {"name": insurance_company})
	return doc.company_name

@frappe.whitelist()
def get_item_price(item):
	return frappe.db.get_value("Item Price", {"item_code": item, "price_list": "Standard Selling"}, ['price_list_rate'])

@frappe.whitelist()
def get_total(items):
	items = list(eval(items))
	items_list = [""]
	for i in items:
		items_list.append(i['observation'])
	items = tuple(items_list)
	res = frappe.db.sql(f"""SELECT SUM(price_list_rate) FROM `tabItem Price` where item_code IN {items} """, as_list=1)
	return res[0][0]


@frappe.whitelist()
def get_practitioner_days(practitioner):
	# import itertools
	days = frappe.db.sql(
		f"select DISTINCT day  from `tabPractitioner Service Unit Schedule` ps , `tabHealthcare Schedule Time Slot` hs  where ps.parent ='{practitioner}' and ps.schedule=hs.parent and hs.disabled =0  ",
		as_list=1)
	# return(list(itertools.chain.from_iterable(days)))
	return days


@frappe.whitelist()
def set_reservation(appointment_time, patient, date, paid_amount, practitioner, medical_department, service_unit,
					medical_insurance, percentage_clinics, company_percentage_clinics,
					hospital_percentage_clinics,is_healthcare_insurance,
					is_consultation,patient_encounter,grand_total,
					cancel_doctor_fees,doctor_percentage_clinics,encounter_id,encounter_date,paper_receipt):
	cancel_doctor_fees=int(cancel_doctor_fees)
	is_consultation=int(is_consultation)
	percentage_clinics=float(percentage_clinics)
	hospital_percentage_clinics=float(hospital_percentage_clinics)
	is_healthcare_insurance=int(is_healthcare_insurance)
	# patient_encounter = set_patient_encounter(patient, practitioner, medical_department,
	# 														 medical_insurance, percentage_clinics,company_percentage_clinics,
	# 														 hospital_percentage_clinics,is_healthcare_insurance,is_consultation,patient_encounter,paid_amount)

	queue_number=get_doctor_queue_number(practitioner,encounter_date)

	patient_encounter=set_patient_encounter(patient, practitioner, medical_department,is_consultation,patient_encounter,cancel_doctor_fees,doctor_percentage_clinics,encounter_id,encounter_date)

	service_type="كشف"
	if is_consultation:
		service_type="أستشارة"

	if cancel_doctor_fees:
		percentage_clinics= float(paid_amount)*100/float(grand_total) 
	if hospital_percentage_clinics:
		percentage_clinics= float(paid_amount)*100/float(grand_total) 

	items=[{"service":service_type,'rate':float(paid_amount),'grand_total':float(grand_total)}]
	
	invoice_item,invoice_number,invoice_name=make_payment(patient=patient, insurance_company=medical_insurance,
			percentage=float(percentage_clinics),company_percentage=float(company_percentage_clinics), 
			hospital_percentage=float(hospital_percentage_clinics),
			is_healthcare_insurance=is_healthcare_insurance, patient_encounter= patient_encounter,
			doctor=practitioner,is_consultation=is_consultation,items=items,posting_date=encounter_date)
	
	if not percentage_clinics  and is_healthcare_insurance:
		make_doctor_entry(doctor=practitioner,patient_encounter=patient_encounter,doctor_discount=float(doctor_percentage_clinics),
							reservation_type="Clinics",items=items,grand_total=float(grand_total),posting_date=encounter_date)
					
	set_patient_appointment(patient_encounter, appointment_time, patient, date, paid_amount, practitioner,
							medical_department, service_unit,is_consultation)
	invoice_item=[{"service":service_type,'rate':float(grand_total)}]

	pay_invoice(invoice_name,paper_receipt,float(paid_amount),encounter_date)

	return print_receipt(invoice_items=invoice_item,doctor_name=practitioner,patient_name=patient,
					  patient_percentage=percentage_clinics,medical_dep=medical_department,paid=float(paid_amount),
					  total=grand_total,queue_number=int(queue_number),
					  insurance_company=medical_insurance,invoice_number=invoice_number)

def set_patient_appointment(patient_encounter, appointment_time, patient, date, paid_amount, practitioner,
							medical_department, service_unit,is_consultation):
	doc = frappe.new_doc("Patient Appointment")
	doc.patient = patient
	doc.appointment_date = date
	# doc.appointment_type = "طوارئ"
	doc.paid_amount = paid_amount
	doc.practitioner = practitioner
	doc.appointment_for = "Practitioner"
	doc.appointment_time = appointment_time
	doc.department = medical_department
	doc.service_unit = service_unit
	doc.appointment_based_on_check_in = 1
	doc.patient_encounter = patient_encounter
	doc.is_consultation=is_consultation
	doc.insert(ignore_permissions=True,ignore_mandatory=True	, ignore_links=True,ignore_if_duplicate=True)


def get_slot(doctor):
	slots = frappe.db.sql(
		f"select hs.day,from_time,to_time,ps.parent  from `tabPractitioner Service Unit Schedule` ps , `tabHealthcare Schedule Time Slot` hs  where ps.parent ='{doctor}' and ps.schedule=hs.parent and hs.disabled =0  ",
		as_dict=1)
	return slots





@frappe.whitelist()
def get_available_slots(day,doctor,is_consultation):
	
	from frappe.utils import  getdate
	if is_consultation=='0':
		max="maximum_appointments"
	else:
		max="maximum_consultation"
	slots = frappe.db.sql(
		f"select {max} as capacity,DATE_FORMAT(from_time, '%H:%i:%s') AS from_time ,DATE_FORMAT(to_time, '%H:%i:%s') AS to_time  from `tabPractitioner Service Unit Schedule` ps , `tabHealthcare Schedule Time Slot` hs  where ps.parent ='{doctor}' and ps.schedule=hs.parent and hs.disabled =0 and hs.day='{day}'  ",
		as_dict=1)
	date=getdate(day)
	for slot in slots:
		appointment= frappe.db.sql(f"select count(name)   from `tabPatient Appointment`  where appointment_date='{date}'  and practitioner='{doctor}' and appointment_time = '{slot['from_time']}' and is_consultation ='{is_consultation}'",as_list=1)
		slot['total_appointment']=appointment[0][0]
		slot['available']=slot['capacity']-slot['total_appointment']
		slot['date']=date
	return slots

def get_doctor_queue_number(doctor,date):
		total_encounters=frappe.db.sql(f"""select  count(name)   from `tabPatient Encounter`  
					where encounter_date='{date}'  and practitioner='{doctor}' and
					  reservation_type in ('Clinical Procedure','Clinics') """,as_list=1)
		follow_ups=frappe.db.sql(f"""SELECT count(name) from`tabPatient Follow Up` 
						where  DATE(creation)='{date}' and doctor='{doctor}'""",as_list=1)
		return total_encounters[0][0]+follow_ups[0][0]+1




def get_queue_no(patient_encounter):
	queue_number = 0
	request = frappe.get_doc("Observation Request", {"patient_encounter": patient_encounter})
	queue = frappe.db.sql(f"""SELECT name,
									ROW_NUMBER() OVER (PARTITION BY DATE(creation) ORDER BY creation) AS row_number
										FROM `tabObservation Request`
										WHERE 
											DATE(creation) = DATE('{request.creation}')
											and observation_category='{request.observation_category}'
										ORDER BY 
											creation """, as_dict=1)
	for i in queue:
		if i.name == request.name:
			queue_number = i.row_number
			break
	return queue_number

@frappe.whitelist()
def print_zero_invoice_request(patient_encounter,insurance=None,medical_discount=None):
	encounter_doc = frappe.get_doc("Patient Encounter",patient_encounter)
	queue_number = get_queue_no(patient_encounter)
	lab_items = get_lab_test_items(encounter_doc.lab_test_prescription)
	print_item = get_print_items(lab_items)
	patient_percentage=0
	encounter_doc.db_set("request_confirmed",1)
	return print_receipt(invoice_items=print_item,doctor_name=encounter_doc.practitioner
						 ,patient_name=encounter_doc.patient,
					  patient_percentage=patient_percentage,medical_dep=None,queue_number=queue_number,
					  insurance_company=insurance or medical_discount,invoice_number=0)



def get_procedure_items(procedures):
	items = []
	testing = ""
	for procedure in procedures:
		items.append(procedure.observation)
	return items

def get_lab_test_items(labs):
	items = []
	testing = ""
	for lab in labs:
		items.append(lab.observation_template)
	return items

def get_print_items(items):
	print_items = []
	for item in items:
		print_items.append({
			"item_name": item,
			"rate": get_item_price(item)
		})
	return print_items

def get_customer_by_encounter(encounter):
	res = frappe.db.sql(f""" select customer 
	from `tabSales Invoice` 
	where patient_encounter = '{encounter}' """, as_list=1)
	if res:
		return res[0][0]
	return " "

def get_hosbital_discount_type(encounter):
	res = frappe.db.sql(f""" select medical_insurance 
	from `tabContract Invoice` 
	where patient_encounter = '{encounter}' """, as_list=1)
	if res:
		return res[0][0]
	return " "




@frappe.whitelist()
def get_doctor_fees(doctor,total,is_consulting):
		total=float(total)
		is_consulting=int(is_consulting)
		# frappe.throw
		# clinic_amount,clinic_percent= frappe.db.sql(f"select clinic_amount,clinic_percent from`tabMedical Staff Fees Details` where healthcare_practitioner='{doctor}' ",as_list=1)[0]
		if is_consulting :
			amount,percent= frappe.db.sql(f"""
					select consultation_amount,consultation_percent from`tabMedical Staff Fees Details`
								  where healthcare_practitioner='{doctor}' """,as_list=1)[0]
		else:
			amount,percent= frappe.db.sql(f"""
			select clinic_amount,clinic_percent from`tabMedical Staff Fees Details` 
								 where healthcare_practitioner='{doctor}' """,as_list=1)[0]
		
		if total*percent/100:
			return total - (total*percent/100)
		return total-amount

@frappe.whitelist()
def get_doctor_charge(doctor):
	doc = frappe.get_doc("Healthcare Practitioner",doctor)
	return [doc.out_patient_booking_charge,doc.op_consulting_charge]



def pay_invoice(invoice_name,paper_receipt,paid_amount,reservation_date):
	if invoice_name:
		payment_receipt=frappe.new_doc("Payment Receipt Tool")
		payment_receipt.pay_invoices(invoice_name,paper_receipt,paid_amount,reservation_date)




