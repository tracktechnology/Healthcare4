// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/healthcare_common.js' %}
{% include 'healthcare/healthcare/doctype/reservation_inpatient/reservation_inpatient_utils.js' %}

{% include 'healthcare/healthcare/doctype/reservation/reservation.js' %}


frappe.ui.form.on("Reservation Inpatient", {
	refresh(frm) {
        frm.disable_save();
        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
        }
        frm.page.set_primary_action("New Patient",function(){
            new_patient_dialog(frm)
        })
        get_current_tab(frm,function(currentTab){
			set_button_by_tab(frm,currentTab)
		})
	},

emergency_patient: function(frm) {
    frm.refresh();
    
},

inpatient: function(frm) {
    frm.refresh();
    
},
medical_insurance:function(frm){
    frm.set_query("medical_insurance_company", function() {  
        return {
            "filters":{'company_name':frm.doc.medical_insurance}

        };
    })
},
});





frappe.ui.form.on("Patient Emergency Details", {
    select:function(frm,cdt,cdn){
    var reference_doc=frappe.model.get_value(cdt,cdn,'reference_doc');
    var patient=frappe.model.get_value(cdt,cdn,'patient');
    var medical_insurance_company=frappe.model.get_value(cdt,cdn,'medical_insurance_company');
    frappe.call({
        method: "update_patient_emergency",
        doc:frm.doc,
        args:{
            patient_emergency_name:reference_doc,
            patient:patient,
            medical_insurance_company:medical_insurance_company,
        },
        callback: function (r) {
        frm.refresh();
        }

    })

    }
  })


  
function set_button_by_tab(frm,currentTab) {
	frm.clear_custom_buttons();

   if (currentTab=="emergency_tab"){
    set_emergency_tab_buttons(frm)

        get_wating_patient_emergency(frm)
         setInterval(function() { get_wating_patient_emergency(frm); }, 60000);


	}
    else if (currentTab=="inpatient_tab"){
        set_inpatient_tab_buttons(frm)
    }
    
		set_styles()
}

function get_wating_patient_emergency(frm){
    
frappe.call({
    method: "healthcare.healthcare.doctype.patient_emergency.patient_emergency.get_wating_patient_emergency ",
    freeze: true,
  
    callback: function (r) {
        var data = r.message[0];

        frm.set_value("patient_emergency_details",null)
        for (var i = 0; i < data.length; i++) {
            let child_row = frm.add_child('patient_emergency_details');
    
            // Setting values in the new row
            child_row.patient = data[i].patient;
            child_row.from_date = data[i].datetime;
            child_row.reference_doc = data[i].name;
            child_row.medical_insurance_company = data[i].medical_insurance_company;
        }      
        refresh_field("patient_emergency_details")
        frm.set_value("available_capacity",r.message[1])
    },
  });
}


