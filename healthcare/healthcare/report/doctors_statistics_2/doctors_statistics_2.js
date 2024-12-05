// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Doctors statistics 2"] = {
	"filters": [
		{
			fieldname: "doctor",
			label: __("Doctor"),
			fieldtype: "Link",
			options: "Healthcare Practitioner",
		  },
		  {
			fieldname: "medical_department",
			label: __("Medical Department"),
			fieldtype: "Link",
			options: "Medical Department"

		  },
		  {
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		  },
		  {
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		  },


	]
};
