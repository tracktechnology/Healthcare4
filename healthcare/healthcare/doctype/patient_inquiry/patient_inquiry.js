// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/healthcare_common.js' %}

frappe.ui.form.on("Patient Inquiry", {
    onload: function(frm){
        set_route_options(frm)
    },
	refresh(frm) {

		frm.disable_save();
        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
        }
        frm.page.set_secondary_action("Home", function () {
            frappe.set_route("app", "healthcare-home","Healthcare Home")
            }).addClass('btn-primary primary-action');	
            frm.add_custom_button('BackOffice', function() {
                frappe.set_route("medical");
            }).addClass('btn-primary primary-action');
        frm.add_custom_button("رجوع للحجز", function () {
            var local_doc = frappe.model.get_new_doc('Reservation');
            local_doc.medical_department=frm.doc.medical_department;
			local_doc.doctor=frm.doc.doctor;
            local_doc.__unsaved=0

            frappe.set_route("Form", "Reservation",local_doc.name);
             });
        const today = frappe.datetime.get_today();
        const after_seven_days = frappe.datetime.add_days(today, -7);

        frm.doc.to_date=today;
        frm.doc.from_date=after_seven_days;
        refresh_field("to_date");
        refresh_field("from_date");

        
        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
          }
        frm.set_query("laboratory", function() {  
            return {
                "filters": 	
                {'observation_category':"Laboratory"}
            };
        });

        frm.set_query("imaging", function() {  
            return {
                "filters": 	
                {'observation_category':"Imaging"}
            };
        });
     
	},
    medical_department:function(frm){
        frm.doc.doctor=null
        frm.doc.clinic_pricing=0
        refresh_field("doctor")
        refresh_field("clinic_pricing")
    frm.set_query("doctor", function() {  
        return {
            "filters": 	
            {'department':frm.doc.medical_department}
        };
    });
},
doctor: function(frm){
    frappe.call({
        method: "get_appointment_details",
        doc: frm.doc,
     

        callback: function (r) {
            frm.refresh()

          },
       
      });
},
laboratory:function(frm){
    if ((frm.doc.laboratory).length>0){
    frappe.call({
        method: "healthcare.healthcare.doctype.reservation.reservation.get_total",
        args:{
            items:frm.doc.laboratory
        },
        callback: function (r) {
          frm.doc.lab_pricing=r.message
         refresh_field("lab_pricing");
        },
      });
    }
    else{
        frm.doc.lab_pricing=0;
    refresh_field("lab_pricing")
    }
},





imaging:function(frm){
    if ((frm.doc.imaging).length>0){
    frappe.call({
        method: "healthcare.healthcare.doctype.reservation.reservation.get_total",
        args:{
            items:frm.doc.imaging
        },   
        callback: function (r) {
          frm.doc.imaging_price=r.message
         refresh_field("imaging_price");
        },
      });
    }
    else{
        frm.doc.imaging_price=0;
    refresh_field("imaging_price")
    }
},


clinical_procedure:function(frm){
    if ((frm.doc.clinical_procedure).length>0){
    frappe.call({
        method: "healthcare.healthcare.doctype.reservation.reservation.get_total",
        args:{
            items:frm.doc.clinical_procedure
        }, 
        callback: function (r) {
          frm.doc.clinical_procedure_price=r.message
         refresh_field("clinical_procedure_price");
        },
      });
    }
    else{
        frm.doc.clinical_procedure_price=0;
    refresh_field("clinical_procedure_price")
    }
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


