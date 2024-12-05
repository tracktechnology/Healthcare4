# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt


import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, getdate
from healthcare.controllers.stock_utils import make_stock_entry_materail_consumption
from healthcare.healthcare.utils import get_medical_codes


class PatientEncounter(Document):
	def make_stock_entry(self):
		self.make_stock_entry_for_procedures()
		self.make_stock_entry_for_observation()


	def make_stock_entry_for_procedures(self):
		item_doc_type = "Clinical Procedure Template"
		warehouse = frappe.db.get_single_value("Stock Settings","clinc_warehouse")
		for procedure in self.procedure_prescription:
			items_doc_name = procedure.procedure
			stoc_entry_name = make_stock_entry_materail_consumption(item_doc_type,items_doc_name,warehouse)
			if stoc_entry_name:
				frappe.db.set_value("Stock Entry",stoc_entry_name,"patient_encounter",self.name)
				frappe.db.set_value("Stock Entry",stoc_entry_name, "source_name", procedure.procedure)
				frappe.db.set_value("Stock Entry",stoc_entry_name, "source_type", item_doc_type)



	def make_stock_entry_for_observation(self):
		item_doc_type = "Observation Template"
		if self.reservation_type == "Imaging":
			warehouse = frappe.db.get_single_value("Stock Settings","imaging_warehouse")
		elif self.reservation_type == "Laboratory":
			warehouse = frappe.db.get_single_value("Stock Settings","labs_warehouse")
		else: return
		for observation in self.lab_test_prescription:
			# frappe.msgprint(str(observation.as_dict()))
			items_doc_name = observation.observation_template
			stoc_entry_name = make_stock_entry_materail_consumption(item_doc_type,items_doc_name,warehouse)
			if stoc_entry_name:
				frappe.db.set_value("Stock Entry",stoc_entry_name , "patient_encounter", self.name)
				frappe.db.set_value("Stock Entry",stoc_entry_name, "source_name" , observation.observation_template)
				frappe.db.set_value("Stock Entry",stoc_entry_name, "source_type", item_doc_type)



	def validate(self):
		self.set_title()
		self.validate_medications()
		self.validate_therapies()
		self.validate_observations()
		set_codification_table_from_diagnosis(self)
		if not self.is_new() and self.submit_orders_on_save:
			self.make_service_request()
			self.make_medication_request()
			self.status = "Ordered"

	def on_update(self):
		if self.appointment:
			frappe.db.set_value("Patient Appointment", self.appointment, "status", "Closed")
	def before_insert(self):
		self.validate_dulicate()

	def validate_dulicate(self):
		# if self.docstatus==1:
		
		# if frappe.db.exists('Patient Encounter',{'encounter_id':self.encounter_id,'reservation_type':self.reservation_type	}):
		# 	frappe.msgprint("Patient Enconter exists already  ")
		
		from frappe.utils import now,add_to_date
		time_threshold = add_to_date(now(), seconds=-10, as_string=True)
		records = frappe.get_all('Patient Encounter', 
								filters={'creation': ['>=', time_threshold],'reservation_type':self.reservation_type,'patient':self.patient},
								fields=['*'])
		# frappe.throw(str(len(records)==0))
		if records:
			frappe.throw(str("please try again"))
	
	def on_submit(self):
		if self.therapies:
			create_therapy_plan(self)
		self.make_service_request()
		self.make_medication_request()
		# to save service_request name in prescription
		self.save("Update")
		self.db_set("status", "Completed")
		self.make_stock_entry()

	def before_cancel(self):
		orders = frappe.get_all("Service Request", {"order_group": self.name})
		
		observations=frappe.get_all("Observation", {"reference_docname":self.name})
		observation_requests=frappe.get_all("Observation Request", {"patient_encounter":self.name})
		for observation in observations:
			observation_doc = frappe.get_doc("Observation", observation.name)
			if observation_doc.docstatus == 1:
				observation_doc.flags.ignore_links  = True
				observation_doc.cancel()

		for order in orders:
			order_doc = frappe.get_doc("Service Request", order.name)
			if order_doc.docstatus == 1:
				order_doc.cancel()

		
		for request in observation_requests:
			request_doc = frappe.get_doc("Observation Request", request.name)
			if request_doc.docstatus == 1:
				request_doc.flags.ignore_links  = True
				request_doc.cancel()

	def cancel_stock_entries(self):
		stocks = frappe.get_all("Stock Entry", {"patient_encounter": self.name})
		for stock_entry_name in stocks:
			stock_entry = frappe.get_doc("Stock Entry", stock_entry_name.name)
			if stock_entry.docstatus == 1:
				stock_entry.cancel()
			elif stock_entry.docstatus == 0:
				stock_entry.db_set("docstatus","2")

	def cancel_consulting(self):
		if self.is_consulting:
			frappe.db.set_value("Patient Encounter",self.reservation,"got_consulting",0)



	def on_cancel(self):
		self.db_set("status", "Cancelled")

		if self.appointment:
			frappe.db.set_value("Patient Appointment", self.appointment, "status", "Open")

		if self.inpatient_record and self.drug_prescription:
			delete_ip_medication_order(self)
		self.cancel_stock_entries()
		self.cancel_consulting()
	def set_title(self):
		self.title = _("{0} with {1}").format(
			self.patient_name or self.patient, self.practitioner_name or self.practitioner
		)[:100]

	@staticmethod
	@frappe.whitelist()
	def get_applicable_treatment_plans(encounter):
		patient = frappe.get_doc("Patient", encounter["patient"])

		plan_filters = {}
		plan_filters["name"] = ["in", []]

		age = patient.age
		if age:
			plan_filters["patient_age_from"] = ["<=", age.years]
			plan_filters["patient_age_to"] = [">=", age.years]

		gender = patient.sex
		if gender:
			plan_filters["gender"] = ["in", [gender, None]]

		diagnosis = encounter.get("diagnosis")
		if diagnosis:
			diagnosis = [_diagnosis["diagnosis"] for _diagnosis in encounter["diagnosis"]]
			filters = [
				["diagnosis", "in", diagnosis],
				["parenttype", "=", "Treatment Plan Template"],
			]
			diagnosis = frappe.db.get_all("Patient Encounter Diagnosis", filters=filters, fields="*")
			plan_names = [_diagnosis["parent"] for _diagnosis in diagnosis]
			plan_filters["name"][1].extend(plan_names)

		symptoms = encounter.get("symptoms")
		if symptoms:
			symptoms = [symptom["complaint"] for symptom in encounter["symptoms"]]
			filters = [
				["complaint", "in", symptoms],
				["parenttype", "=", "Treatment Plan Template"],
			]
			symptoms = frappe.db.get_all("Patient Encounter Symptom", filters=filters, fields="*")
			plan_names = [symptom["parent"] for symptom in symptoms]
			plan_filters["name"][1].extend(plan_names)

		if not plan_filters["name"][1]:
			plan_filters.pop("name")

		plans = frappe.get_list("Treatment Plan Template", fields="*", filters=plan_filters)

		return plans

	@frappe.whitelist()
	def set_treatment_plans(self, treatment_plans=None):
		for treatment_plan in treatment_plans:
			self.set_treatment_plan(treatment_plan)

	def set_treatment_plan(self, plan):
		plan_doc = frappe.get_doc("Treatment Plan Template", plan)

		for plan_item in plan_doc.items:
			self.set_treatment_plan_item(plan_item)

		for drug in plan_doc.drugs:
			self.append("drug_prescription", (frappe.copy_doc(drug)).as_dict())

	def set_treatment_plan_item(self, plan_item):
		if plan_item.type == "Clinical Procedure Template":
			self.append("procedure_prescription", {"procedure": plan_item.template})

		if plan_item.type == "Lab Test Template":
			self.append("lab_test_prescription", {"lab_test_code": plan_item.template})

		if plan_item.type == "Therapy Type":
			self.append(
				"therapies",
				{"therapy_type": plan_item.template, "no_of_sessions": plan_item.qty},
			)

		if plan_item.type == "Observation Template":
			self.append("lab_test_prescription", {"observation_template": plan_item.template})

	def validate_medications(self):
		if not self.drug_prescription:
			return

		for item in self.drug_prescription:
			if not item.drug_code:
				frappe.throw(_("Row #{0} (Drug Prescription): Drug Code is mandatory").format(item.idx))
			else:
				if not item.medication:
					medication = frappe.db.get_value(
						"Medication Linked Item",
						{"item": item.drug_code},
						"parent",
					)
					if medication:
						item.medication = medication

	def validate_therapies(self):
		if not self.therapies:
			return

		for therapy in self.therapies:
			if therapy.no_of_sessions <= 0:
				frappe.throw(
					_("Row #{0} (Therapies): Number of Sessions should be at least 1").format(therapy.idx)
				)

	def validate_observations(self):
		if not self.lab_test_prescription:
			return

		for observation in self.lab_test_prescription:
			if not observation.observation_template and not observation.lab_test_code:
				frappe.throw(
					_("Row #{0} (Lab Tests): Observation Template or Lab Test Template is mandatory").format(
						observation.idx
					)
				)

	def make_service_request(self):
		if self.lab_test_prescription:
			for lab_test in self.lab_test_prescription:
				if lab_test.observation_template:
					template_doc = "Observation Template"
					template = "observation_template"
				elif lab_test.lab_test_code:
					template_doc = "Lab Test Template"
					template = "lab_test_code"
				else:
					continue
				if not lab_test.service_request:
					lab_template = frappe.get_doc(template_doc, lab_test.get(template))
					order = self.get_order_details(lab_template, lab_test)
					order.insert(ignore_permissions=True, ignore_mandatory=True)
					order.submit()
					lab_test.service_request = order.name

		if self.procedure_prescription:
			for procedure in self.procedure_prescription:
				if not procedure.service_request:
					procedure_template = frappe.get_doc("Clinical Procedure Template", procedure.procedure)
					order = self.get_order_details(procedure_template, procedure)
					order.insert(ignore_permissions=True, ignore_mandatory=True)
					order.submit()
					procedure.service_request = order.name

		if self.therapies:
			for therapy in self.therapies:
				if not therapy.service_request:
					therapy_type = frappe.get_doc("Therapy Type", therapy.therapy_type)
					order = self.get_order_details(therapy_type, therapy)
					order.insert(ignore_permissions=True, ignore_mandatory=True)
					order.submit()
					therapy.service_request = order.name

	def make_medication_request(self):
		if self.drug_prescription:
			# make_medication_request
			for drug in self.drug_prescription:
				if (drug.medication or drug.drug_code) and not drug.medication_request:
					medication = ""
					if drug.medication:
						medication = frappe.get_doc("Medication", drug.medication)
					order = self.get_order_details(medication, drug, True)
					order.insert(ignore_permissions=True, ignore_mandatory=True)
					order.submit()
					drug.medication_request = order.name

	def get_order_details(self, template_doc, line_item, medication_request=False):
		order = frappe.get_doc(
			{
				"doctype": "Medication Request" if medication_request else "Service Request",
				"order_date": self.encounter_date,
				"order_time": self.encounter_time,
				"company": self.company,
				"status": "draft-Medication Request Status" if medication_request else "draft-Request Status",
				"patient": self.get("patient"),
				"practitioner": self.practitioner,
				"source_doc": "Patient Encounter",
				"order_group": self.name,
				"sequence": line_item.get("sequence"),
				"intent": line_item.get("intent"),
				"priority": line_item.get("priority"),
				"quantity": line_item.get_quantity() if line_item.get("doctype") == "Drug Prescription" else 1,
				"dosage": line_item.get("dosage"),
				"dosage_form": line_item.get("dosage_form"),
				"period": line_item.get("period"),
				"expected_date": line_item.get("expected_date"),
				"as_needed": line_item.get("as_needed"),
				"staff_role": template_doc.get("staff_role") if template_doc else "",
				"note": line_item.get("note"),
				"patient_instruction": line_item.get("patient_instruction"),
			}
		)

		description = ""
		if not line_item.get("description"):
			if template_doc:
				if template_doc.get("doctype") == "Lab Test Template":
					description = template_doc.get("lab_test_description")
				else:
					description = template_doc.get("description")
		else:
			description = line_item.get("description")

		if template_doc and template_doc.get("doctype") == "Clinical Procedure Template":
			order.update(
				{
					"referred_to_practitioner": line_item.get("practitioner"),
					"ordered_for": line_item.get("date"),
				}
			)

		if medication_request:
			order.update(
				{
					"medication": template_doc.get("name") if template_doc else "",
					"number_of_repeats_allowed": line_item.get("number_of_repeats_allowed"),
					"medication_item": line_item.get("drug_code") if line_item.get("drug_code") else "",
				}
			)
		else:
			order.update(
				{
					"template_dt": template_doc.get("doctype"),
					"template_dn": template_doc.get("name"),
					# "patient_care_type": line_item.patient_care_type
					# if line_item.patient_care_type
					# else template_doc.get("patient_care_type"),
				}
			)

		order.update({"order_description": description})
		return order

	@frappe.whitelist()
	def add_clinical_note(self, note, note_type=None):
		clinical_note_doc = frappe.new_doc("Clinical Note")
		clinical_note_doc.patient = self.patient
		clinical_note_doc.reference_doc = "Patient Encounter"
		clinical_note_doc.reference_name = self.name
		clinical_note_doc.note = note
		clinical_note_doc.clinical_note_type = note_type
		clinical_note_doc.practitioner = self.practitioner
		clinical_note_doc.insert()

	@frappe.whitelist()
	def edit_clinical_note(self, note, note_name):
		clinical_note_doc = frappe.get_doc("Clinical Note", note_name)
		clinical_note_doc.note = note
		clinical_note_doc.save()

	@frappe.whitelist()
	def delete_clinical_note(self, note_name):
		if frappe.db.exists("Clinical Note", note_name):
			frappe.delete_doc("Clinical Note", note_name)

	@frappe.whitelist()
	def get_clinical_notes(self, patient):
		return frappe.get_all(
			"Clinical Note",
			{
				"patient": patient,
			},
			["posting_date", "note", "name", "practitioner", "user", "clinical_note_type"],
		)

	@frappe.whitelist()
	def get_encounter_details(self):
		medication_requests = []
		service_requests = []
		filters = {"patient": self.patient, "docstatus": 1}
		medication_requests = frappe.get_all("Medication Request", filters, ["*"])
		service_requests = frappe.get_all("Service Request", filters, ["*"])
		for service_request in service_requests:
			if service_request.template_dt == "Lab Test Template":
				lab_test = frappe.db.get_value("Lab Test", {"service_request": service_request.name}, "name")
				if lab_test:
					subject = frappe.db.get_value(
						"Patient Medical Record", {"reference_name": lab_test}, "subject"
					)
					if subject:
						service_request["lab_details"] = subject
		clinical_notes = frappe.get_all(
			"Clinical Note",
			{
				"patient": self.patient,
			},
			["posting_date", "note"],
		)

		return medication_requests, service_requests, clinical_notes


