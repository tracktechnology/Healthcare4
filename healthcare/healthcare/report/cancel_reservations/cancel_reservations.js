// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

const today = new Date();

const yesterday = new Date(today);
yesterday.setDate(today.getDate() - 1);

frappe.query_reports["Cancel Reservations"] = {
	"filters": [
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
		value = "<span style='color:red!important;'>" + value + "</span>";
	
		return value;
	  },
};
