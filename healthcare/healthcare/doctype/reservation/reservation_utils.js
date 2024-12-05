
let check_and_set_availability = function(frm) {
    if (!frm.doc.doctor||!frm.doc.patient){
        frappe.throw("برجاء ادخال جميع البيانات ")
    }
        
    var reservation_type=null
    let d = new frappe.ui.Dialog({
      
        title: __('Available slots'),
        fields: [
            { fieldtype: 'Data', default: frm.doc.doctor, read_only: 1, fieldname: 'practitioner', label: 'Healthcare Practitioner' },
            { fieldtype: 'Check', read_only:0, fieldname: 'is_consultation', label: 'Consultation'},

            { fieldtype: 'Column Break' },
            { fieldtype: 'Select', reqd: 1, fieldname: 'appointment_date', label: 'Date',  
            options:practitioner_days,        
             },

            { fieldtype: 'Data',reqd:1,fieldname:'paper_receipt',label:'الرقم الدفتري'},

            // { fieldtype: 'Column Break' },
            { fieldtype: 'Section Break' },
            { fieldtype: 'HTML', fieldname: 'available_slots' },
        ],
    })

    d.set_values({
        'practitioner': frm.doc.doctor,
        'appointment_date':practitioner_days[0],
        'is_consultation':frm.doc.is_consulting
    });

    d.fields_dict['appointment_date'].df.onchange = () => {get_slots()}
    d.fields_dict['is_consultation'].df.onchange = () => {
        get_slots()  
        frm.set_value("is_consulting",d.get_value("is_consultation"))
        if (frm.doc.is_consulting==0){
            reservation_type="كشف"
        }
        else{
            reservation_type="أستشاره"
        }
    d.fields_dict['paper_receipt'].df.onchange = () => {get_slots()}

         
    }

        function get_slots(){
            
             
            frappe.call({
            method: "healthcare.healthcare.doctype.reservation.reservation.get_available_slots",
            args: {
                day: d.get_value("appointment_date"),
                doctor: d.get_value('practitioner'),
                is_consultation:frm.doc.is_consulting
            },
            callback: function (r) {
                var fees=frm.doc.total;
                var service_unit=frm.doc.medical_department;
                var slots=r.message
                var content_html=`  <div class="slot-info text-center";
                <span><b>
                ${__('Fees: ')} </b> ${fees} L.E
                </span><br>
            <span><b> ${__('Service Unit: ')} </b> ${service_unit}</span><br>
            <span><b> ${__('Reservation Type: ')} </b> ${reservation_type}</span><br>`

            

                slots.forEach(slot => {
                    var count_class=null
                    var available=null
                    if (slot.available>0){
                        count_class='badge-success'
                        available=slot.available
                        // available="Full"

                    }
                    else{
                        count_class='badge-danger'
                        available="Full"
                    }
                content_html+=
                    `
                   <button onclick="if ('${available}'!='Full')
                   {set_reservation('${slot.from_time}','${frm.doc.patient}','${slot.date}','${frm.doc.total}',
                   '${frm.doc.doctor}','${frm.doc.medical_department}','${service_unit}','${frm.doc.medical_insurance}',
                   '${frm.doc.percentage}','${frm.doc.company_percentage}',
                   '${frm.doc.hospital_percentage}','${frm.doc.health_insurance}',
                   '${d.get_value('is_consultation')}','${frm.doc.patient_encounter}','${frm.doc.grand_total}',
                   '${frm.doc.cancel_doctor_fees}','${frm.doc.doctor_percentage}','${frm.doc.encounter_id}',
                   '${frm.doc.reservation_date}','${d.get_value("paper_receipt")}')}else{frappe.throw('Not able to reservation')}" class="btn btn-secondary" >
                   
                    ${slot.from_time} -${slot.to_time}
                    <br>
                    <span class='badge ${count_class}' >${available} </span>
                    
                    </button>
                    `    
                });
                        
                d.get_field('available_slots').$wrapper.html(content_html);
            
            },
          });

    
        
        
        
    };
    

    d.show();
  
}

function remove_buttons(frm) {
    
}

function set_button_by_tab(frm,clinics_tab=false) {
	
	if (clinics_tab){
		frm.add_custom_button("استعلام مواعيد عيادة", function () {
					
                frappe.route_options={
                    "doctor":frm.doc.doctor,
                    "medical_department":frm.doc.medical_department
                }
                frappe.set_route("app", "appointment-tool","Appointment Tool");

			});
        frm.add_custom_button("استعلام مواعيد طبيب", function () {
            
            frappe.route_options={
                "doctor":frm.doc.doctor,
                "medical_department":frm.doc.medical_department
                }
            frappe.set_route("app", "appointment-tool","Appointment Tool");
    
        });
        frm.add_custom_button("حجز", function () {
            
            check_and_set_availability(frm)
        })
				
				 set_styles()

	}

}


