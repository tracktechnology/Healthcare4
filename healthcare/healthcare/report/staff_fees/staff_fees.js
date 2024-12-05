// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
// Get current date
const currentDate = new Date();
const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

frappe.query_reports["Staff Fees"] = {
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
			default:firstDay
		  },
		  {
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default:lastDay
		  },

		  

	],


	

}

function formatDate(date) {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    return `${month}-${day}-${year}`;
}