@frappe.whitelist()
def make_ip_medication_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.start_date = source.encounter_date
		for entry in source.drug_prescription:
			if entry.drug_code:
				dosage = frappe.get_doc("Prescription Dosage", entry.dosage)
				dates = get_prescription_dates(entry.period, target.start_date)
				for date in dates:
					for dose in dosage.dosage_strength:
						order = target.append("medication_orders")
						order.drug = entry.drug_code
						order.drug_name = entry.drug_name
						order.dosage = dose.strength
						order.instructions = entry.comment
						order.dosage_form = entry.dosage_form
						order.date = date
						order.time = dose.strength_time
				target.end_date = dates[-1]

	doc = get_mapped_doc(
		"Patient Encounter",
		source_name,
		{
			"Patient Encounter": {
				"doctype": "Inpatient Medication Order",
				"field_map": {
					"name": "patient_encounter",
					"patient": "patient",
					"patient_name": "patient_name",
					"patient_age": "patient_age",
					"inpatient_record": "inpatient_record",
					"practitioner": "practitioner",
					"start_date": "encounter_date",
				},
			}
		},
		target_doc,
		set_missing_values,
	)

	return doc


def get_prescription_dates(period, start_date):
	prescription_duration = frappe.get_doc("Prescription Duration", period)
	days = prescription_duration.get_days()
	dates = [start_date]
	for i in range(1, days):
		dates.append(add_days(getdate(start_date), i))
	return dates


