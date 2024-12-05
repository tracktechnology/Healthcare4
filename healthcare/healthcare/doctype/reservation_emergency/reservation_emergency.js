// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/doctype/reservation_emergency/reservation_emergency_utils.js' %}
{% include 'healthcare/healthcare/healthcare_common.js' %}
frappe.ui.form.on("Reservation Emergency", {
    on_load(frm){
    // frappe.model.clear_doc('Reservation Emergency', frm.doc.name);
    // frm.clear();
    frappe.ui.toolbar.clear_cache()

    // refresh_doc();
    }, 
refresh(frm) {
    // localStorage.clear();
    // frappe.model.clear_doc_cache('Reservation Emergency');
    // frappe.model.clear_all_locals();



    get_current_tab(frm,function(currentTab){
        set_button_by_tab(frm,currentTab)


    })
  

    frm.disable_save();
    if (frm.is_dirty()){
        document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
    }

    frm.page.set_primary_action("New Patient",function(){
        new_patient_dialog(frm)
    })
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

laboratory:function(frm){
    if ((frm.doc.laboratory).length>0){
    frappe.call({
        method: "healthcare.healthcare.doctype.reservation.reservation.get_total",
        args:{
            items:frm.doc.laboratory
        },
        callback: function (r) {
          frm.doc.lab_total=r.message
          frm.doc.lab_grand_total=r.message
         refresh_field("lab_total");
         refresh_field("lab_grand_total");
        },
      });
    }
    else{
        frm.doc.lab_total=0;
        frm.doc.lab_grand_total=0;
    refresh_field("lab_total")
	refresh_field("lab_grand_total");

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
          frm.doc.imaging_total=r.message
          frm.doc.imaging_grand_total=r.message
         refresh_field("imaging_total");
         refresh_field("imaging_grand_total");

        },
      });
    }
    else{
        frm.doc.imaging_total=0;
        frm.doc.imaging_grand_total=0;
		refresh_field("imaging_total")
		refresh_field("imaging_grand_total")
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
          frm.doc.clinical_procedure_total=r.message
          frm.doc.clinical_procedure_grand_total=r.message
         refresh_field("clinical_procedure_total");
         refresh_field("clinical_procedure_grand_total");
        },
      });
    }
    else{
        frm.doc.clinical_procedure_total=0;
        frm.doc.clinical_procedure_grand_total=0;
    refresh_field("clinical_procedure_total")
	refresh_field("clinical_procedure_grand_total");

    }
},


insurance_company_lab:function(frm){
    get_medical_insurance_percent(frm,frm.doc.insurance_company_lab,"Emergency","percentage_lab","company_percentage_lab","lab_total","lab_grand_total")

    frm.set_value(totla_field,data[0]/100*frm.doc[grand_total_field])

},
health_insurance_lab:function(frm){
	if (!frm.doc.health_insurance_lab){
		frm.set_value("lab_total",frm.doc.lab_grand_total)
		frm.set_value("percentage_lab",0)

	}
},


insurance_company_imaging:function(frm){
    get_medical_insurance_percent(frm,frm.doc.insurance_company_imaging,"Emergency","percentage_imaging","company_percentage_imaging","imaging_total","imaging_grand_total")

},

insurance_company_doctor:function(frm){
    get_medical_insurance_percent(frm,frm.doc.insurance_company_doctor,"Emergency","percentage_doctor","company_percentage_doctor","total","grand_total","emergency_fees_amount")
},

health_insurance_imaging:function(frm){
	if (!frm.doc.health_insurance_imaging){
		frm.set_value("imaging_total",frm.doc.imaging_grand_total)
		frm.set_value("percentage_imaging",0)


	}
},
health_insurance_doctor:function(frm){
    if (!frm.doc.health_insurance_doctor){
        // frappe.call({
        //     method: "get_patient_emergency",
        //     doc: frm.doc,
        //     callback: function (r) {
            refresh_field(["emergency_fees","emergency_fees_amount","total","grand_total"])
            frm.set_value("total",frm.doc.grand_total)
            frm.set_value("emergency_fees_amount",frm.doc.emergency_fees_amount*100/frm.doc.percentage_doctor)
            frm.set_value("percentage_doctor",0)
        //     },
        //   });
        
    }
   
},

insurance_company_clinical_procedure:function(frm){
    get_medical_insurance_percent(frm,frm.doc.insurance_company_clinical_procedure,"Emergency","percentage_clinical_procedure","company_percentage_clinical_procedure","clinical_procedure_total","clinical_procedure_grand_total")

},

