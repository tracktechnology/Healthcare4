# Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from healthcare.healthcare.doctype.service_request.service_request import make_observation
from healthcare.healthcare.utils import get_healthcare_services_to_invoice
from frappe.utils import add_days, getdate
from frappe.utils import now
from erpnext.controllers.mylogger import log_message

from frappe.model.mapper import get_mapped_doc


class Reservation(Document):
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
    def get_total_lab(self):
        return get_total(self.laboratory)

    @frappe.whitelist()
    def get_total_clinical_procedure(self):
        return get_total(self.clinical_procedure)

    @frappe.whitelist()
    def get_total_imaging(self):
        return get_total(self.imaging)

    @frappe.whitelist()
    def set_lab_reservation(self):
        patient_encounter = set_observation_patient_encounter(self.laboratory_patient, self.lab_doctor,
                                                              self.lab_department, self.laboratory, "Laboratory")
        items = make_payment(self.laboratory_patient, self.insurance_company_lab, self.percentage_lab,
                             self.health_insurance_lab, patient_encounter)
        return print_receipt(items, self.lab_doctor, self.laboratory_patient, "تحاليل", self.lab_department
                             , self.insurance_company_lab, self.percentage_lab)

    @frappe.whitelist()
    def set_clinical_procedure_reservation(self):
        patient_encounter = set_observation_patient_encounter(self.clinical_procedure_patient_name,
                                                              self.clinical_procedure_doctor,
                                                              self.clinical_procedure_department,
                                                              self.clinical_procedure, "Clinical Procedure")
        items = make_payment(self.clinical_procedure_patient_name, self.insurance_company_clinical_procedure,
                             self.percentage_clinical_procedure, self.health_insurance_clinical_procedure,
                             patient_encounter)
        return print_receipt(items, self.clinical_procedure_doctor, self.clinical_procedure_patient_name, "Procedure",
                             self.clinical_procedure_department
                             , self.insurance_company_clinical_procedure, self.percentage_clinical_procedure)

    @frappe.whitelist()
    def set_imaging_reservation(self):
        patient_encounter = set_observation_patient_encounter(self.imaging_patient, self.imaging_doctor,
                                                              self.imaging_department, self.imaging, "Imaging")
        items = make_payment(self.imaging_patient, self.insurance_company_imaging, self.percentage_imaging,
                             self.health_insurance_imaging, patient_encounter)
        return print_receipt(items, self.imaging_doctor, self.imaging_patient, "أشعة", self.imaging_department
                             , self.insurance_company_imaging, self.percentage_imaging)


@frappe.whitelist()
def set_patient_encounter(patient, doctor, medical_department, insurance_company_clinics, percentage_clinics,
                          is_healthcare_insurance):
    if frappe.db.exists('Patient Encounter', {"patient": patient, 'encounter_date': getdate(), "practitioner": doctor}):
        frappe.throw("غير مسموح بتكرار الحجز")

    doc = frappe.new_doc("Patient Encounter")
    doc.patient = patient
    doc.practitioner = doctor
    doc.medical_department = medical_department
    doc.reservation_type = "Clinics"

    doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
    doc.submit()
    items = make_payment(patient, insurance_company_clinics, float(percentage_clinics), int(is_healthcare_insurance),
                         doc.name)
    doc.db_set('invoiced', 1)
    return doc.name, items


@frappe.whitelist()
def set_observation_patient_encounter(patient, doctor, medical_department, list_of_observations, reservation_type):
    doc = frappe.new_doc("Patient Encounter")
    doc.patient = patient
    doc.practitioner = doctor
    doc.medical_department = medical_department
    doc.reservation_type = reservation_type
    if reservation_type == "Clinical Procedure":
        for i in list_of_observations:
            doc.append("procedure_prescription", {"procedure": i.observation})
    else:
        for i in list_of_observations:
            doc.append("lab_test_prescription", {"observation_template": i.observation})
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
def create_new_patient(patient_name, mobile, dob, gender, uid):
    doc = frappe.new_doc("Patient")
    doc.first_name = patient_name
    doc.full_name = patient_name
    doc.mobile = mobile
    doc.dob = dob
    doc.sex = gender
    doc.uid = uid
    doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)


