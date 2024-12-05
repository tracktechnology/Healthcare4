// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/doctype/nursing_tool/nursing_tool_utils.js' %}
{% include 'healthcare/healthcare/healthcare_common.js' %}
let suppress_check_out_event = false;
let suppress_service_count_event = false;
var  reservation_type =null
frappe.ui.form.on("Nursing Tool", {
onload(frm){
    const queryString = window.location.search;
const parameters = new URLSearchParams(queryString);
 reservation_type = parameters.get('reservation_type');
 reservation_type="Emergency";
// if (patient){
//     frm.set_value('patient', patient)
// }
// if (!reservation_type){
//     window.location.href = '/desk';
//     return false;
// }   
} ,
refresh(frm) {
    get_current_tab(frm,function(currentTab){
        set_button_by_tab(frm,currentTab)


    })
    // frm.set_query("patient", function() {  
       
    //     return {
    //         "filters":{
    //             'status':"Admitted",
    //                     'reservation_type':reservation_type,
    //                 }

    //     };
    // })
    frm.set_query("laboratory_patient", function() {  
        return {
            "filters":{
                'status':"Admitted",
                        'reservation_type':reservation_type,
                    }
        };
    })
    frm.set_query("imaging_patient", function() {  
        return {

            "filters":{
                'status':"Admitted",
                        'reservation_type':reservation_type,
                    }
        };
    })

    frm.set_query("medication_patient", function() {  
        return {
            "filters":{
                'status':"Admitted",
                        'reservation_type':reservation_type,
                    }
        };
    })
    frm.set_query("medical_service_patient", function() {  
        return {
            "filters":{
                'status':"Admitted",
                        'reservation_type':reservation_type,
                    }
        };
    })

    
    frm.set_query("clinical_procedure_patient", function() {  
        return {
            "filters":{
                'status':"Admitted",
                        'reservation_type':reservation_type,
                    }
        };
    })
   

    frm.disable_save();
    if (frm.is_dirty()){
        document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
    }


    frm.page.set_secondary_action("Home", function () {
        frappe.set_route("app", "healthcare-home","Healthcare Home")
        }).addClass('btn-primary primary-action');	
            
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
add_medical_service: function(frm){
    $(document).ready(function() {
        $('.grid-add-row').click();
    });
},
// medical_service_patient: function(frm){
//     // alert("service pateint");
//     // load_medical_services(frm);
//     if(frm.doc.medical_service_patient){
//         load_medical_services(frm);
//     frm.events.set_patient_info(frm,frm.doc.medical_service_patient);

//     }
// },
patient: function(frm) {
    frm.events.set_patient_info(frm,frm.doc.patient);
},

// medical_service_patient: function(frm) {
//     frm.events.set_patient_info(frm,frm.doc.medical_service_patient);
// },

patient_history:function(frm) {
    frappe.call({
        method: "get_patient_history",
        doc:frm.doc,
        callback: function (r) {
            refresh_field("history_items")
            refresh_field("patient_name")
            refresh_field("reservation_type")
            refresh_field("medical_insurance_company")
            refresh_field("health_insurance")
            refresh_field("medical_insurance")
            refresh_field("room")
            
        },
      });
},
laboratory_patient: function(frm) {
        frm.events.set_patient_info(frm,frm.doc.laboratory_patient);
},

imaging_patient: function(frm) {
    frm.events.set_patient_info(frm,frm.doc.imaging_patient);
},
clinical_procedure_patient: function(frm) {
    frm.events.set_patient_info(frm,frm.doc.clinical_procedure_patient);
},

medication_patient: function(frm) {
    frm.events.set_patient_info(frm,frm.doc.medication_patient);
},
set_patient_info: async function(frm,patient_name) {
    if (patient_name) { 
        let me = frm
        if (frm.doc.patient!=patient_name){
            frm.set_value("patient",patient_name)
        }
        if (frm.doc.laboratory_patient!=patient_name){
            frm.set_value("laboratory_patient",patient_name)
        }
        if (frm.doc.imaging_patient!=patient_name){
            frm.set_value("imaging_patient",patient_name)
        }
        if (frm.doc.clinical_procedure_patient!=patient_name){
            frm.set_value("clinical_procedure_patient",patient_name)
        }
        
        if (frm.doc.medication_patient!=patient_name){
            frm.set_value("medication_patient",patient_name)
        }
        if (frm.doc.patient_history!=patient_name){
                frm.set_value("patient_history",patient_name)
        }
        
        if (frm.doc.medical_service_patient!=patient_name){
            frm.set_value("medical_service_patient",patient_name)
    }
        
        
     frm.refresh()
    } 
},
});



// function show_alert_message(){
    // frappe.show_alert({
    //     message: __("Thank you for reading the notice!"),
    //     indicator: 'green'
    // });
// }


function set_button_by_tab(frm,currentTab) {
	frm.clear_custom_buttons();
    frm.add_custom_button('BackOffice', function() {
        frappe.set_route("medical");
    }).addClass('btn-primary primary-action');
    if (currentTab=="clinics_tab"){
		set_clinics_tab_buttons(frm)
	}	
	else if (currentTab=="laboratory_tab"){
		set_lab_tab_buttons(frm)
        // frm.events.lab_status(frm)

	}
	else if (currentTab=="imaging_tab"){
		set_imaging_tab_buttons(frm)
        // frm.events.imaging_status(frm)

	}
	else if (currentTab=="clinical_procedure_tab"){
		set_clinical_procedure_tab_buttons(frm)
	}
    
	else if (currentTab=="medications_tab"){
		set_medications_tab_buttons(frm)
	}
    
    
		set_styles()
}




frappe.ui.form.on("Medical Service Tool Detail", {
    check_out: function(frm,cdt,cdn){
        if (suppress_check_out_event) {
            suppress_check_out_event = false;  // Reset the flag after skipping
            return;
        // set_service_count(frm,cdt,cdn);
        }else{
        set_service_count(frm,cdt,cdn);

        }
    },
    service_count: function(frm,cdt,cdn){
        if (suppress_service_count_event) {
            suppress_service_count_event = false;  // Reset the flag after skipping
            return;
        // set_service_count(frm,cdt,cdn);
        }else{
        set_check_out(frm,cdt,cdn);

        }
    },
    end_service: function(frm,cdt,cdn){
        let check_out = frappe.model.get_value(cdt,cdn,"check_out");
        let source = frappe.model.get_value(cdt,cdn,"source");
        if (! check_out){
            set_datetime_by_now(cdt,cdn,"check_out");

        }
        frappe.model.set_value(cdt,cdn,"ended",1);
        if(source){
        update_singel_medical_service(frm,cdt,cdn);
        }else{
                add_single_medical_service(frm,cdt,cdn);
        }
    },
    add_service: function(frm,cdt,cdn){
        add_single_medical_service(frm,cdt,cdn)
    },
    remove_service: function(frm,cdt,cdn){
        let source = frappe.model.get_value(cdt,cdn,"source");
        if(!source){
            location.reload();
        }else{
            frappe.call({
                method:"healthcare.healthcare.doctype.nursing_tool.nursing_tool.remove_medical_service",
                args:{source},
                callback: function(r){
                    alert("Removed")
                    location.reload();


                }
            })
        }
    },

    update: function(frm,cdt,cdn){
        update_singel_medical_service(frm,cdt,cdn);
    }

})

function set_check_out(frm,cdt,cdn){
    let check_in = frappe.model.get_value(cdt,cdn,"check_in");
    let period = frappe.model.get_value(cdt,cdn,"period");
    let period_count = frappe.model.get_value(cdt,cdn,"period_count");
    let service_count = frappe.model.get_value(cdt,cdn,"service_count");

    frappe.call({
        method:"healthcare.healthcare.doctype.nursing_tool.nursing_tool.get_check_out_time",
        args:{check_in,period,period_count,service_count},
        callback: function(r){
            console.log(String(r.message))
            suppress_check_out_event = true;
            frappe.model.set_value(cdt,cdn,"check_out",r.message,true);
        }
    })

}


function set_service_count(frm,cdt,cdn){
    let check_in = frappe.model.get_value(cdt,cdn,"check_in");
    let check_out = frappe.model.get_value(cdt,cdn,"check_out");
    let period = frappe.model.get_value(cdt,cdn,"period");
    let period_count = frappe.model.get_value(cdt,cdn,"period_count");

    frappe.call({
        method:"healthcare.healthcare.doctype.nursing_tool.nursing_tool.get_service_count",
        args:{check_in,check_out,period,period_count},
        callback: function(r){
            console.log(String(r.message))
            suppress_service_count_event = true;
            frappe.model.set_value(cdt,cdn,"service_count",r.message,true);
        }
    })
}

function load_medical_services(frm){
    frappe.call({
        doc: frm.doc,
        method:"load_medical_services",
        callback: function(r){
            frm.refresh_field("medical_services");
        }
    })
}



function open_childtable_dialog_programmatically(row) {
	
	const elem = $(`*[data-name="${row.name}"]`).filter(function() {
		return (
		$(this).clone() //clone the element
		.children() //select all the children
		.remove() //remove all the children
		.end() //again go back to selected element
	)})
	const test= elem

	// elem.on('click', function() { 

	// })
	
	console.log(elem[0][Object.keys(elem[0])[0]].grid_row.row_index[0].click());

	// add_open_form_button() {
}
function set_datetime_by_now(cdt,cdn,field_name){
    let now = new Date();

        // Format the date and time as YYYY-MM-DD HH:mm:ss
        let formattedDateTime = now.getFullYear() + '-' + 
                                ('0' + (now.getMonth() + 1)).slice(-2) + '-' + 
                                ('0' + now.getDate()).slice(-2) + ' ' + 
                                ('0' + now.getHours()).slice(-2) + ':' + 
                                ('0' + now.getMinutes()).slice(-2) + ':' + 
                                ('0' + now.getSeconds()).slice(-2);

        // Set the value of the datetime field
        frappe.model.set_value(cdt,cdn,field_name, formattedDateTime);
}  

function update_singel_medical_service(frm,cdt,cdn){
    let row = frappe.get_doc(cdt,cdn);
        frappe.call({
            method:"healthcare.healthcare.doctype.nursing_tool.nursing_tool.update_medical_service",
            args:{medical_service_row:row,reservation_type:frm.doc.reservation_type,
                health_insurance:frm.doc.health_insurance,
                medical_insurance:frm.doc.medical_insurance,
                patient:frm.doc.patient_name,
            },
            callback: function(r){tion_type:frm.doc.medical_service_reservation},
            callback: function(r){
                frappe.msgprint("Updated")
            }
        })
}

function add_single_medical_service(frm,cdt,cdn) {
    let row = frappe.get_doc(cdt,cdn);
        frappe.call({
            method:"healthcare.healthcare.doctype.nursing_tool.nursing_tool.add_medical_service",
            args:{inpatient_record:frm.doc.medical_service_patient,
                medical_service_row:row,reservation_type:frm.doc.reservation_type,
                health_insurance:frm.doc.health_insurance,
                medical_insurance_company:frm.doc.medical_insurance_company,
                medical_insurance:frm.doc.medical_insurance,
                patient:frm.doc.patient_name,
            },
            callback: function(r){
                load_medical_services(frm)
            }
        })
  }



frappe.ui.form.on("Inpatient Room Details", {
    btn_checkout:function(frm,cdt,cdn){
    var check_in=frappe.model.get_value(cdt,cdn,'check_in');
    var room=frappe.model.get_value(cdt,cdn,'room');
    var name=frappe.model.get_value(cdt,cdn,'name');
    frappe.call({
        method:"set_checkout_room",
        doc:frm.doc,
        freeze:true,

        args:{check_in:check_in,room:room,name:name},
        callback: function(r){
            frm.reload_doc();
        
        }
    })
    }
  })