function set_styles(){	
	var btns=document.getElementsByClassName("btn btn-default ellipsis")
	for (let i = 0; i < btns.length; i++) {
		btns[i].style.backgroundColor = '#3a87ad'
		btns[i].style.color = 'white'
	}
	var  primary_btn=document.getElementsByClassName("btn btn-primary btn-sm primary-action")
	for (let i = 0; i < primary_btn.length; i++) {
		primary_btn[i].style.backgroundColor = '#9B67E6'
		// btns[i].style.color = 'white'
	}
	// var primary_btn=document.getElementsByClassName("btn btn-primary btn-sm primary-action")[0].style.backgroundColor="#9B67E6"
}


function set_clinics_tab_buttons(frm) {
    if (frm.doc.patient){
        frm.add_custom_button("حجز", function () {
            check_and_set_availability(frm)
        })	
    }
   
}


function set_lab_tab_buttons(frm) {
    if (frm.doc.patient){
        
   
        frm.add_custom_button("فتح خدمة", function () {
            
            frappe.call({
                method: "set_lab_reservation",
                doc: frm.doc,
                freeze: true,
                callback: function (r) {
                    frm.refresh_fields();
                },
              });
            // set_reservation_by_method(frm,"set_lab_reservation")

    })
    }
}
// function new_paper_receipt() {
//     return new Promise((resolve, reject)=>{

//         let d = new frappe.ui.Dialog({
//             title: __("Create a paper receipt"),
//             fields: [
//                 {
//                   label: __("الرقم الدفتري"),
//                   fieldname: "paper_receipt",
//                   fieldtype: "Data",
//                   mandatory_depends_on:true,
            
//                 },
//                 {
//                     label: __("المبلغ المدفوع"),
//                     fieldname: "paid_amount",
//                     fieldtype: "Currency",
//                     mandatory_depends_on:true,
              
//                   },
//             ],
//             primary_action: function ({ paper_receipt,paid_amount}) {
//                 if (paper_receipt){
//                     resolve([paper_receipt,paid_amount])
//                     d.hide()
//                 }
//               },
//               primary_action_label: __("Submit"),
//         })
        
    
//         d.show();
//     })


// }
function set_imaging_tab_buttons(frm) {
    if (frm.doc.patient){
      
         
        frm.add_custom_button("فتح خدمة", function () {
            
            frappe.call({
                method: "set_imaging_reservation",
                doc: frm.doc,
                freeze: true,
                callback: function (r) {
                    frm.refresh_fields();
                },
              });

    })
    }

}
  



function set_clinical_procedure_tab_buttons(frm) {
 //   frm.set_value("clinical_procedure",[])
    if (frm.doc.patient){
        // frm.set_df_property('clinical_procedure', 'hidden', 0)
        // refresh_field("clinical_procedure")

    frm.add_custom_button("حجز", function () {
        // set_reservation_by_method(frm,"set_clinical_procedure_reservation",tr///ue)
        payment_dialog(frm,"set_clinical_procedure_reservation",frm.doc.total)
        
})
}
}



function set_dental_procedure_tab_buttons(frm) {
    if (frm.doc.patient){

    frm.add_custom_button("حجز", function () {
        set_dental_reservation(frm)
})
}
}

function set_cancel_reservation_tab_buttons(frm) {
    if (frm.doc.cancel_patient){

    frm.add_custom_button("إلغاء الحجز", function () {
        var selectedRows = cur_frm.doc.reservations.filter(row => row.__checked);
        if (selectedRows.length==0){
            frappe.throw("من فضلك قم بأختيار العناصر من الجدول")

        }
        frappe.call({
            method: "cancel_reservation",
            doc: frm.doc,
            freeze: true,
            args:{
                items:selectedRows
            },
            callback: function (r) {
                frm.reload_doc();
            
            },
          });


    })

    frm.add_custom_button("حذف الفواتير", function () {
        var selectedRows = cur_frm.doc.invoices.filter(row => row.__checked);

        frappe.call({
            method: "delete_invoices",
            doc: frm.doc,
            args:{
                items:selectedRows
            },
            callback: function (r) {
                frm.reload_doc();
            
            },
          });


    })
}
}



// function  set_reservation_by_method(frm,method,is_print=false) { 
//     var paper_receipt=null;
//     var paid_amount =null;
//     paid_amount,paper_receipt=payment_dialog(frm,frm.doc.total);

    
// }



function getDayIndex(day) {
    let days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    return days.indexOf(day);
}


