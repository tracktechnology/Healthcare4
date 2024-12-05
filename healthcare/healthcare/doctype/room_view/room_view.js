// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Room View", {
	// refresh(frm) {
    // }

    onload: function (frm) {
        window.location.replace(window.origin+"/room_view/index");

    },

});
