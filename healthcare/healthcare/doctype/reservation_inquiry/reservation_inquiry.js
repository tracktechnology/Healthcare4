// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/healthcare_common.js' %}

frappe.ui.form.on("Reservation Inquiry", {
    onload(frm){
        const today = frappe.datetime.get_today();
        const after_seven_days = frappe.datetime.add_days(today, 7);

        frm.doc.from_date=today;
        frm.doc.to_date=after_seven_days;
        refresh_field("to_date");
        refresh_field("from_date");
    },
    refresh(frm) {
        // set_route_options(frm)

        // frm.disable_save();
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
        frm.add_custom_button("تبديل الدكتور", function(){
            var selectedRows = frm.doc.reservation_deatils.filter(row => row.__checked); 
            frappe.call({
            method: "healthcare.healthcare.doctype.reservation_inquiry.reservation_inquiry.replace_doctor",
            args:{
                rows: selectedRows,
                replace_doctor:frm.doc.replace_doctor
            },
            callback: function (r) {
            },
          }); 

        });
        frm.add_custom_button(" الغاء الحجز", function(){
            var selectedRows = frm.doc.reservation_deatils.filter(row => row.__checked); 
            if (selectedRows.length==0){
                frappe.throw("من فضلك قم بأختيار العناصر من الجدول")
            }
            frappe.call({
                method: "cancel_reservation",
                doc: frm.doc,
                freeze: true,
                args:{
                    items: selectedRows
                },
                callback: function (r) {
                    frm.reload_doc();
                
                },
              });

        });	 

      
          
	},
    reservation_doctor:function(frm){
        get_reservation_details(frm);

        frm.set_query("replace_doctor", function() {  //field name  + must be a link
            return {
                "filters": 	{
                    // 'department': ['=', frm.doc.medical_department],
                    'name': ['!=', frm.doc.reservation_doctor],
                }
            };
        });

    },
    
    reservation_patient:function(frm){
        get_reservation_details(frm);
    },
    
    from_date:function(frm){
        get_reservation_details(frm);
    },
    
    to_date:function(frm){
        get_reservation_details(frm);
    },
    reservation_type:function(frm){
        get_reservation_details(frm);
    },
    cancel_selected:function(frm){
    
    },
    replace_btn:function(frm){
        var selectedRows = frm.doc.reservation_deatils.filter(row => row.__checked); 
        frappe.call({
            method: "healthcare.healthcare.doctype.reservation_inquiry.reservation_inquiry.replace_doctor",
            args:{
                rows: selectedRows,
                replace_doctor:frm.doc.replace_doctor
            },
            callback: function (r) {
            },
          }); 
    },
    
    
});

frappe.ui.form.on("Patient Inquiry Details", {
    cancel:function (frm, cdt, cdn) {

        var patient_encounter = frappe.model.get_value(cdt, cdn, 'patient_encounter') 
        frappe.call({
            method: "healthcare.healthcare.doctype.reservation_inquiry.reservation_inquiry.cancel_reservation",
            args:{
                patient_encounter:patient_encounter
            },
            callback: function (r) {
            },
          });    }
});





function get_reservation_details(frm) {

    frappe.call({
        method: "get_reservation_details",
        doc: frm.doc,
        callback: function (r) {

         frm.refresh()
        },
      });
}