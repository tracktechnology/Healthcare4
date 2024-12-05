# isort: skip_file
import frappe
from erpnext.setup.utils import insert_record
from frappe import _

data = {
	"desktop_icons": [
		"Patient",
		"Patient Appointment",
		"Patient Encounter",
		"Lab Test",
		"Healthcare",
		"Vital Signs",
		"Clinical Procedure",
		"Inpatient Record",
		"Accounts",
		"Buying",
		"Stock",
		"HR",
		"ToDo",
	],
	"default_portal_role": "Patient",
	"restricted_roles": [
		"Healthcare Administrator",
		"LabTest Approver",
		"Laboratory User",
		"Nursing User",
		"Physician",
		"Patient",
	],
	"custom_fields": {
		"Sales Invoice": [
			{
				"fieldname": "patient",
				"label": "Patient",
				"fieldtype": "Link",
				"options": "Patient",
				"insert_after": "naming_series",
			},
			{
				"fieldname": "patient_name",
				"label": "Patient Name",
				"fieldtype": "Data",
				"fetch_from": "patient.patient_name",
				"insert_after": "patient",
				"read_only": True,
			},
			{
				"fieldname": "ref_practitioner",
				"label": "Referring Practitioner",
				"fieldtype": "Link",
				"options": "Healthcare Practitioner",
				"insert_after": "customer",
			},
			{
				"fieldname": "service_unit",
				"label": "Service Unit",
				"fieldtype": "Link",
				"options": "Healthcare Service Unit",
				"insert_after": "customer_name",
			},
		],
		"Sales Invoice Item": [
			{
				"fieldname": "reference_dt",
				"label": "Reference DocType",
				"fieldtype": "Link",
				"options": "DocType",
				"insert_after": "edit_references",
			},
			{
				"fieldname": "reference_dn",
				"label": "Reference Name",
				"fieldtype": "Dynamic Link",
				"options": "reference_dt",
				"insert_after": "reference_dt",
			},
			{
				"fieldname": "practitioner",
				"label": "Practitioner",
				"fieldtype": "Link",
				"options": "Healthcare Practitioner",
				"insert_after": "reference_dn",
				"read_only": True,
			},
			{
				"fieldname": "medical_department",
				"label": "Medical Department",
				"fieldtype": "Link",
				"options": "Medical Department",
				"insert_after": "delivered_qty",
				"read_only": True,
			},
			{
				"fieldname": "service_unit",
				"label": "Service Unit",
				"fieldtype": "Link",
				"options": "Healthcare Service Unit",
				"insert_after": "medical_department",
				"read_only": True,
			},
		],
		"Stock Entry": [
			{
				"fieldname": "inpatient_medication_entry",
				"label": "Inpatient Medication Entry",
				"fieldtype": "Link",
				"options": "Inpatient Medication Entry",
				"insert_after": "credit_note",
				"read_only": True,
			}
		],
		"Stock Entry Detail": [
			{
				"fieldname": "patient",
				"label": "Patient",
				"fieldtype": "Link",
				"options": "Patient",
				"insert_after": "po_detail",
				"read_only": True,
			},
			{
				"fieldname": "inpatient_medication_entry_child",
				"label": "Inpatient Medication Entry Child",
				"fieldtype": "Data",
				"insert_after": "patient",
				"read_only": True,
			},
		],
	},
	"on_setup": "healthcare.setup.setup_healthcare",
}


def setup_healthcare():
	if frappe.db.exists("Medical Department", "Cardiology"):
		# already setup
		return

	from healthcare.regional.india.abdm.setup import setup as abdm_setup

	abdm_setup()

	create_custom_records()
	create_default_root_service_units()

	setup_domain()

	frappe.clear_cache()


def setup_domain():
	"""
	Setup custom fields, properties, roles etc.
	Add Healthcare to active domains in Domain Settings
	"""
	domain = frappe.get_doc("Domain", "Healthcare")
	domain.setup_domain()

	# update active domains
	if "Healthcare" not in frappe.get_active_domains():
		has_domain = frappe.get_doc(
			{
				"doctype": "Has Domain",
				"parent": "Domain Settings",
				"parentfield": "active_domains",
				"parenttype": "Domain Settings",
				"domain": "Healthcare",
			}
		)
		has_domain.save()


def before_uninstall():
	"""
	Remove Custom Fields, portal menu items, domain
	"""
	delete_custom_records()
	remove_portal_settings_menu_items()

	domain = frappe.get_doc("Domain", "Healthcare")
	domain.remove_domain()

	remove_from_active_domains()

	frappe.clear_cache()


def create_default_root_service_units():
	from healthcare.healthcare.utils import create_healthcare_service_unit_tree_root

	companies = frappe.get_all("Company")
	for company in companies:
		create_healthcare_service_unit_tree_root(company)


def create_custom_records():
	create_medical_departments()
	create_antibiotics()
	create_lab_test_uom()
	create_duration()
	create_dosage()
	create_dosage_form()
	create_healthcare_item_groups()
	create_sensitivity()
	setup_patient_history_settings()
	setup_service_request_masters()
	setup_order_status_codes()


def create_medical_departments():
	departments = [
		"Accident And Emergency Care",
		"Anaesthetics",
		"Biochemistry",
		"Cardiology",
		"Diabetology",
		"Dermatology",
		"Diagnostic Imaging",
		"ENT",
		"Gastroenterology",
		"General Surgery",
		"Gynaecology",
		"Haematology",
		"Maternity",
		"Microbiology",
		"Nephrology",
		"Neurology",
		"Oncology",
		"Orthopaedics",
		"Pathology",
		"Physiotherapy",
		"Rheumatology",
		"Serology",
		"Urology",
	]
	for department in departments:
		mediacal_department = frappe.new_doc("Medical Department")
		mediacal_department.department = _(department)
		try:
			mediacal_department.save()
		except frappe.DuplicateEntryError:
			pass