health_insurance_clinical_procedure:function(frm){
	if (!frm.doc.health_insurance_clinical_procedure){
		frm.set_value("clinical_procedure_total",frm.doc.clinical_procedure_grand_total)
		frm.set_value("percentage_clinical_procedure",0)

	}
},

patient: function(frm) {

    frm.events.set_patient_info(frm,frm.doc.patient);
},

// lab_status: function(frm){
//     if (frm.doc.lab_status=="Open Service"){
//         frm.custom_buttons['حجز'].text('فتح خدمة');
//     }
//     else{
//         frm.custom_buttons['حجز'].text('دفع');
//     }
// },

// imaging_status: function(frm){
//     if (frm.doc.imaging_status=="Open Service"){
//         frm.custom_buttons['حجز'].text('فتح خدمة');

//     }
//     else{
//         frm.custom_buttons['حجز'].text('دفع');
//     }
// },

medical_insurance:function(frm){
    frm.set_query("insurance_company_clinics", function() {  
        return {
            "filters":{'company_name':frm.doc.medical_insurance}

        };
    })
},

medical_insurance:function(frm){
    frm.set_query("insurance_company_doctor", function() {  
        return {
            "filters":{'company_name':frm.doc.medical_insurance}

        };
    })
},
medical_insurance_lab:function(frm){
    frm.set_query("insurance_company_lab", function() {  
        return {
            "filters":{'company_name':frm.doc.medical_insurance_lab}

        };
    })
},
medical_insurance_imaging:function(frm){
    frm.set_query("insurance_company_imaging", function() {  
        return {
            "filters":{'company_name':frm.doc.medical_insurance_imaging}

        };
    })
},
medical_insurance_clinical_procedure:function(frm){
    frm.set_query("insurance_company_clinical_procedure", function() {  
        return {
            "filters":{'company_name':frm.doc.medical_insurance_clinical_procedure}

        };
    })
},

laboratory_patient: function(frm) {
   
        frm.events.set_patient_info(frm,frm.doc.laboratory_patient);
    get_current_tab(frm,function(currentTab){
     
        // if (currentTab=="laboratory_tab"&&frm.doc.laboratory_patient){
        
        // get_observation_request(frm,frm.doc.laboratory_patient,"Laboratory","laboratory",
        // "lab_department","lab_doctor",
        // "lab_total","lab_grand_total","lab_status")
        // }
    })
        
},

imaging_patient: function(frm) {
    frm.events.set_patient_info(frm,frm.doc.imaging_patient);
    get_current_tab(frm,function(currentTab){
        // alert(currentTab)
    // if (currentTab=="imaging_tab"&&frm.doc.imaging_patient){
    // get_observation_request(frm,frm.doc.imaging_patient,"Imaging","imaging",
    // "imaging_department","imaging_doctor",
    // "imaging_total","imaging_grand_total","imaging_status")
    // }
})
},
clinical_procedure_patient: function(frm) {

    frm.events.set_patient_info(frm,frm.doc.clinical_procedure_patient);
},
set_patient_info: async function(frm,patient_name) {
    if (patient_name) {
        let me = frm
        // frm.doc.patient=patient_name
        // frm.doc.laboratory_patient=patient_name
        // frm.doc.imaging_patient=patient_name
        // frm.doc.clinical_procedure_patient=patient_name
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
        frappe.call({
            method: 'healthcare.healthcare.doctype.patient.patient.get_patient_detail',
            args: {
                patient: patient_name
            },
            callback: function(data) {
                let age = '';
                if (data.message.dob) {
                    age = calculate_age(data.message.dob);
                }

                let values = {
                    'patient_age': age,
                    'patient_age_laboratory': age,
                    'patient_age_imaging': age,
                    'clinical_procedure_patient_age': age,
                    'patient_name':data.message.patient_name,
                    'clinical_procedure_patient_name':data.message.patient_name,
                    'patient_name_laboratory':data.message.patient_name,
                    'patient_name_imaging':data.message.patient_name,
                    'patient_sex': data.message.sex,
                    'inpatient_record': data.message.inpatient_record,
                    'inpatient_status': data.message.inpatient_status,
                    "mobile_phone":data.message.mobile,
                    "mobile_phone_laboratory":data.message.mobile,
                    "mobile_phone_imaging":data.message.mobile,
                    "mobile_phone_clinical_procedure":data.message.mobile,
                };

                frappe.run_serially([
                    
                   ()=>frm.set_value(values),
                       frm.refresh()
                    
                ]);
            }
        });
    } else {
        let values = {
            'patient_age': '',
            'patient_name':'',
            'patient_sex': '',
            'inpatient_record': '',
            'inpatient_status': ''
        };
        frm.set_value(values);
    }

 

    frappe.call({
        method: "get_patient_emergency",
        doc: frm.doc,
        callback: function (r) {
            refresh_field(["emergency_fees","emergency_fees_amount","total","grand_total"])
        },
      });
},
});



