// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Observation Request'] = {
	
	get_indicator: function(doc) {
		var status_color = {
			"Pending": "red",
			"Unpaid": "orange",
			"Paid": "blue",
			"Completed": "green",

		};
		return [__(doc.status), status_color[doc.status], "status,=,"+doc.status];
	},
};