def create_antibiotics():
	abt = [
		"Amoxicillin",
		"Ampicillin",
		"Bacampicillin",
		"Carbenicillin",
		"Cloxacillin",
		"Dicloxacillin",
		"Flucloxacillin",
		"Mezlocillin",
		"Nafcillin",
		"Oxacillin",
		"Penicillin G",
		"Penicillin V",
		"Piperacillin",
		"Pivampicillin",
		"Pivmecillinam",
		"Ticarcillin",
		"Cefacetrile (cephacetrile)",
		"Cefadroxil (cefadroxyl)",
		"Cefalexin (cephalexin)",
		"Cefaloglycin (cephaloglycin)",
		"Cefalonium (cephalonium)",
		"Cefaloridine (cephaloradine)",
		"Cefalotin (cephalothin)",
		"Cefapirin (cephapirin)",
		"Cefatrizine",
		"Cefazaflur",
		"Cefazedone",
		"Cefazolin (cephazolin)",
		"Cefradine (cephradine)",
		"Cefroxadine",
		"Ceftezole",
		"Cefaclor",
		"Cefamandole",
		"Cefmetazole",
		"Cefonicid",
		"Cefotetan",
		"Cefoxitin",
		"Cefprozil (cefproxil)",
		"Cefuroxime",
		"Cefuzonam",
		"Cefcapene",
		"Cefdaloxime",
		"Cefdinir",
		"Cefditoren",
		"Cefetamet",
		"Cefixime",
		"Cefmenoxime",
		"Cefodizime",
		"Cefotaxime",
		"Cefpimizole",
		"Cefpodoxime",
		"Cefteram",
		"Ceftibuten",
		"Ceftiofur",
		"Ceftiolene",
		"Ceftizoxime",
		"Ceftriaxone",
		"Cefoperazone",
		"Ceftazidime",
		"Cefclidine",
		"Cefepime",
		"Cefluprenam",
		"Cefoselis",
		"Cefozopran",
		"Cefpirome",
		"Cefquinome",
		"Ceftobiprole",
		"Ceftaroline",
		"Cefaclomezine",
		"Cefaloram",
		"Cefaparole",
		"Cefcanel",
		"Cefedrolor",
		"Cefempidone",
		"Cefetrizole",
		"Cefivitril",
		"Cefmatilen",
		"Cefmepidium",
		"Cefovecin",
		"Cefoxazole",
		"Cefrotil",
		"Cefsumide",
		"Cefuracetime",
		"Ceftioxide",
		"Ceftazidime/Avibactam",
		"Ceftolozane/Tazobactam",
		"Aztreonam",
		"Imipenem",
		"Imipenem/cilastatin",
		"Doripenem",
		"Meropenem",
		"Ertapenem",
		"Azithromycin",
		"Erythromycin",
		"Clarithromycin",
		"Dirithromycin",
		"Roxithromycin",
		"Telithromycin",
		"Clindamycin",
		"Lincomycin",
		"Pristinamycin",
		"Quinupristin/dalfopristin",
		"Amikacin",
		"Gentamicin",
		"Kanamycin",
		"Neomycin",
		"Netilmicin",
		"Paromomycin",
		"Streptomycin",
		"Tobramycin",
		"Flumequine",
		"Nalidixic acid",
		"Oxolinic acid",
		"Piromidic acid",
		"Pipemidic acid",
		"Rosoxacin",
		"Ciprofloxacin",
		"Enoxacin",
		"Lomefloxacin",
		"Nadifloxacin",
		"Norfloxacin",
		"Ofloxacin",
		"Pefloxacin",
		"Rufloxacin",
		"Balofloxacin",
		"Gatifloxacin",
		"Grepafloxacin",
		"Levofloxacin",
		"Moxifloxacin",
		"Pazufloxacin",
		"Sparfloxacin",
		"Temafloxacin",
		"Tosufloxacin",
		"Besifloxacin",
		"Clinafloxacin",
		"Gemifloxacin",
		"Sitafloxacin",
		"Trovafloxacin",
		"Prulifloxacin",
		"Sulfamethizole",
		"Sulfamethoxazole",
		"Sulfisoxazole",
		"Trimethoprim-Sulfamethoxazole",
		"Demeclocycline",
		"Doxycycline",
		"Minocycline",
		"Oxytetracycline",
		"Tetracycline",
		"Tigecycline",
		"Chloramphenicol",
		"Metronidazole",
		"Tinidazole",
		"Nitrofurantoin",
		"Vancomycin",
		"Teicoplanin",
		"Telavancin",
		"Linezolid",
		"Cycloserine 2",
		"Rifampin",
		"Rifabutin",
		"Rifapentine",
		"Rifalazil",
		"Bacitracin",
		"Polymyxin B",
		"Viomycin",
		"Capreomycin",
	]

	for a in abt:
		antibiotic = frappe.new_doc("Antibiotic")
		antibiotic.antibiotic_name = a
		try:
			antibiotic.save()
		except frappe.DuplicateEntryError:
			pass