let calculate_age = function(birth) {
	let ageMS = Date.parse(Date()) - Date.parse(birth);
	let age = new Date();
	age.setTime(ageMS);
	let years =  age.getFullYear() - 1970;
	return `${years} ${__('Years(s)')} ${age.getMonth()} ${__('Month(s)')} ${age.getDate()} ${__('Day(s)')}`;
};

function new_patient_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __("Create a new patient"),
		fields: [
			{
			  label: __("Patient Name"),
			  fieldname: "patient_name",
			  fieldtype: "Data",
			  mandatory_depends_on:true,
		
			},
			{
				label: __("Gender"),
				fieldname: "gender",
				fieldtype: "Link",
                options:"Gender",
				mandatory_depends_on:true,
			  },
              {
				label: __("Mobile"),
				fieldname: "mobile",
				fieldtype: "Data",
				// mandatory_depends_on:true,
			  },
              {
				label: __("Date of Birth"),
				fieldname: "dob",
				fieldtype: "Date",
				mandatory_depends_on:true,
              },
			  {
				label: __("National ID"),
				fieldname: "uid",
				fieldtype: "Data",
              },

              
		],
		primary_action: function ({ patient_name,mobile,dob,gender,uid=null }) {
            if (mobile){
                if (!validateMobileNumber(mobile)){
                    frappe.throw('Please enter valid mobile number')
                }
            }
			frappe.call({
            method: 'healthcare.healthcare.doctype.reservation.reservation.create_new_patient',

			  args: {
				patient_name: patient_name,
				gender:gender,
                mobile:mobile,
                dob:dob,
                uid:uid,

			  },
			  freeze: true,
			  callback: function (r) {
                frm.set_value("patient",patient_name)
				// frm.refresh()
				d.hide();
			 
	
			  },
			  error: function () {
				d.hide();
				frappe.msgprint({
				  message: __(" Please try again."),
				  title: __("Request Failed"),
				  indicator: "red",
				});
			  },
			});
		  },
		  primary_action_label: __("Submit"),
	})

    d.show();

}


function validateMobileNumber(number) {
    // Regular expression to match a valid mobile number format
    var regex = /^[0-9]{11}$/;

    // Check if the number matches the regular expression
    if (regex.test(number)) {
        return true; // Valid mobile number
    } else {
        return false; // Invalid mobile number
    }
}


function get_medical_insurance_percent(frm,insurance_company,department,percent_field,company_percent_field,totla_field,grand_total_field,emergency_fees_amount) {
    frappe.call({
        method: 'healthcare.healthcare.doctype.reservation.reservation.get_medical_insurance_percent',
        args:{
            insurance_company:insurance_company,
            department:department
        },
        callback: function (r) {
            var data=r.message
        frm.set_value(percent_field,data[0])
        frm.set_value(company_percent_field,data[1])

        if (r.message !=0){
            frm.set_value(totla_field,data[0]/100*frm.doc[grand_total_field])
            frm.set_value("emergency_fees_amount",data[0]/100*frm.doc.emergency_fees_amount)
        }

        },
    });
}


	function show_alert_message(){
		frappe.show_alert({
			message: __("Thank you for reading the notice!"),
			indicator: 'green'
		});
	}







function set_button_by_tab(frm,currentTab) {
	frm.clear_custom_buttons();
    frm.add_custom_button('BackOffice', function() {
        frappe.set_route("medical");
    }).addClass('btn-primary primary-action');
    if (currentTab=="clinics_tab"&&frm.doc.patient){
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
 
    
		set_styles()
}



// function get_observation_request(frm,patient_name,observation_category,mutlti_selecte_field,medical_dep_field,doctor_field,total_field,grand_total_field,observation_status) {
//     frappe.call({
//         method: "get_observation_request",
//         doc: frm.doc,
//         args:{
//             patient_name:patient_name,
//             mutlti_selecte_field:mutlti_selecte_field,
//             medical_dep_field:medical_dep_field,
//             doctor_field:doctor_field,
//             total_field:total_field,
//             grand_total_field:grand_total_field,
//             observation_category:observation_category,
//             observation_status:observation_status
//         },
//             callback: function (r) {
//             if (r.message) {
//             refresh_field([mutlti_selecte_field,medical_dep_fiield,doctor_field,grand_total_field,total_field,observation_status])
//         }
//         },
//       });
// }


