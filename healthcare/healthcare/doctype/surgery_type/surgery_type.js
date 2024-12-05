// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Surgery Type", {
	refresh(frm) {
        frm.set_query("surgery_sub_group", function() {  
            return {
                "filters":{'surgery_group':frm.doc.surgery_type}

            };
        });
	},
});
