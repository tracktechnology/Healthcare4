// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
const today = new Date();

// Subtract one day from the date
const yesterday = new Date(today);
yesterday.setDate(today.getDate() - 1);
frappe.query_reports["Clinic Report"] = {
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
				default: yesterday
			  },
			  {
				fieldname: "to_date",
				label: __("To Date"),
				fieldtype: "Date",
				default: yesterday
			  },
	
	],
	formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);
    value = "<span style='font-weight:Bold';>" + value + "</span>";
	if (data){
		if (data["الحالة"] == "Paid") {
		  value = "<span style='color:green!important;'>" + value + "</span>";
		} else if (data["الحالة"] == "Cancelled") {
		  value = "<span style='color:DarkRed!important;'>" + value + "</span>";
		}
	}

    return value;
  },
};