def create_lab_test_uom():
	records = [
		{"doctype": "Lab Test UOM", "name": "umol/L", "lab_test_uom": "umol/L", "uom_description": None},
		{"doctype": "Lab Test UOM", "name": "mg/L", "lab_test_uom": "mg/L", "uom_description": None},
		{
			"doctype": "Lab Test UOM",
			"name": "mg / dl",
			"lab_test_uom": "mg / dl",
			"uom_description": None,
		},
		{
			"doctype": "Lab Test UOM",
			"name": "pg / ml",
			"lab_test_uom": "pg / ml",
			"uom_description": None,
		},
		{"doctype": "Lab Test UOM", "name": "U/ml", "lab_test_uom": "U/ml", "uom_description": None},
		{"doctype": "Lab Test UOM", "name": "/HPF", "lab_test_uom": "/HPF", "uom_description": None},
		{
			"doctype": "Lab Test UOM",
			"name": "Million Cells / cumm",
			"lab_test_uom": "Million Cells / cumm",
			"uom_description": None,
		},
		{
			"doctype": "Lab Test UOM",
			"name": "Lakhs Cells / cumm",
			"lab_test_uom": "Lakhs Cells / cumm",
			"uom_description": None,
		},
		{"doctype": "Lab Test UOM", "name": "U / L", "lab_test_uom": "U / L", "uom_description": None},
		{"doctype": "Lab Test UOM", "name": "g / L", "lab_test_uom": "g / L", "uom_description": None},
		{
			"doctype": "Lab Test UOM",
			"name": "IU / ml",
			"lab_test_uom": "IU / ml",
			"uom_description": None,
		},
		{"doctype": "Lab Test UOM", "name": "gm %", "lab_test_uom": "gm %", "uom_description": None},
		{
			"doctype": "Lab Test UOM",
			"name": "Microgram",
			"lab_test_uom": "Microgram",
			"uom_description": None,
		},
		{"doctype": "Lab Test UOM", "name": "Micron", "lab_test_uom": "Micron", "uom_description": None},
		{
			"doctype": "Lab Test UOM",
			"name": "Cells / cumm",
			"lab_test_uom": "Cells / cumm",
			"uom_description": None,
		},
		{"doctype": "Lab Test UOM", "name": "%", "lab_test_uom": "%", "uom_description": None},
		{
			"doctype": "Lab Test UOM",
			"name": "mm / dl",
			"lab_test_uom": "mm / dl",
			"uom_description": None,
		},
		{
			"doctype": "Lab Test UOM",
			"name": "mm / hr",
			"lab_test_uom": "mm / hr",
			"uom_description": None,
		},
		{
			"doctype": "Lab Test UOM",
			"name": "ulU / ml",
			"lab_test_uom": "ulU / ml",
			"uom_description": None,
		},
		{
			"doctype": "Lab Test UOM",
			"name": "ng / ml",
			"lab_test_uom": "ng / ml",
			"uom_description": None,
		},
		{
			"doctype": "Lab Test UOM",
			"name": "ng / dl",
			"lab_test_uom": "ng / dl",
			"uom_description": None,
		},
		{
			"doctype": "Lab Test UOM",
			"name": "ug / dl",
			"lab_test_uom": "ug / dl",
			"uom_description": None,
		},
	]

	insert_record(records)


def create_duration():
	records = [
		{"doctype": "Prescription Duration", "name": "3 Month", "number": "3", "period": "Month"},
		{"doctype": "Prescription Duration", "name": "2 Month", "number": "2", "period": "Month"},
		{"doctype": "Prescription Duration", "name": "1 Month", "number": "1", "period": "Month"},
		{"doctype": "Prescription Duration", "name": "12 Hour", "number": "12", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "11 Hour", "number": "11", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "10 Hour", "number": "10", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "9 Hour", "number": "9", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "8 Hour", "number": "8", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "7 Hour", "number": "7", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "6 Hour", "number": "6", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "5 Hour", "number": "5", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "4 Hour", "number": "4", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "3 Hour", "number": "3", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "2 Hour", "number": "2", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "1 Hour", "number": "1", "period": "Hour"},
		{"doctype": "Prescription Duration", "name": "5 Week", "number": "5", "period": "Week"},
		{"doctype": "Prescription Duration", "name": "4 Week", "number": "4", "period": "Week"},
		{"doctype": "Prescription Duration", "name": "3 Week", "number": "3", "period": "Week"},
		{"doctype": "Prescription Duration", "name": "2 Week", "number": "2", "period": "Week"},
		{"doctype": "Prescription Duration", "name": "1 Week", "number": "1", "period": "Week"},
		{"doctype": "Prescription Duration", "name": "6 Day", "number": "6", "period": "Day"},
		{"doctype": "Prescription Duration", "name": "5 Day", "number": "5", "period": "Day"},
		{"doctype": "Prescription Duration", "name": "4 Day", "number": "4", "period": "Day"},
		{"doctype": "Prescription Duration", "name": "3 Day", "number": "3", "period": "Day"},
		{"doctype": "Prescription Duration", "name": "2 Day", "number": "2", "period": "Day"},
		{"doctype": "Prescription Duration", "name": "1 Day", "number": "1", "period": "Day"},
	]
	insert_record(records)


