// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Doctor Schedule Tool", {
	refresh(frm) {

        frm.disable_save();
        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
        }

        
        frm.add_custom_button("Set Data",function(){
            frappe.call({
                method: "set_practitioner_details",
                doc: frm.doc,
            
                callback: function (r) {
                  frm.reload_doc();

                }
            })
        })
    
	},
    
    day(frm){
        frappe.call({
            method: "get_practitioner_details",
            doc: frm.doc,
        
            callback: function (r) {
            refresh_field("time_slots")
            }
        })    
    },
});