def create_therapy_plan(encounter):
	if len(encounter.therapies):
		doc = frappe.new_doc("Therapy Plan")
		doc.patient = encounter.patient
		doc.start_date = encounter.encounter_date
		for entry in encounter.therapies:
			doc.append(
				"therapy_plan_details",
				{"therapy_type": entry.therapy_type, "no_of_sessions": entry.no_of_sessions},
			)
		doc.save(ignore_permissions=True)
		if doc.get("name"):
			encounter.db_set("therapy_plan", doc.name)
			frappe.msgprint(
				_("Therapy Plan {0} created successfully.").format(frappe.bold(doc.name)), alert=True
			)


def delete_ip_medication_order(encounter):
	record = frappe.db.exists("Inpatient Medication Order", {"patient_encounter": encounter.name})
	if record:
		frappe.delete_doc("Inpatient Medication Order", record, force=1)


def set_codification_table_from_diagnosis(doc):
	if doc.diagnosis and not doc.codification_table:
		for diag in doc.diagnosis:
			medical_code_details = get_medical_codes("Diagnosis", diag.diagnosis)
			if medical_code_details and len(medical_code_details) > 0:
				for m_code in medical_code_details:
					doc.append(
						"codification_table",
						{
							"code_value": m_code.get("code_value"),
							"code_system": m_code.get("code_system"),
							"code": m_code.get("code"),
							"definition": m_code.get("definition"),
							"system": m_code.get("system"),
						},
					)


