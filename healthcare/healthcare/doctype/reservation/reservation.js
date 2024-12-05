// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
var practitioner_days=[];
{% include 'healthcare/healthcare/doctype/reservation/reservation_utils.js' %}
{% include 'healthcare/healthcare/healthcare_common.js' %}
var current_tab=null;
let tab_dict = {
    "clinics_tab": "Clinics",
    "laboratory_tab": "Laboratory",
    "imaging_tab": "Imaging",
    "clinical_procedure_tab": "Clinical Procedure",
    "dental_tab": "Dental",
  };  
 
frappe.ui.form.on("Reservation", {
    onload: function(frm){
        // set_route_options(frm)
        get_redirect_tabs()

    },
    medical_department(frm){
        var filter;
		if (frm.doc.medical_department==''){
             filter={}
        }
        else{
            medical_department=frm.doc.medical_department
            filter={'department':medical_department}
        }
        frm.set_query("doctor", function() {  
            return {
                "filters":filter
            };
        });
	
    },

    doctor: function(frm){
        frappe.call({
            method: "healthcare.healthcare.doctype.reservation.reservation.get_practitioner_days",
            args: {
                practitioner: frm.doc.doctor,
            },
            callback: function (r) {
                var arrays =  r.message
                var days =  arrays.flat(1) 
                practitioner_days= sortDays(days)
              },
          });

          if (current_tab=='clinics_tab'){
          frappe.call({
            method: "healthcare.healthcare.doctype.reservation.reservation.get_doctor_charge",
            args: {
                doctor: frm.doc.doctor,
            },
            callback: function (r) {
                var res=r.message;
               frm.set_value("booking_fees",res[0])
               frm.set_value("consulting_fees",res[1])
                frm.trigger("is_consulting");

              },
          });
        }
    },
    
	refresh(frm) {
        // frm.set_intro('Please set the value of description', 'blue');
        // frm.fields_dict['reservation_invoices'].grid.wrapper.on('click', '.grid-row', function(e) {
        // frm.set_value("doctor","HLC-PRAC-2024-00044")
        // frm.set_value("patient","(for test)هاني عادل")
        // frm.fields_dict['reservation_invoices'].grid.wrapper.on('click', 'div.grid-row', function(e) {
       
        // frm.set_df_property('clinical_procedure', 'hidden', 1)

        var today=frappe.datetime.nowdate()
        frm.set_value(
        {"reservation_date":today}
        )
        
        frm.set_query("dental_procedure", function() {  
            return {
                "filters": {'medical_department':'اسنان'}
            };
        });
         
        // set_route_options(frm)
        get_current_tab(frm,function(currentTab){
            current_tab=currentTab
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
            // frappe.ui.toolbar.clear_cache();
            window.location.replace(window.origin+"/Healthcare Home");
            
            // frappe.set_route("app", "healthcare-home","Healthcare Home")
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

    medical_insurance:function(frm){
        frm.set_query("insurance_company", function() {  
            return {
                "filters":{'company_name':frm.doc.medical_insurance}

            };
        })
    },

cancel_doctor_fees(frm){
    // frm.trigger("doctor")
    frm.set_df_property('health_insurance', 'read_only', 1)

    if (!frm.doc.cancel_doctor_fees){
        // frm.trigger("doctor")
        frm.set_value("total",frm.doc.grand_total)
        frm.set_df_property('health_insurance_clinics', 'read_only', 0)

        return 
    }
    if (!frm.doc.doctor&&frm.doc.cancel_doctor_fees){
        frm.set_value("cancel_doctor_fees",0)
        // frm.trigger("is_consulting");

        frappe.throw(" من فضلك قم باختيار الدكتور")
    }

    frappe.call({
        method: "healthcare.healthcare.doctype.reservation.reservation.get_doctor_fees",
        // doc:frm.doc,
        args:{
            doctor:frm.doc.doctor,
            total:frm.doc.total,
            doctor_disount_percent:frm.doc.doctor_percentage_clinics,
            is_consulting:frm.doc.is_consulting
        },
        freeze:true,
        callback: function (r) {
            frm.set_value("total",r.message)
            
        }
    })
    refresh_field("health_insurance")

},
hospital_percentage:function(frm){
    if  (frm.doc.extra_discount){
        set_extra_percentage(frm)
    
    }
},
doctor_percentage:function(frm){
    // var percent=frm.doc.doctor_percentage_clinics+frm.doc.hospital_percentage_clinics+frm.doc.company_percentage_clinics+frm.doc.percentage_clinics
    // var total= frm.doc.grand_total-(frm.doc.total*percent/100)
    // frm.set_value("total",total)
    // console.log(frm.doc.grand_total)
    if (frm.doc.special_doctor_percentage){
        set_extra_percentage(frm)

    }

  
},
is_consulting:function(frm){
    frappe.run_serially([
   ()=>{
    return new Promise((resolve, reject) => {
    var is_consulting=0
     frappe.call({
        method: "get_consulting",
        doc: frm.doc,
    
        callback: function (r) {
          if (r.message) {
        //   frm.set_value("is_consulting",1)
           
            frm.doc.is_consulting=1
            refresh_field("is_consulting")
          frm.set_value("patient_encounter",r.message)
          is_consulting=1
          }

          resolve(is_consulting)
        },
      });
    })
    },
    (is_consulting)=>{

        if (frm.doc.is_consulting||is_consulting){
            frm.set_value("total",frm.doc.consulting_fees)
            frm.set_value("grand_total",frm.doc.consulting_fees)
        }
        else{
    
            frm.set_value("total",frm.doc.booking_fees)
            frm.set_value("grand_total",frm.doc.booking_fees)
    
            // frm.set_value("total",frm.doc.consulting_fees)
    
        }
        
    }
    ])

      
  


},
laboratory:function(frm){
    if ((frm.doc.laboratory).length>0){
    frappe.call({
        method: "healthcare.healthcare.doctype.reservation.reservation.get_total",
        args:{
            items:frm.doc.laboratory
        },
        callback: function (r) {
          frm.doc.total=r.message
          frm.doc.grand_total=r.message
         refresh_field("total");
         refresh_field("grand_total");
        },
      });
    }
    else{
        frm.doc.total=0;
        frm.doc.grand_total=0;
    refresh_field("total")
	refresh_field("grand_total");

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
          frm.doc.total=r.message
          frm.doc.grand_total=r.message
         refresh_field("total");
         refresh_field("grand_total");

        },
      });
    }
    else{
        frm.doc.total=0;
        frm.doc.grand_total=0;
		refresh_field("total")
		refresh_field("grand_total")
    }
},
clinical_procedure:function(frm){
    console.log((frm.doc.clinical_procedure).length)
    if ((frm.doc.clinical_procedure).length>0){
        frappe.call({
            method: "healthcare.healthcare.doctype.reservation.reservation.get_total",
            args:{
                items:frm.doc.clinical_procedure
            },
            callback: function (r) {
            frm.doc.total=r.message
            frm.doc.grand_total=r.message
            refresh_field("total");
            refresh_field("grand_total");
            },
        });
    }
    // else{
    //         frm.doc.total=0;
    //         frm.doc.grand_total=0;
    //         refresh_field("total")
    //         refresh_field("grand_total");
    // }
},
dental_procedure:function(frm){
    if ((frm.doc.dental_procedure).length>0){
    frappe.call({
        method: "healthcare.healthcare.doctype.reservation.reservation.get_total",
        args:{
            items:frm.doc.dental_procedure
        },
        callback: function (r) {
          frm.doc.total=r.message
          frm.doc.grand_total=r.message
        //   frm.doc.clinical_procedure_grand_total=r.message
         refresh_field("total");
         refresh_field("grand_total");
        //  refresh_field("clinical_procedure_grand_total");
        },
      });
    }
    else{
        frm.doc.total=0;
        // frm.doc.clinical_procedure_grand_total=0;
    refresh_field("total")
	// refresh_field("clinical_procedure_grand_total");

    }
},
insurance_company:function(frm){
    get_medical_insurance_percent(frm,frm.doc.insurance_company,frm.doc.medical_department)

},



health_insurance:function(frm){
    frm.set_df_property('cancel_doctor_fees', 'read_only', 1)

	if (!frm.doc.health_insurance){
		frm.set_value("total",frm.doc.grand_total)
		frm.set_value("percentage",0)
		frm.set_value("medical_insurance","")
		frm.set_value("insurance_company","")
        frm.set_df_property('cancel_doctor_fees', 'read_only', 0)

	}

},

patient: function(frm) {

        frm.events.set_patient_info(frm,frm.doc.patient);
},

is_follow_up: function(frm)
{
    frm.fields_dict['reservation_invoices'].grid.wrapper.on('click', '.grid-row-check', function() {
        var selectedRows = frm.doc.reservation_invoices.filter(row => row.__checked);
            // var sales_invoice=selectedRows['sales_invoice']
        if (selectedRows.length > 0) {
        
            frappe.call({
                method: "get_dental_ivoice_details",
                doc: frm.doc,
                args:{
                    sales_invoice:selectedRows[0]['sales_invoice']
                },
                callback: function (r) {
                refresh_field(["dental_procedure","total","paid","remaining","payments","reservation_follow_up_details"])
                },
              });

        }


    });

    if (!frm.doc.patient||!frm.doc.doctor){
        frm.set_value("is_follow_up",0)

        frappe.throw("Please select  Patient and Doctor")
    }

    frappe.call({
        method: "get_patient_dental_procedure",
        doc: frm.doc,
        callback: function (r) {
        refresh_field(["dental_procedure","dental_total","dental_paid","dental_remaining","payments","reservation_invoices","reservation_follow_up_details"])
        },
      });
},
request_patient: function(frm){
    frm.refresh()
    if (frm.doc.request_patient){
        frappe.call({
            method: "get_observation_invoice",
            doc: frm.doc,
            callback: function (r) {
                    // frm.refresh();
                    refresh_field("request_invoices")
                    refresh_field("zero_invoices")
            },
          });
        
    }
},
cancel_patient: function(frm) {
    frm.events.set_patient_info(frm,frm.doc.cancel_patient);
    if (frm.doc.cancel_patient){
        frappe.call({
            method: "get_patient_invoices",
            doc: frm.doc,
            callback: function (r) {
                    // frm.refresh();
                    refresh_field("reservations")
                    refresh_field("invoices")
            },
          });
        
    }
},

set_patient_info: async function(frm,patient_name) {
    var encounter_id= Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    frm.set_value("encounter_id",encounter_id)
    if (patient_name) {
        let me = frm
        // frm.doc.patient=patient_name
        // frm.doc.laboratory_patient=patient_name
        // frm.doc.imaging_patient=patient_name
        // frm.doc.clinical_procedure_patient=patient_name
        // if (frm.doc.patient!=patient_name){
        //     frm.set_value("patient",patient_name)
        // }
        
        if (frm.doc.cancel_patient!=patient_name){
            frm.set_value("cancel_patient",patient_name)
        }
        
        frappe.call({
            method: 'healthcare.healthcare.doctype.patient.patient.get_patient_detail',
            args: {
                patient: patient_name
            },
            callback: function(data) {
                let age = '';
                // if (data.message.dob) {
                //     age = calculate_age(data.message.dob);
                // }
                let values = {
                    'patient_age': data.message.age_years,
                    'patient_name':data.message.patient_name,
                    'patient_sex': data.message.sex,
                    'inpatient_record': data.message.inpatient_record,
                    'inpatient_status': data.message.inpatient_status,
                    "mobile_phone":data.message.mobile,
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
},
});



let calculate_age = function(birth) {
	let ageMS = Date.parse(Date()) - Date.parse(birth);
	let age = new Date();
	age.setTime(ageMS);
	let years =  age.getFullYear() - 1970;
	return `${years} ${__('Years(s)')} ${age.getMonth()} ${__('Month(s)')} ${age.getDate()} ${__('Day(s)')}`;
};

function new_patient_dialog(frm=null) {
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
				mandatory_depends_on:true,
			  },
              {
				label: __("Age"),
				fieldname: "age",
				fieldtype: "Data",
				mandatory_depends_on:true,
              },
              {
				label: __("Address"),
				fieldname: "address",
				fieldtype: "Data",
				mandatory_depends_on:true,
              },
			  {
				label: __("National ID"),
				fieldname: "uid",
				fieldtype: "Data",
              },

              
		],
		primary_action: function ({ patient_name,mobile,age,gender,address,uid=null }) {
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
                age:age,
                uid:uid,
                address:address,

			  },
			  freeze: true,
			  callback: function (r) {
                if (frm){
                    frm.set_value("patient",patient_name)

                }
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




function get_medical_insurance_percent(frm,insurance_company,medical_department=null) {
    
    frappe.call({
            method: 'healthcare.healthcare.healthcare_utils.get_medical_insurance_percent',
            args:{
                insurance_company:insurance_company,
                department:tab_dict[current_tab],
                reservation_type:"Outpatient",
                medical_department:medical_department,
            },
            callback: function (r) {
            var data=r.message
			frm.set_value("percentage",data[0])
			frm.set_value("company_percentage",data[1])
			frm.set_value("hospital_percentage",data[2])
			frm.set_value("doctor_percentage",data[3])
            // frappe.throw(data)
			if (r.message !=0){
                // if (totla_field){
                    var total=data[0]/100*frm.doc.grand_total
                    // if (total<0){
                            // total=0
                    // }
                    frm.set_value("total",total)
                // }
			}
            },
        });
}

  window.set_reservation = function(appointment_time,patient,
    date,paid_amount,practitioner,medical_department,service_unit,medical_insurance,percentage_clinics,
    company_percentage_clinics,
    hospital_percentage_clinics,is_healthcare_insurance,is_consultation,patient_encounter,
    grand_total,cancel_doctor_fees,doctor_percentage_clinics,encounter_id,encounter_date,paper_receipt){
    // window.set_reservation = function(frm){
    
    frappe.call({
		method: "healthcare.healthcare.doctype.reservation.reservation.set_reservation",
		args: {
			patient:patient,
			date:date,
			paid_amount:paid_amount,
			practitioner:practitioner,
			appointment_time:appointment_time,
			medical_department:medical_department,
			service_unit:service_unit,
			medical_insurance:medical_insurance,
			percentage_clinics:percentage_clinics,
            company_percentage_clinics:company_percentage_clinics,
			is_healthcare_insurance:is_healthcare_insurance,
            is_consultation:is_consultation,
            patient_encounter:patient_encounter,
            hospital_percentage_clinics:hospital_percentage_clinics,
            grand_total:grand_total,
            cancel_doctor_fees:cancel_doctor_fees,
            doctor_percentage_clinics:doctor_percentage_clinics,
            encounter_id:encounter_id,
            encounter_date:encounter_date,
            paper_receipt:paper_receipt,
		},
        freeze:true,
        
		callback: function (r) {
			show_alert_message()
            var message = r.message;
            var w = window.open();
            
            w.document.open();
            w.document.write(message);
            w.document.write("</div></body></html>");
            w.document.close(); // Close the document to complete loading

            w.focus(); // Bring the window to the front
            w.print(); // Open the print dialog
        //     w.onafterprint = function() {
        //     w.close(); // Close the window after printing
        //     window.location.reload();

        // };       
            w.close(); // Close the window after printing
            window.location.reload();
        // w.close();
        
        // frappe.set_route("app", "reservation","Reservation");
    
        // var local_doc = frappe.model.get_new_doc('Reservation');
        // frappe.set_route("Form", "Reservation",local_doc.name);
            
        // frappe.model.get_new_doc(doctype)// Creates a new document object for the specified DocType.



		},
	});
    // console.log(frm );

	}

	function show_alert_message(){
		frappe.show_alert({
			message: __("Thank you for reading the notice!"),
			indicator: 'green'
		});
	}



function append_common_section(frm,currentTab) {
    let field = frm.get_field('special_doctor_percentage');

    let dependsOn = field.df.depends_on; // Access the depends_on property

    console.log(dependsOn)
    if (!tab_dict[currentTab]){
        return
    }
    if (currentTab=="laboratory_tab"||currentTab=="imaging_tab"){
        frm.set_df_property('special_doctor_percentage', 'hidden', 1); // hide the field
        frm.set_df_property('cancel_doctor_fees', 'hidden', 1); // hide the field
        
    }
    else{
        frm.set_df_property('special_doctor_percentage', 'hidden', 0); // Show the field
        frm.set_df_property('cancel_doctor_fees', 'hidden', 0); // hide the field

    }

    const tab = document.getElementById(`reservation-${currentTab}`)
    const section = document.querySelector('[data-fieldname="start_section"]'); // Element to copy
    const section2 = document.querySelector('[data-fieldname="patietn_info_section"]'); // Element to copy
    const section3 = document.querySelector('[data-fieldname="fees_section"]'); // Element to copy
    
    tab.insertBefore(section,tab.firstChild)		
    tab.insertBefore(section2, tab.children[1]);
    tab.insertBefore(section3,tab.children[2]);

}

function set_button_by_tab(frm,currentTab) {
    frm.doc.total=0
    frm.doc.grand_total=0
    frm.doc.medical_department=null
    frm.doc.clinical_procedure=[]
    frm.doc.doctor=null
    // frm.refresh_fields();
    // frm.set_value("cli")
// console.log(frm.doc.clinical_procedure)
    frm.clear_custom_buttons();
    append_common_section(frm,currentTab)
    
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
        console.log(frm.doc.clinical_procedure)
        set_clinical_procedure_tab_buttons(frm)
	}
    
	else if (currentTab=="cancel_reservation_tab"){
		set_cancel_reservation_tab_buttons(frm)
	}
    else if (currentTab=="emergency_tab"){
		set_emergency_tab_buttons(frm)
	}

    else if (currentTab=="dental_tab"){
        frm.set_value("medical_department","اسنان")
        set_dental_procedure_tab_buttons(frm)
    }
    frm.refresh_fields();

    
		set_styles()
}

frappe.ui.form.on("Reservation Invoices", {
    confirm:function(frm,cdt,cdn){
    var patient_encounter=frappe.model.get_value(cdt,cdn,'patient_encounter');
    var remaining_amount=frappe.model.get_value(cdt,cdn,'remaining_amount');
    var sales_invoice=frappe.model.get_value(cdt,cdn,'sales_invoice');
    console.log(patient_encounter)
    console.log(remaining_amount)
    console.log(sales_invoice)
    // if (remaining_amount>0){

    // }
    set_patient_follow_up(frm,patient_encounter,remaining_amount,sales_invoice)
    }
  })

  
frappe.ui.form.on("Request Invoices", {
    confirm:function(frm,cdt,cdn){
    var sales_invoice=frappe.model.get_value(cdt,cdn,'sales_invoice');
    var remaining_amount=frappe.model.get_value(cdt,cdn,'remaining_amount');
    payment_dialog(frm,"print_request",remaining_amount,sales_invoice)
    }
  })

frappe.ui.form.on("Pay Request Zero Encounters", {
    confirm:function(frm,cdt,cdn){
    var patient_encounter=frappe.model.get_value(cdt,cdn,'patient_encounter');
    var insurance=frappe.model.get_value(cdt,cdn,'insurance');
    var medical_discount =frappe.model.get_value(cdt,cdn,'medical_discount_type');

    frappe.call({
        method: "healthcare.healthcare.doctype.reservation.reservation.print_zero_invoice_request",
        args: {
          patient_encounter:patient_encounter,
          insurance:insurance,
          medical_discount: medical_discount
        },
        callback: function (r) {
            var message = r.message;
            var w = window.open();
            w.document.open();
            w.document.write(message);
            w.document.write("</div></body></html>");
            w.document.close(); // Close the document to complete loading
    
            w.focus(); // Bring the window to the front
            w.print(); // Open the print dialog
            w.onafterprint = function() {
                w.close(); // Close the window after printing
            };                               
            frm.reload_doc();
        },
      });
    
    }
  })
  
function set_patient_follow_up(frm,patient_encounter,remaining_amount,sales_invoice) {
	alert("ininfir")
    let dialog = new frappe.ui.Dialog({		
        title: __("دفع إجراءات الأسنان"),
		fields: [
              {
				label: __("Paid Amount"),
				fieldname: "paid_amount",
				fieldtype: "Float",
                default:remaining_amount||0,
				mandatory_depends_on:remaining_amount>0,
                // read_only:remaining_amount==0
            },
            {
				label: __("Paper Receipt"),
				fieldname: "paper_receipt",
				fieldtype: "Data",
				// mandatory_depends_on:1,
                // read_only:remaining_amount==0
            },

		],
        primary_action_label: 'Print',
		primary_action: function ({}) {
            // alert(request_paid_amount)

			frappe.call({
            method: 'set_patient_follow_up',
            doc:frm.doc,
            args:{
            'patient_encounter': patient_encounter,
            'paid_amount': dialog.get_value("paid_amount"),
            'paper_receipt': dialog.get_value("paper_receipt"),
            'sales_invoice': sales_invoice,
            },
            freeze: true,
			  callback: function (r) {
				// frm.refresh()
                var message = r.message;
                var w = window.open();
                
                w.document.open();
                w.document.write(message);
                w.document.write("</div></body></html>");
                w.document.close(); // Close the document to complete loading
    
                w.focus(); // Bring the window to the front
                w.print(); // Open the print dialog
                w.close(); // Close the window after printing
                // window.location.reload();
                frm.reload_doc();

                dialog.hide();	
			  },
			  error: function () {
				dialog.hide();
				frappe.msgprint({
				  message: __(" Please try again."),
				  title: __("Request Failed"),
				  indicator: "red",
				});
			  },
			});
		  },
	})
    dialog.show();
}

function set_extra_percentage(frm){
    var percent=frm.doc.hospital_percentage+frm.doc.company_percentage
    var total= frm.doc.grand_total-(frm.doc.grand_total*percent/100)
    frm.set_value("total",total)
    if (frm.doc.doctor_percentage){
    frappe.call({
        method: "healthcare.healthcare.reservation_accounts.get_doctor_profit",
        freeze: true,
        args: {
          rate: frm.doc.grand_total,
          doctor: frm.doc.doctor,
          is_consulting: frm.doc.is_consulting,
          //
        },
        callback: function (r) {
            var doctor_profit=r.message
            var total= frm.doc.total-(doctor_profit[0]*frm.doc.doctor_percentage/100)
            if (total<0){
                total = 0
            } 
            frm.set_value("total",total)
        },
      });
    }
}