def set_sales_invoice(patient, company="Track INT'l Trad (Demo)", insurance_company=None, percentage=None, items=None,
                      reference_dt=None, patient_encounter=None):
    invoices = []
    total = 0
    rate = 0
    total_before_discount = 0
    if not items:
        items = get_healthcare_services_to_invoice(patient, company)
    doc = frappe.new_doc("Sales Invoice")
    total_before_discount = 0
    for i in items:
        income_account = "4110 - Sales - TITD"
        qty = 1

        if not i.get("rate"):
            i['rate'] = get_item_price(i['service'])

        rate_before_discount = float(i['rate'])
        if percentage:
            i['rate'] = float(i['rate']) * float(percentage) / 100

        if i.get("qty"):
            qty = i['qty']

        if not i.get("reference_name"):
            i['reference_name'] = None
        if not i.get("reference_type"):
            i['reference_type'] = None
        # if i.get("income_account"):
        #     income_account = i['income_account']
        doc.append("items", {

            "reference_dn": i['reference_name'],
            "reference_dt": i['reference_type'],
            "item_name": i['service'],
            "rate": i['rate'],
            "qty": qty,
            "income_account": income_account

        })
        invoices.append({
            "service": i['service'],
            "rate": rate_before_discount,
            "print_rate": i['rate']
        })
        total += i['rate']
        total_before_discount += rate_before_discount

    if not insurance_company:
        doc.patient = patient
        doc.customer = patient
    else:
        insurance_company_name = frappe.db.get_value("Medical insurance company", insurance_company, "company_name")
        doc.customer = insurance_company_name
    # frappe.throw(str(doc.customer))

    doc.hub_manager = "ahmed.khalifa@track-eg.com"
    doc.total_before_discount = total_before_discount
    doc.base_grand_total = total
    doc.grand_total = total
    doc.reference_dt = reference_dt
    doc.patient_encounter = patient_encounter
    doc.posting_date = frappe.db.get_value("Patient Encounter",patient,"encounter_date")
    doc.posting_time = frappe.db.get_value("Patient Encounter",patient,"encounter_time")

    doc.due_date = doc.posting_date
    # doc.set_missing_values()
    log_message(patient_encounter)
    doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
    doc.submit()
    if doc.grand_total != 0 and not insurance_company:
        set_payment_entry(doc)

    invoices_status = "Paid"
    outstanding_amount = 0
    if insurance_company:
        invoices_status = "Unpaid"
        outstanding_amount = doc.grand_total

    doc.db_set('outstanding_amount', outstanding_amount)
    doc.db_set('status', invoices_status)
    return [invoices, doc.name]


def get_insurance_company(insurance_company):
    doc = frappe.get_doc("Medical insurance company", {"name": insurance_company})
    return doc.company_name


def get_item_price(item):
    return frappe.db.get_value("Item Price", {"item_code": item, "price_list": "Standard Selling"}, ['price_list_rate'])


def set_payment_entry(invoice):
    doc = frappe.new_doc("Payment Entry")
    doc.party_type = "Customer"
    doc.party = invoice.customer
    doc.mode_of_payment = "Cash"
    doc.payment_type = "Receive"
    doc.paid_amount = invoice.grand_total
    doc.received_amount = invoice.grand_total
    doc.target_exchange_rate = 1
    doc.paid_from = invoice.debit_to
    doc.paid_to = "1110 - Cash - TITD"
    doc.party_account = invoice.debit_to
    doc.posting_date = invoice.posting_date
    doc.posting_time = invoice.posting_time

    doc.paid_to_account_type = "Cash"
    doc.patient_encounter = invoice.patient_encounter
    doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)

    doc.submit()
    return True


@frappe.whitelist()
def get_total(items):
    items_list = [""]
    for i in items:
        items_list.append(i.observation)
    items = tuple(items_list)
    res = frappe.db.sql(f"""SELECT SUM(price_list_rate) FROM `tabItem Price` where item_code IN {items} """, as_list=1)
    return res[0][0]