function sortDays(days) {
// Get today's day name
let today = new Date().toLocaleDateString("en-US", { weekday: "long" });

// Split the array into two parts: days before today and days after today
let beforeToday = days.filter(day => getDayIndex(day) < getDayIndex(today));
let afterToday = days.filter(day => getDayIndex(day) >= getDayIndex(today));

// Sort each part separately
beforeToday.sort((a, b) => getDayIndex(a) - getDayIndex(b));
afterToday.sort((a, b) => getDayIndex(a) - getDayIndex(b));

// Concatenate the sorted parts
let sortedDays = afterToday.concat(beforeToday);

return sortedDays
}


function get_day_by_date(date) {
    var day = new Date(date).getDay();

    let weekday=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    return weekday[day]
}


//function get_date_by_day( dayOfWeek) 
function get_date_by_day(day) {
	var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
	var today = new Date();
	var targetDay = days.indexOf(day);
	var currentDay = today.getDay();
	var offset = (targetDay - currentDay + 7) % 7;
	today.setDate(today.getDate() + offset);
	
	return today.toISOString().slice(0,10);
  }
  

function print_receipt(message) {
	var w = window.open();
	w.document.open();
	//  w.document.write("<div class='col-xs-12' style='margin=0mm;padding=0mm'>");
	w.document.write(message);
	w.document.write("</div></body></html>");
	//  w.document.close();
	// // fappe.msgprint("testing");
	w.print();
	w.close();

}


function show_alert_message(){
	frappe.show_alert({
		message: __("Thank you for reading the notice!"),
		indicator: 'green'
	});
}


function set_dental_reservation(frm) {
    
	let dialog = new frappe.ui.Dialog({
		title: __("دفع إجراءات الأسنان"),
		fields: [
              {
				label: __("Paid Amount"),
				fieldname: "paid_amount",
				fieldtype: "Float",
                default:frm.doc.total,
				mandatory_depends_on:frm.doc.total>0,
                // read_only:remaining_amount==0
            },
            {
				label: __("paper Receipt"),
				fieldname: "paper_receipt",
				fieldtype: "Data",
				mandatory_depends_on:frm.doc.total>0,
                // read_only:remaining_amount==0
            }

		],
        primary_action_label: 'Print',
		primary_action: function ({ paid_amount}) {
            // alert(request_paid_amount)
            frm.set_value("request_paid_amount",paid_amount)
            
            frappe.call({
                method: "set_dental_procedure_reservation",
                doc: frm.doc,
                args:{
                    paper_receipt: dialog.get_value("paper_receipt"),
                    paid_amount: dialog.get_value("paid_amount"),
                     
                },
                freeze:true,
                callback: function (r) {
                    if (r.message) {
                        
                        show_alert_message();
                        
                            var message = r.message;
                            var w = window.open();
                            
                            w.document.open();
                            w.document.write(message);
                            w.document.write("</div></body></html>");
                            w.document.close(); // Close the document to complete loading
                    
                            w.focus(); // Bring the window to the front
                            w.print(); // Open the print dialog
                            w.close(); // Close the window after printing
        
                        frm.reload_doc();
                    } 
                },
            });
            
            dialog.hide();	
		  
        },
	})

    dialog.show();

}



function  payment_dialog(frm,method,paid_amount,sales_invoice=null){
    // Create a new Frappe dialog
    var read_only=0
    if (tab_dict[current_tab]=="Clinics"){
      read_only=1
    }
  let dialog = new frappe.ui.Dialog({
      fields: [
          {
              label: 'Paper Receipt',
              fieldname: 'paper_receipt',
              fieldtype: 'Data',  // This field is a simple text input
              reqd: 1  // Makes the field mandatory
          },
          {
              label: 'Paid Amount',
              fieldname: 'paid_amount',
              fieldtype: 'Currency',  // This field is a currency input
              reqd: 1 , // Makes the field mandatory
              default:paid_amount,
              read_only: read_only
          },
      ],
      primary_action_label: 'Submit',
      primary_action(values) {
            // retutn [,dialog.get_value("paper_receipt")]
            let args={
                paper_receipt: dialog.get_value("paper_receipt"),
                paid_amount: dialog.get_value("paid_amount"),

            }
            if (sales_invoice){
                args["sales_invoice"] = sales_invoice;

            }
            frappe.call({
                method: method,
                doc: frm.doc,
                args:args,
                freeze:true,
                callback: function (r) {
                    if (r.message) {
                        
                        show_alert_message();
                        
                            var message = r.message;
                            var w = window.open();
                            
                            w.document.open();
                            w.document.write(message);
                            w.document.write("</div></body></html>");
                            w.document.close(); // Close the document to complete loading
                    
                            w.focus(); // Bring the window to the front
                            w.print(); // Open the print dialog
                            w.close(); // Close the window after printing
        
                        frm.reload_doc();
                    } 
                },
            });
  
            dialog.hide();
      }
  });
  
  // Show the dialog
  dialog.show();
  }