def create_dosage():
	records = [
		{
			"doctype": "Prescription Dosage",
			"name": "1-1-1-1",
			"dosage": "1-1-1-1",
			"dosage_strength": [
				{"strength": "1.0", "strength_time": "9:00:00"},
				{"strength": "1.0", "strength_time": "13:00:00"},
				{"strength": "1.0", "strength_time": "17:00:00"},
				{"strength": "1.0", "strength_time": "21:00:00"},
			],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "0-0-1",
			"dosage": "0-0-1",
			"dosage_strength": [{"strength": "1.0", "strength_time": "21:00:00"}],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "1-0-0",
			"dosage": "1-0-0",
			"dosage_strength": [{"strength": "1.0", "strength_time": "9:00:00"}],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "0-1-0",
			"dosage": "0-1-0",
			"dosage_strength": [{"strength": "1.0", "strength_time": "14:00:00"}],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "1-1-1",
			"dosage": "1-1-1",
			"dosage_strength": [
				{"strength": "1.0", "strength_time": "9:00:00"},
				{"strength": "1.0", "strength_time": "14:00:00"},
				{"strength": "1.0", "strength_time": "21:00:00"},
			],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "1-0-1",
			"dosage": "1-0-1",
			"dosage_strength": [
				{"strength": "1.0", "strength_time": "9:00:00"},
				{"strength": "1.0", "strength_time": "21:00:00"},
			],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "Once Bedtime",
			"dosage": "Once Bedtime",
			"dosage_strength": [{"strength": "1.0", "strength_time": "21:00:00"}],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "5 times a day",
			"dosage": "5 times a day",
			"dosage_strength": [
				{"strength": "1.0", "strength_time": "5:00:00"},
				{"strength": "1.0", "strength_time": "9:00:00"},
				{"strength": "1.0", "strength_time": "13:00:00"},
				{"strength": "1.0", "strength_time": "17:00:00"},
				{"strength": "1.0", "strength_time": "21:00:00"},
			],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "QID",
			"dosage": "QID",
			"dosage_strength": [
				{"strength": "1.0", "strength_time": "9:00:00"},
				{"strength": "1.0", "strength_time": "13:00:00"},
				{"strength": "1.0", "strength_time": "17:00:00"},
				{"strength": "1.0", "strength_time": "21:00:00"},
			],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "TID",
			"dosage": "TID",
			"dosage_strength": [
				{"strength": "1.0", "strength_time": "9:00:00"},
				{"strength": "1.0", "strength_time": "14:00:00"},
				{"strength": "1.0", "strength_time": "21:00:00"},
			],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "BID",
			"dosage": "BID",
			"dosage_strength": [
				{"strength": "1.0", "strength_time": "9:00:00"},
				{"strength": "1.0", "strength_time": "21:00:00"},
			],
		},
		{
			"doctype": "Prescription Dosage",
			"name": "Once Daily",
			"dosage": "Once Daily",
			"dosage_strength": [{"strength": "1.0", "strength_time": "9:00:00"}],
		},
	]
	insert_record(records)


def create_dosage_form():
	records = [
		{
			"doctype": "Dosage Form",
			"dosage_form": "Tablet",
		},
		{
			"doctype": "Dosage Form",
			"dosage_form": "Syrup",
		},
		{
			"doctype": "Dosage Form",
			"dosage_form": "Injection",
		},
		{
			"doctype": "Dosage Form",
			"dosage_form": "Capsule",
		},
		{
			"doctype": "Dosage Form",
			"dosage_form": "Cream",
		},
	]
	insert_record(records)


def create_healthcare_item_groups():
	item_group = {
		"doctype": "Item Group",
		"item_group_name": _("All Item Groups"),
		"is_group": 1,
		"parent_item_group": "",
	}
	if not frappe.db.exists(item_group["doctype"], item_group["item_group_name"]):
		insert_record([item_group])

	records = get_item_group_records()
	insert_record(records)


def get_item_group_records():
	return [
		{
			"doctype": "Item Group",
			"item_group_name": _("Laboratory"),
			"name": _("Laboratory"),
			"is_group": 0,
			"parent_item_group": _("All Item Groups"),
		},
		{
			"doctype": "Item Group",
			"item_group_name": _("Drug"),
			"name": _("Drug"),
			"is_group": 0,
			"parent_item_group": _("All Item Groups"),
		},
	]


def create_sensitivity():
	records = [
		{"doctype": "Sensitivity", "sensitivity": _("Low Sensitivity")},
		{"doctype": "Sensitivity", "sensitivity": _("High Sensitivity")},
		{"doctype": "Sensitivity", "sensitivity": _("Moderate Sensitivity")},
		{"doctype": "Sensitivity", "sensitivity": _("Susceptible")},
		{"doctype": "Sensitivity", "sensitivity": _("Resistant")},
		{"doctype": "Sensitivity", "sensitivity": _("Intermediate")},
	]
	insert_record(records)


def setup_patient_history_settings():
	import json

	settings = frappe.get_single("Patient History Settings")
	configuration = get_patient_history_config()
	for dt, config in configuration.items():
		settings.append(
			"standard_doctypes",
			{"document_type": dt, "date_fieldname": config[0], "selected_fields": json.dumps(config[1])},
		)
	settings.save()


