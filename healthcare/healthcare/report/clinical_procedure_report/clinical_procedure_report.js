// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
// const currentDate = new Date();
const today = new Date();

const yesterday = new Date(today);
yesterday.setDate(today.getDate() - 1);
frappe.query_reports["Clinical Procedure Report"] = {
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
		  {
			fieldname: "reservation_type",
			label: __("التخصص"),
			fieldtype: "Select",
			options:['','Dental'],
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
			} else if (data["الحالة"] == null) {
			  value = "<span style='color:blue!important;'>" + value + "</span>";
			}
		}
	
		return value;
	  },
};
