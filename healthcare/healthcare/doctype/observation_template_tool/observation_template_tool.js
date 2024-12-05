// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/healthcare_common.js' %}

frappe.ui.form.on("Observation Template Tool", {
	refresh(frm) {
        frm.disable_save();
        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
          }
          
    

        get_current_tab(frm,function(currentTab){
            set_buttons(frm,currentTab)
        })
	},

    edit_observation(frm){
        frappe.call({
            method: "get_observation_details",
            doc: frm.doc,
            callback: function (r) {
            refresh_field("edit_normal_test_templates")
            refresh_field("edit_rate")
            refresh_field("edit_custom_result")
            },
          });

    },
});



function set_buttons(frm,tab=null){
    if (tab=="add_tab"){
        frm.page.set_primary_action("Set Observation", function () {
            frappe.call({
                method: "set_observation",
                doc: frm.doc,
                callback: function (r) {
                    frappe.show_alert({
                        message:__('Add result successfully'),
                        indicator:'green'
                    }, 5);
                frm.reload_doc();

                },
              });
        });
    }
    else if (tab=="edit_pricing_tab"){
        frm.page.set_primary_action("Update Observation", function () {
            frappe.call({
                method: "update_observation",
                doc: frm.doc,
                callback: function (r) {
                    frappe.show_alert({
                        message:__('Updated result successfully'),
                        indicator:'green'
                    }, 5);
                frm.reload_doc();
                    
                },
              });
        });
    }
    else if (tab=="bulk_edit_tab"){
        frm.page.set_primary_action("Update", function () {
            frappe.call({
                method: "update_bulk_observation",
                doc: frm.doc,
                callback: function (r) {
                    frappe.show_alert({
                        message:__('Updated result successfully'),
                        indicator:'green'
                    }, 5);
                frm.reload_doc();
                    
                },
              });
        });
    }
}