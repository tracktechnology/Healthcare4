// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
const currentDate = new Date();

frappe.query_reports["Imaging Report"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: currentDate
		  },
		  {
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: currentDate
		  },

		  {
			fieldname: "image_type",
			label: __("Imaging Type"),
			fieldtype: "Link",
			options:"Imaging Type",
			default: "Sonar"
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
