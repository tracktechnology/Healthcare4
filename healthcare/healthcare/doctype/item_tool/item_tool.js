// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/healthcare_common.js' %}

frappe.ui.form.on("Item Tool", {
	refresh(frm) {
        frm.disable_save();
        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
          }
          frm.set_query("department", function() {  
            return {
                "filters":{
                    'department_name':["!=","Clinics"],
                            
                        }
            };
        })

        get_current_tab(frm,function(currentTab){
            set_button_by_tab(frm,currentTab)
        })
    

   
	},
    edit_item(frm){
        frappe.call({
            method: "get_item_price_list",
            doc: frm.doc,
            callback: function (r) {
                
                frm.refresh()

            },
          });
    },
});



function set_button_by_tab(frm,currentTab){

if (currentTab=="add_tab"){
    frm.page.set_primary_action("Set Item", function () {
        frappe.call({
            method: "set_item",
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

else if(currentTab=="add_practitioner_tab"){
    frm.page.set_primary_action("Set Practitioner", function () {
        frappe.call({
            method: "set_practitioner",
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
else if(currentTab=="edit_pricing_tab"){
    frm.page.set_primary_action("Update Price List", function () {
        frappe.call({
            method: "update_item_price_list",
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

else if(currentTab=="edit_practitioner_tab"){
    frm.page.set_primary_action("Update Practitioner", function () {
        frappe.call({
            method: "update_practitioner",
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
}