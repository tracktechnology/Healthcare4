// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Clinic Fees", {
	refresh(frm) {
        frm.add_custom_button('Get All Doctors', function() {
            frappe.call({
                method: "get_all_doctors",
                doc: frm.doc,
                callback: function (r) {
                    frm.reload_doc();

                },
              });
        }).addClass('btn-primary primary-action');
	},
});