def setup_service_request_masters():
	records = [
		{"doctype": "Patient Care Type", "patient_care_type": _("Preventive")},
		{"doctype": "Patient Care Type", "patient_care_type": _("Intervention")},
		{"doctype": "Patient Care Type", "patient_care_type": _("Diagnostic")},
		{
			"doctype": "Code System",
			"uri": "http://hl7.org/fhir/request-intent",
			"is_fhir_defined": 1,
			"code_system": _("Intent"),
			"description": _(
				"Codes indicating the degree of authority/intentionality associated with a request."
			),
			"oid": "2.16.840.1.113883.4.642.4.114",
			"experimental": 1,
			"immutable": 1,
			"custom": 0,
		},
		{
			"doctype": "Code System",
			"uri": "http://hl7.org/fhir/request-priority",
			"is_fhir_defined": 1,
			"code_system": _("Priority"),
			"description": _("Identifies the level of importance to be assigned to actioning the request."),
			"oid": "2.16.840.1.113883.4.642.4.116",
			"experimental": 1,
			"immutable": 1,
			"custom": 0,
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Order"),
			"definition": _(
				"The request represents a request/demand and authorization for action by the requestor."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Proposal"),
			"definition": _(
				"The request is a suggestion made by someone/something that does not have an intention to ensure it occurs and without providing an authorization to act."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Plan"),
			"definition": _(
				"The request represents an intention to ensure something occurs without providing an authorization for others to act."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Directive"),
			"definition": _(
				"The request represents a legally binding instruction authored by a Patient or RelatedPerson."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Original Order"),
			"definition": _("The request represents an original authorization for action."),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Reflex Order"),
			"definition": _(
				"The request represents an automatically generated supplemental authorization for action based on a parent authorization together with initial results of the action taken against that parent authorization."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Filler Order"),
			"definition": _(
				"The request represents the view of an authorization instantiated by a fulfilling system representing the details of the fulfiller's intention to act upon a submitted order."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Instance Order"),
			"definition": _(
				"An order created in fulfillment of a broader order that represents the authorization for a single activity occurrence. E.g. The administration of a single dose of a drug."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Intent",
			"code_value": _("Option"),
			"definition": _(
				"The request represents a component or option for a RequestOrchestration that establishes timing, conditionality and/or other constraints among a set of requests."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-intent",
		},
		{
			"doctype": "Code Value",
			"code_system": "Priority",
			"code_value": _("Routine"),
			"definition": _("The request has normal priority."),
			"official_url": "http://hl7.org/fhir/ValueSet/request-priority",
		},
		{
			"doctype": "Code Value",
			"code_system": "Priority",
			"code_value": _("Urgent"),
			"definition": _("The request should be actioned promptly - higher priority than routine."),
			"official_url": "http://hl7.org/fhir/ValueSet/request-priority",
		},
		{
			"doctype": "Code Value",
			"code_system": "Priority",
			"code_value": _("ASAP"),
			"definition": _(
				"The request should be actioned as soon as possible - higher priority than urgent."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-priority",
		},
		{
			"doctype": "Code Value",
			"code_system": "Priority",
			"code_value": _("STAT"),
			"definition": _(
				"The request should be actioned immediately - highest possible priority. E.g. an emergency."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-priority",
		},
	]
	insert_record(records)


def get_patient_history_config():
	return {
		"Patient Encounter": (
			"encounter_date",
			[
				{"label": "Healthcare Practitioner", "fieldname": "practitioner", "fieldtype": "Link"},
				{"label": "Symptoms", "fieldname": "symptoms", "fieldtype": "Table Multiselect"},
				{"label": "Diagnosis", "fieldname": "diagnosis", "fieldtype": "Table Multiselect"},
				{"label": "Drug Prescription", "fieldname": "drug_prescription", "fieldtype": "Table"},
				{"label": "Lab Tests", "fieldname": "lab_test_prescription", "fieldtype": "Table"},
				{"label": "Clinical Procedures", "fieldname": "procedure_prescription", "fieldtype": "Table"},
				{"label": "Therapies", "fieldname": "therapies", "fieldtype": "Table"},
				{"label": "Review Details", "fieldname": "encounter_comment", "fieldtype": "Small Text"},
			],
		),
		"Clinical Procedure": (
			"start_date",
			[
				{"label": "Procedure Template", "fieldname": "procedure_template", "fieldtype": "Link"},
				{"label": "Healthcare Practitioner", "fieldname": "practitioner", "fieldtype": "Link"},
				{"label": "Notes", "fieldname": "notes", "fieldtype": "Small Text"},
				{"label": "Service Unit", "fieldname": "service_unit", "fieldtype": "Healthcare Service Unit"},
				{"label": "Start Time", "fieldname": "start_time", "fieldtype": "Time"},
				{"label": "Sample", "fieldname": "sample", "fieldtype": "Link"},
			],
		),
		"Lab Test": (
			"result_date",
			[
				{"label": "Test Template", "fieldname": "template", "fieldtype": "Link"},
				{"label": "Healthcare Practitioner", "fieldname": "practitioner", "fieldtype": "Link"},
				{"label": "Test Name", "fieldname": "lab_test_name", "fieldtype": "Data"},
				{"label": "Lab Technician Name", "fieldname": "employee_name", "fieldtype": "Data"},
				{"label": "Sample ID", "fieldname": "sample", "fieldtype": "Link"},
				{"label": "Normal Test Result", "fieldname": "normal_test_items", "fieldtype": "Table"},
				{
					"label": "Descriptive Test Result",
					"fieldname": "descriptive_test_items",
					"fieldtype": "Table",
				},
				{"label": "Organism Test Result", "fieldname": "organism_test_items", "fieldtype": "Table"},
				{
					"label": "Sensitivity Test Result",
					"fieldname": "sensitivity_test_items",
					"fieldtype": "Table",
				},
				{"label": "Comments", "fieldname": "lab_test_comment", "fieldtype": "Table"},
			],
		),
		"Therapy Session": (
			"start_date",
			[
				{"label": "Therapy Type", "fieldname": "therapy_type", "fieldtype": "Link"},
				{"label": "Healthcare Practitioner", "fieldname": "practitioner", "fieldtype": "Link"},
				{"label": "Therapy Plan", "fieldname": "therapy_plan", "fieldtype": "Link"},
				{"label": "Duration", "fieldname": "duration", "fieldtype": "Int"},
				{"label": "Location", "fieldname": "location", "fieldtype": "Link"},
				{"label": "Healthcare Service Unit", "fieldname": "service_unit", "fieldtype": "Link"},
				{"label": "Start Time", "fieldname": "start_time", "fieldtype": "Time"},
				{"label": "Exercises", "fieldname": "exercises", "fieldtype": "Table"},
				{"label": "Total Counts Targeted", "fieldname": "total_counts_targeted", "fieldtype": "Int"},
				{"label": "Total Counts Completed", "fieldname": "total_counts_completed", "fieldtype": "Int"},
			],
		),
		"Vital Signs": (
			"signs_date",
			[
				{"label": "Body Temperature", "fieldname": "temperature", "fieldtype": "Data"},
				{"label": "Heart Rate / Pulse", "fieldname": "pulse", "fieldtype": "Data"},
				{"label": "Respiratory rate", "fieldname": "respiratory_rate", "fieldtype": "Data"},
				{"label": "Tongue", "fieldname": "tongue", "fieldtype": "Select"},
				{"label": "Abdomen", "fieldname": "abdomen", "fieldtype": "Select"},
				{"label": "Reflexes", "fieldname": "reflexes", "fieldtype": "Select"},
				{"label": "Blood Pressure", "fieldname": "bp", "fieldtype": "Data"},
				{"label": "Notes", "fieldname": "vital_signs_note", "fieldtype": "Small Text"},
				{"label": "Height (In Meter)", "fieldname": "height", "fieldtype": "Float"},
				{"label": "Weight (In Kilogram)", "fieldname": "weight", "fieldtype": "Float"},
				{"label": "BMI", "fieldname": "bmi", "fieldtype": "Float"},
			],
		),
		"Inpatient Medication Order": (
			"start_date",
			[
				{"label": "Healthcare Practitioner", "fieldname": "practitioner", "fieldtype": "Link"},
				{"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date"},
				{"label": "End Date", "fieldname": "end_date", "fieldtype": "Date"},
				{"label": "Medication Orders", "fieldname": "medication_orders", "fieldtype": "Table"},
				{"label": "Total Orders", "fieldname": "total_orders", "fieldtype": "Float"},
			],
		),
	}


def setup_code_sysem_for_version():
	records = [
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://hl7.org/fhir/ValueSet/version-algorithm",
			"code_system": _("FHIRVersion"),
			"description": _(
				"""Indicates the mechanism used to compare versions to determine which is more current."""
			),
			"oid": "2.16.840.1.113883.4.642.3.3103",
			"experimental": 1,
			"immutable": 1,
			"custom": 0,
		},
		{
			"doctype": "Code Value",
			"code_system": _("FHIRVersion"),
			"code_value": "5.0.0",
			"display": _("5.0.0"),
		},
	]
	insert_record(records)


def setup_non_fhir_code_systems():
	"""A subset of external code systems as published in the FHIR R5 documentation
	https://www.hl7.org/fhir/terminologies-systems.html#external

	For a full set of external code systems, see
	https://terminology.hl7.org/external_terminologies.html
	"""
	code_systems = [
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://snomed.info/sct",
			"code_system": _("SNOMED CT"),
			"description": _(
				"""Using SNOMED CT with HL7 Standards. https://terminology.hl7.org/SNOMEDCT.html
				See also the SNOMED CT Usage Summary (link below) which summarizes the use of SNOMED CT in the base FHIR Specification.
				https://www.hl7.org/fhir/snomedct-usage.html"""
			),
			"oid": "2.16.840.1.113883.6.96",
			"experimental": 0,
			"immutable": 0,
			"custom": 0,
			"version": "5.0.0-FHIRVersion",
		},
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://www.nlm.nih.gov/research/umls/rxnorm",
			"code_system": _("RxNorm"),
			"description": _("Using RxNorm with HL7 Standards. https://terminology.hl7.org/RxNorm.html"),
			"oid": "2.16.840.1.113883.6.88",
			"experimental": 0,
			"immutable": 0,
			"custom": 0,
			"version": "5.0.0-FHIRVersion",
		},
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://loinc.org",
			"code_system": _("LOINC"),
			"description": _("Using LOINC with HL7 Standards. https://terminology.hl7.org/LOINC.html"),
			"oid": "2.16.840.1.113883.6.1",
			"experimental": 0,
			"immutable": 0,
			"custom": 0,
			"version": "5.0.0-FHIRVersion",
		},
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://unitsofmeasure.org",
			"code_system": _("pCLUCUMOCD"),
			"description": _("Using UCUM with HL7 Standards. https://terminology.hl7.org/UCUM.html"),
			"oid": "2.16.840.1.113883.6.8",
			"experimental": 0,
			"immutable": 0,
			"custom": 0,
			"version": "5.0.0-FHIRVersion",
		},
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://hl7.org/fhir/sid/icd-9-cm",
			"code_system": _("ICD-9-CM (clinical codes)"),
			"description": _("Using ICD-[x] with HL7 Standards. https://terminology.hl7.org/ICD.html"),
			"oid": "2.16.840.1.113883.6.103",
			"experimental": 0,
			"immutable": 0,
			"custom": 0,
			"version": "5.0.0-FHIRVersion",
		},
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://hl7.org/fhir/sid/icd-9-cm",
			"code_system": _("ICD-9-CM (procedure codes)"),
			"description": _("Using ICD-[x] with HL7 Standards. https://terminology.hl7.org/ICD.html"),
			"oid": "2.16.840.1.113883.6.104",
			"experimental": 0,
			"immutable": 0,
			"custom": 0,
			"version": "5.0.0-FHIRVersion",
		},
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://hl7.org/fhir/sid/icd-10-cm",
			"code_system": _("ICD-10-CM (United States)"),
			"description": _("Using ICD-[x] with HL7 Standards. https://terminology.hl7.org/ICD.html"),
			"oid": "2.16.840.1.113883.6.90",
			"experimental": 0,
			"immutable": 0,
			"custom": 0,
			"version": "5.0.0-FHIRVersion",
		},
	]
	insert_record(code_systems)


def setup_fhir_code_systems():
	code_systems = [
		{
			"doctype": "Code System",
			"is_fhir_defined": 1,
			"uri": "http://hl7.org/fhir/FHIR-version",
			"code_system": _("FHIRVersion"),
			"description": _("All published FHIR Versions."),
			"oid": "2.16.840.1.113883.4.642.4.1310",
			"experimental": 0,
			"immutable": 0,
			"custom": 0,
		},
		{
			"doctype": "Code System",
			"is_fhir_defined": 1,
			"uri": "http://hl7.org/fhir/publication-status",
			"code_system": _("PublicationStatus"),
			"description": _("The lifecycle status of an artifact."),
			"oid": "22.16.840.1.113883.4.642.3.3",
			"experimental": 0,
			"immutable": 1,
			"custom": 0,
		},
	]
	insert_record(code_systems)


def setup_diagnostic_module_codes():
	records = []

	records.extend(get_diagnostic_module_code_systems())
	records.extend(get_observation_category_codes())
	records.extend(get_observation_status_codes())

	# TODO: insert observation methods
	insert_record(records)


def get_diagnostic_module_code_systems():
	return [
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://terminology.hl7.org/CodeSystem/observation-category",
			"code_system": _("ObservationCategory"),
			"description": _("Observation Category codes."),
			"oid": "2.16.840.1.113883.4.642.1.1125",
			"experimental": 1,
			"immutable": 0,
			"custom": 0,
		},
		{
			"doctype": "Code System",
			"is_fhir_defined": 1,
			"uri": "http://hl7.org/fhir/observation-status",
			"code_system": _("ObservationStatus"),
			"description": _("Codes providing the status of an observation."),
			"version": "5.0.0-FHIRVersion",
			"oid": "2.16.840.1.113883.4.642.4.401",
			"experimental": 0,
			"immutable": 0,
			"complete": 1,
			"custom": 0,
		},
	]


def get_observation_category_codes():
	return [
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "social-history",
			"display": _("Social History"),
			"definition": _(
				"Social History Observations define the patient's occupational, personal (e.g., lifestyle), social, familial, and environmental history and health risk factors that may impact the patient's health."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "vital-signs",
			"display": _("Vital Signs"),
			"definition": _(
				"Clinical observations measure the body's basic functions such as blood pressure, heart rate, respiratory rate, height, weight, body mass index, head circumference, pulse oximetry, temperature, and body surface area."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "imaging",
			"display": _("Imaging"),
			"definition": _(
				"Observations generated by imaging. The scope includes observations regarding plain x-ray, ultrasound, CT, MRI, angiography, echocardiography, and nuclear medicine."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "laboratory",
			"display": _("Laboratory"),
			"definition": _(
				"The results of observations generated by laboratories. Laboratory results are typically generated by laboratories providing analytic services in areas such as chemistry, hematology, serology, histology, cytology, anatomic pathology (including digital pathology), microbiology, and/or virology. These observations are based on analysis of specimens obtained from the patient and submitted to the laboratory."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "procedure",
			"display": _("Procedure"),
			"definition": _(
				"Observations generated by other procedures. This category includes observations resulting from interventional and non-interventional procedures excluding laboratory and imaging (e.g., cardiology catheterization, endoscopy, electrodiagnostics, etc.). Procedure results are typically generated by a clinician to provide more granular information about component observations made during a procedure. An example would be when a gastroenterologist reports the size of a polyp observed during a colonoscopy."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "survey",
			"display": _("Survey"),
			"definition": _(
				"Assessment tool/survey instrument observations (e.g., Apgar Scores, Montreal Cognitive Assessment (MoCA))."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "exam",
			"display": _("Exam"),
			"definition": _(
				"Observations generated by physical exam findings including direct observations made by a clinician and use of simple instruments and the result of simple maneuvers performed directly on the patient's body."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "therapy",
			"display": _("Therapy"),
			"definition": _(
				"Observations generated by non-interventional treatment protocols (e.g. occupational, physical, radiation, nutritional and medication therapy)"
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Category"),
			"code_value": "activity",
			"display": _("Activity"),
			"definition": _(
				"Observations that measure or record any bodily activity that enhances or maintains physical fitness and overall health and wellness. Not under direct supervision of practitioner such as a physical therapist. (e.g., laps swum, steps, sleep data)"
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-category",
		},
	]


def get_observation_status_codes():
	# TODO: Add field for canonical mapping to Resource Status
	return [
		{
			"doctype": "Code Value",
			"code_system": _("Observation Status"),
			"code_value": "registered",
			"display": _("Registered"),
			"definition": _(
				"Observations that measure or record any bodily activity that enhances or maintains physical fitness and overall health and wellness. Not under direct supervision of practitioner such as a physical therapist. (e.g., laps swum, steps, sleep data.)"
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-status",
			"version": "6.0.0-cibuild",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Status"),
			"code_value": "preliminary",
			"display": _("Preliminary"),
			"definition": _(
				"This is an initial or interim observation: data may be incomplete or unverified."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-status",
			"version": "6.0.0-cibuild",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Status"),
			"code_value": "final",
			"display": _("Final"),
			"definition": _("The observation is complete and there are no further actions needed.)"),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-status",
			"version": "6.0.0-cibuild",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Status"),
			"code_value": "amended",
			"display": _("Amended"),
			"definition": _(
				"Subsequent to being Final, the observation has been modified subsequent. This includes updates/new information and corrections."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-status",
			"version": "6.0.0-cibuild",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Status"),
			"code_value": "corrected",
			"display": _("Corrected"),
			"definition": _(
				"Subsequent to being Final, the observation has been modified to correct an error in the test result."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-status",
			"version": "6.0.0-cibuild",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Status"),
			"code_value": "cancelled",
			"display": _("Cancelled"),
			"definition": _(
				"The observation is unavailable because the measurement was not started or not completed (also sometimes called 'aborted')."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-status",
			"version": "6.0.0-cibuild",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Status"),
			"code_value": "entered-in-error",
			"display": _("Entered in Error"),
			"definition": _(
				"The observation has been withdrawn following previous final release. This electronic record should never have existed, though it is possible that real-world decisions were based on it. (If real-world activity has occurred, the status should be 'cancelled' rather than 'entered-in-error'.)."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-status",
			"version": "6.0.0-cibuild",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Observation Status"),
			"code_value": "unknown",
			"display": _("Unknown"),
			"definition": _(
				"The authoring/source system does not know which of the status values currently applies for this observation. Note: This concept is not to be used for 'other' - one of the listed statuses is presumed to apply, but the authoring/source system does not know which."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/observation-status",
			"version": "6.0.0-cibuild",
		},
	]


def setup_order_status_codes():
	sr_code_systems = get_service_request_code_systems()
	insert_record(sr_code_systems)
	service_request_codes = get_service_request_codes()
	insert_record(service_request_codes)

	mr_code_systems = get_medication_request_code_systems()
	insert_record(mr_code_systems)
	medication_request_codes = get_medication_request_codes()
	insert_record(medication_request_codes)


def get_service_request_code_systems():
	return [
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://hl7.org/fhir/request-status",
			"code_system": _("Request Status"),
			"description": _("Request Status Codes."),
			"oid": "2.16.840.1.113883.4.642.4.112",
			"experimental": 1,
			"immutable": 0,
			"custom": 0,
		},
	]


def get_medication_request_code_systems():
	return [
		{
			"doctype": "Code System",
			"is_fhir_defined": 0,
			"uri": "http://hl7.org/fhir/CodeSystem/medicationrequest-status",
			"code_system": _("Medication Request Status"),
			"description": _("Medication Request Status Codes."),
			"oid": "2.16.840.1.113883.4.642.4.1377",
			"experimental": 1,
			"immutable": 0,
			"custom": 0,
		},
	]


def get_service_request_codes():
	return [
		{
			"doctype": "Code Value",
			"code_system": _("Request Status"),
			"code_value": "draft",
			"display": _("Draft"),
			"definition": _("The request has been created but is not yet complete or ready for action."),
			"official_url": "http://hl7.org/fhir/ValueSet/request-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Request Status"),
			"code_value": "active",
			"display": _("Active"),
			"definition": _("The request is in force and ready to be acted upon."),
			"official_url": "http://hl7.org/fhir/ValueSet/request-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Request Status"),
			"code_value": "on-hold",
			"display": _("On Hold"),
			"definition": _(
				"The request (and any implicit authorization to act) has been temporarily withdrawn but is expected to resume in the future."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Request Status"),
			"code_value": "revoked",
			"display": _("Revoked"),
			"definition": _(
				"The request (and any implicit authorization to act) has been terminated prior to the known full completion of the intended actions. No further activity should occur."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Request Status"),
			"code_value": "completed",
			"display": _("Completed"),
			"definition": _(
				"The activity described by the request has been fully performed. No further activity will occur."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Request Status"),
			"code_value": "entered-in-error",
			"display": _("Entered in Error"),
			"definition": _(
				"This request should never have existed and should be considered 'void'. (It is possible that real-world decisions were based on it. If real-world activity has occurred, the status should be 'revoked' rather than 'entered-in-error'.)."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Request Status"),
			"code_value": "unknown",
			"display": _("Unknown"),
			"definition": _(
				"The authoring/source system does not know which of the status values currently applies for this request. Note: This concept is not to be used for 'other' - one of the listed statuses is presumed to apply, but the authoring/source system does not know which."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/request-status",
		},
	]


def get_medication_request_codes():
	return [
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "active",
			"display": _("Active"),
			"definition": _(
				"The request is 'actionable', but not all actions that are implied by it have occurred yet."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "on-hold",
			"display": _("On Hold"),
			"definition": _(
				"Actions implied by the request are to be temporarily halted. The request might or might not be resumed. May also be called 'suspended'."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "ended",
			"display": _("Ended"),
			"definition": _(
				"The request is no longer active and the subject should no longer be taking the medication."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "stopped",
			"display": _("Stopped"),
			"definition": _(
				"Actions implied by the request are to be permanently halted, before all of the administrations occurred. This should not be used if the original order was entered in error"
			),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "completed",
			"display": _("Completed"),
			"definition": _("All actions that are implied by the request have occurred."),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "cancelled",
			"display": _("Cancelled"),
			"definition": _("The request has been withdrawn before any administrations have occurred"),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "entered-in-error",
			"display": _("Entered in Error"),
			"definition": _(
				"The request was recorded against the wrong patient or for some reason should not have been recorded (e.g. wrong medication, wrong dose, etc.). Some of the actions that are implied by the medication request may have occurred. For example, the medication may have been dispensed and the patient may have taken some of the medication."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "draft",
			"display": _("Draft"),
			"definition": _(
				"The request is not yet 'actionable', e.g. it is a work in progress, requires sign-off, verification or needs to be run through decision support process."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
		{
			"doctype": "Code Value",
			"code_system": _("Medication Request Status"),
			"code_value": "unknown",
			"display": _("Unknown"),
			"definition": _(
				"The authoring/source system does not know which of the status values currently applies for this request. Note: This concept is not to be used for 'other' - one of the listed statuses is presumed to apply, but the authoring/source system does not know which."
			),
			"official_url": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
		},
	]


def delete_custom_records():
	"""Delete custom records inserted by Health app"""
	records = get_item_group_records()
	for record in records:
		frappe.db.delete(record.get("doctype"), record.get("name"))

	frappe.db.set_single_value("Portal Settings", "default_role", "")


def remove_from_active_domains():
	"""Remove Healthcare from active domains in Domain Settings"""
	frappe.db.delete("Has Domain", {"domain": "Healthcare"})


def remove_portal_settings_menu_items():
	"""Remove menu items added in Portal Settings"""
	menu_items = frappe.get_hooks("standard_portal_menu_items", app_name="healthcare")
	for item in menu_items:
		frappe.db.delete("Portal Menu Item", item)