@frappe.whitelist()
def create_service_request(encounter):
	encounter_doc = frappe.get_doc("Patient Encounter", encounter)
	if not frappe.db.exists("Service Request", {"order_group": encounter}):
		encounter_doc.make_service_request()

		for lab_presc in encounter_doc.lab_test_prescription:
			if lab_presc.invoiced:
				frappe.db.set_value(
					"Service Request",
					{"order_group": encounter, "template_dn": lab_presc.lab_test_code},
					{"docstatus": 1, "invoiced": 1, "status": "active-Request Status"},
				)

		for proc_presc in encounter_doc.procedure_prescription:
			if proc_presc.invoiced:
				frappe.db.set_value(
					"Service Request",
					{"order_group": encounter, "template_dn": proc_presc.procedure},
					{"docstatus": 1, "invoiced": 1, "status": "active-Request Status"},
				)


@frappe.whitelist()
def create_medication_request(encounter):
	encounter_doc = frappe.get_doc("Patient Encounter", encounter)
	if not frappe.db.exists("Medication Request", {"order_group": encounter}):
		encounter_doc.make_medication_request()


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_medications_query(doctype, txt, searchfield, start, page_len, filters):
	medication_name = filters.get("name")
	medication_child = frappe.qb.DocType("Medication Linked Item")
	medication = frappe.qb.DocType("Medication")
	item = frappe.qb.DocType("Item")
	data = (
		frappe.qb.select(medication_child.brand, medication_child.manufacturer, medication_child.item)
		.from_(medication_child)
		.left_join(medication)
		.on(medication.name == medication_child.parent)
		.left_join(item)
		.on(item.name == medication_child.item)
		.where((medication.name == medication_name) & (item.disabled == 0))
	).run(as_dict=True)
	data_list = []
	for d in data:
		display_list = []
		if d.get("item"):
			display_list.append(d.get("item"))
		if d.get("brand"):
			display_list.append(d.get("brand"))
		if d.get("manufacturer"):
			display_list.append(d.get("manufacturer"))
		default_warehouse = frappe.get_cached_value("Stock Settings", None, "default_warehouse")
		if default_warehouse:
			actual_qty = frappe.db.get_value(
				"Bin", {"warehouse": default_warehouse, "item_code": d.get("name")}, "actual_qty"
			)
			display_list.append("Qty:" + str(actual_qty) if actual_qty else "0")
		data_list.append(display_list)
	res = tuple(tuple(sub) for sub in data_list)
	return res


@frappe.whitelist()
def get_medications(medication):
	return frappe.get_all("Medication Linked Item", {"parent": medication}, ["item"])


@frappe.whitelist()
def cancel_request(doctype, request):
	request_doc = frappe.get_doc(doctype, request)
	request_doc.cancel()


@frappe.whitelist()
def create_service_request_from_widget(encounter, data, medication_request=False):
	data = json.loads(data)
	encounter_doc = frappe.get_doc("Patient Encounter", encounter)
	if medication_request:
		template = frappe.get_doc("Medication", data.get("medication"))
		order = encounter_doc.get_order_details(template, data, True)
	else:
		template = frappe.get_doc(data.get("order_template_type"), data.get("order_template"))
		order = encounter_doc.get_order_details(template, data)
	order.insert(ignore_permissions=True, ignore_mandatory=True)
	order.submit()