def make_payment(patient, insurance_company, percentage=None, is_healthcare_insurance=False, patient_encounter=None):
    items, reference_dt = set_sales_invoice(patient=patient, percentage=percentage, patient_encounter=patient_encounter)
    if is_healthcare_insurance:
        insurance_company_percent = 100 - float(percentage)
        set_sales_invoice(patient=patient, insurance_company=insurance_company, percentage=insurance_company_percent,
                          items=items, reference_dt=reference_dt, patient_encounter=patient_encounter)
    # frappe.msgprint(str("تم الحجز بنجاح"))
    return items


@frappe.whitelist()
def get_medical_insurance_percent(insurance_company, department):
    percent = frappe.db.sql(
        f"select percentage  from `tabMedical insurance company details` where parent='{insurance_company}' and department='{department}'",
        as_list=1)
    try:
        return percent[0][0]
    except:
        # frappe.msgprint("Not found")
        return 0


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
                    insurance_company_clinics, percentage_clinics, is_healthcare_insurance):
    patient_encounter, invoice_items = set_patient_encounter(patient, practitioner, medical_department,
                                                             insurance_company_clinics, percentage_clinics,
                                                             is_healthcare_insurance)
    set_patient_appointment(patient_encounter, appointment_time, patient, date, paid_amount, practitioner,
                            medical_department, service_unit)
    # return print_receipt(invoice_items,patient,"Clinic")
    return print_receipt(invoice_items, doctor_name=practitioner, patient_name=patient, service_type="كشف",
                         medical_dep=medical_department, company_insurance=insurance_company_clinics,
                         insurane_percentage=percentage_clinics)


def set_patient_appointment(patient_encounter, appointment_time, patient, date, paid_amount, practitioner,
                            medical_department, service_unit):
    doc = frappe.new_doc("Patient Appointment")
    doc.patient = patient
    doc.appointment_date = date
    doc.appointment_type = "طوارئ"
    doc.paid_amount = paid_amount
    doc.practitioner = practitioner
    doc.appointment_for = "Practitioner"
    doc.appointment_time = appointment_time
    doc.department = medical_department
    doc.service_unit = service_unit
    doc.appointment_based_on_check_in = 1
    doc.patient_encounter = patient_encounter
    doc.insert(ignore_permissions=True, ignore_links=True)


def get_slot(doctor):
    slots = frappe.db.sql(
        f"select hs.day,from_time,to_time,ps.parent  from `tabPractitioner Service Unit Schedule` ps , `tabHealthcare Schedule Time Slot` hs  where ps.parent ='{doctor}' and ps.schedule=hs.parent and hs.disabled =0  ",
        as_dict=1)
    return slots


# def print_receipt(invoice_items,patient_name,service_type):
# 	template = "healthcare/healthcare/doctype/reservation/template.html"
# 	base_template_path = "healthcare/healthcare/doctype/reservation/print_preview.html"
# 	items = []
# 	# invoice_items = []
# 	# frappe.msgprint(str(invoice_items))
# 	total = 0.0
# 	for item in invoice_items:
# 		item_print = {
# 				  "item_name": item.get("service"),
# 				"item_price": item.get("print_rate")
# 		}
# 		items.append(item_print)
# 		total += item.get("print_rate")

# 	from frappe.www.printview import get_letter_head
# 	html = frappe.render_template(template, {
# 		"patient_name":patient_name,
# 		"type": service_type,
# 		"items": items,
# 		"total": total
# 	})
# 	final_template = frappe.render_template(base_template_path, {"body": html, "title": "Report Card"})

# 	return final_template


def print_receipt(invoice_items, doctor_name, patient_name, service_type, medical_dep, company_insurance,
                  insurane_percentage):
    template = "healthcare/healthcare/doctype/reservation/template.html"
    base_template_path = "healthcare/healthcare/doctype/reservation/print_preview.html"
    items = []
    # invoice_items = []
    # frappe.msgprint(str(invoice_items))
    total = 0.0
    for item in invoice_items:
        item_print = {
            "item_name": item.get("service"),
            "item_price": item.get("print_rate")
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
        "patient_code": get_patient_code(patient_name)
    })
    final_template = frappe.render_template(base_template_path, {"body": html, "title": "Report Card"})

    return final_template


def get_doctor_title(healthcare_practitioner):
    return frappe.db.get_value("Healthcare Practitioner", healthcare_practitioner, 'practitioner_name')


def get_patient_code(patient_name):
    return frappe.db.get_value("Patient", patient_name, 'patient_code')
