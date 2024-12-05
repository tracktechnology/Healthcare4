// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/healthcare_common.js' %}

frappe.ui.form.on("Appointment Tool", {
	refresh(frm) {
        set_route_options(frm)
        frm.disable_save();
        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
        }

        frm.add_custom_button("رجوع للحجز", function () {
            var local_doc = frappe.model.get_new_doc('Reservation');
            local_doc.medical_department=frm.doc.medical_department;
            local_doc.doctor=frm.doc.doctor;
            local_doc.__unsaved=0

            frappe.set_route("Form", "Reservation",local_doc.name);
             });
             frm.page.set_secondary_action("Home", function () {
                frappe.set_route("app", "healthcare-home","Healthcare Home")
                }).addClass('btn-primary primary-action');	
    
	},
    doctor: function(frm){
		frappe.call({
            method: "get_appointment_details",
            doc: frm.doc,
            args:{
                doctor:true
            },

            callback: function (r) {
                frm.refresh()

              },
           
          });
    },

    medical_department: function(frm){
		frappe.call({
            method: "get_appointment_details",
            doc: frm.doc,
            args:{
                department:true
            },

            callback: function (r) {
                frm.refresh()

              },
           
          });
    },
});

frappe.ui.form.on("Appointment Details", {
    reservation:function (frm, cdt, cdn) {

        var doctor = frappe.model.get_value(cdt, cdn, 'doctor') 
        var local_doc = frappe.model.get_new_doc('Reservation');
        local_doc.doctor=doctor;
        frappe.set_route("Form", "Reservation",local_doc.name);

            }
  });