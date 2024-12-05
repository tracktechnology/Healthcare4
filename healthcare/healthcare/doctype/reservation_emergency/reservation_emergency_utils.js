





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

function set_emergency_fees(frm,insurance_company,percentage,company_percentage,health_insurance,patient) {
    frappe.run_serially([
        () => {
            return new Promise((resolve, reject) => {
                let res = new_paper_receipt(title=`Emergency Fees = ${frm.doc.emergency_fees_amount}`);
              
                if (res) {
                    resolve(res);
                } else {
                    reject("Error generating paper receipt");
                }
            });
        },
        (res) => {
            let paper_receipt=res[0]
            let paid_amount=res[1]
            if (paid_amount!=frm.doc.emergency_fees_amount) {
                frappe.throw(`بجب تحصيل قيمه كشف الطوارئ بالكامل = ${frm.doc.emergency_fees_amount}`)
            }
            frappe.call({
                method: "set_emergency_fees",
                doc: frm.doc,
            
                args: {
                    paper_receipt:paper_receipt,
                    paid_amount: paid_amount,
                    insurance_company:insurance_company,
                    percentage:percentage,
                    company_percentage:company_percentage,
                    health_insurance:health_insurance,
                    patient:patient
                  //
                },
                callback: function (r) {
                  var doc = r.message;
                  console.log(doc);
                //   frm.refresh();
                  frm.set_value("emergency_fees",1)
                },
              });


        }
    ])
}

function set_clinics_tab_buttons(frm) {
    if (frm.doc.patient){
        if (!frm.doc.emergency_fees){
            frm.add_custom_button("دفع خدمة الطوارئ", function () {
                set_emergency_fees(
                    frm=frm,
                    insurance_company=frm.doc.medical_insurance,
                    percentage=frm.doc.percentage_doctor,
                    company_percentage=frm.doc.company_percentage_doctor,
                    health_insurance=frm.doc.health_insurance_doctor,
                    patient=frm.doc.patient,
                )
            })
            return 
    
        }
        frm.add_custom_button("حجز", function () {
            frappe.run_serially([
                () => {
                    return new Promise((resolve, reject) => {
                        let res = new_paper_receipt();
                      
                        if (res) {
                            resolve(res);
                        } else {
                            reject("Error generating paper receipt");
                        }
                    });
                },
                (res) => {
                    let paper_receipt=res[0]
                    let paid_amount=res[1]
                    set_reservation_by_method(frm,"set_request_emergency_doctor", paper_receipt,paid_amount)


                }
            ])
        })	
    }
   			

}


function set_lab_tab_buttons(frm) {
    if (frm.doc.laboratory_patient){
        if (frm.doc.lab_status!="Open Service"){
        frm.add_custom_button("دفع", function () {
        frappe.run_serially([
            () => {
                return new Promise((resolve, reject) => {
                    let res = new_paper_receipt();
                  
                    if (res) {
                        resolve(res);
                    } else {
                        reject("Error generating paper receipt");
                    }
                });
            },
            (res) => {
                let paper_receipt=res[0]
                let paid_amount=res[1]
                set_reservation_by_method(frm,"set_lab_reservation", paper_receipt,paid_amount)
            }
        ])
    })

}
frm.add_custom_button("فتح خدمة", function () {
    if (!frm.doc.emergency_fees){
        frm.add_custom_button("دفع خدمة الطوارئ", function () {
            set_emergency_fees(
                frm=frm,
                insurance_company=frm.doc.medical_insurance_lab,
                percentage=frm.doc.percentage_lab,
                company_percentage=frm.doc.company_percentage_lab,
                health_insurance=frm.doc.health_insurance_lab,
                patient=frm.doc.laboratory_patient,
            )
        })
        return 

    }
    frappe.run_serially([
        () => {
            return new Promise((resolve, reject) => {
                let res = new_paper_receipt();
              
                if (res) {
                    resolve(res);
                } else {
                    reject("Error generating paper receipt");
                }
            });
        },
        (res) => {
            let paper_receipt=res[0]
            let paid_amount=res[1]
            // set_reservation_by_method(frm,"set_lab_reservation", paper_receipt,paid_amount)
            set_reservation_by_method(frm,"set_lab_reservation",paper_receipt,paid_amount)

        }
    ])
})
    }
}
function new_paper_receipt(title="Create a paper receipt") {
    return new Promise((resolve, reject)=>{

        let d = new frappe.ui.Dialog({
            title: __(title),
            fields: [
                {
                  label: __("الرقم الدفتري"),
                  fieldname: "paper_receipt",
                  fieldtype: "Data",
                  mandatory_depends_on:true,
            
                },
                {
                    label: __("المبلغ المدفوع"),
                    fieldname: "paid_amount",
                    fieldtype: "Currency",
                    mandatory_depends_on:true,
              
                  },
            ],
            primary_action: function ({ paper_receipt,paid_amount}) {
                if (paper_receipt){
                    resolve([paper_receipt,paid_amount])
                    d.hide()
                }
              },
              primary_action_label: __("Submit"),
        })
        
    
        d.show();
    })


}
function set_imaging_tab_buttons(frm) {
    if (frm.doc.imaging_patient){
        if (!frm.doc.emergency_fees){
            frm.add_custom_button("دفع خدمة الطوارئ", function () {
                set_emergency_fees(
                    frm=frm,
                    insurance_company=frm.doc.medical_insurance_imaging,
                    percentage=frm.doc.percentage_imaging,
                    company_percentage=frm.doc.company_percentage_imaging,
                    health_insurance=frm.doc.health_insurance_imaging,
                    patient=frm.doc.imaging_patient,
                )
            })
            return 
    
        }
        if(frm.doc.imaging_status!="Open Service"){
         
        frm.add_custom_button("دفع", function () {
            frappe.run_serially([
                () => {
                    return new Promise((resolve, reject) => {
                        let res = new_paper_receipt();
                        if (res) {
                            resolve(res);
                        } else {
                            reject("Error generating paper receipt");
                        }
                    });
                },
                (res) => {
                    let paper_receipt=res[0]
                    let paid_amount=res[1]
                    set_reservation_by_method(frm,"set_imaging_reservation", paper_receipt,paid_amount)
                }
            ])
            })
        }
        frm.add_custom_button("فتح خدمة", function () {
            set_reservation_by_method(frm,"set_imaging_reservation")

        })
    }
  
}


function set_clinical_procedure_tab_buttons(frm) {
    if (frm.doc.clinical_procedure_patient){
        if (!frm.doc.emergency_fees){
            frm.add_custom_button("دفع خدمة الطوارئ", function () {
                set_emergency_fees(
                    frm=frm,
                    insurance_company=frm.doc.medical_insurance_clinical_procedure,
                    percentage=frm.doc.percentage_clinical_procedure,
                    company_percentage=frm.doc.company_percentage_clinical_procedure,
                    health_insurance=frm.doc.health_insurance_clinical_procedure,
                    patient=frm.doc.clinical_procedure_patient,
                )
            })
            return 
    
        }
    frm.add_custom_button("حجز", function () {
        
        frappe.run_serially([
            () => {
                return new Promise((resolve, reject) => {
                    let res = new_paper_receipt();
                    if (res) {
                        resolve(res);
                    } else {
                        reject("Error generating paper receipt");
                    }
                });
            },
            (res) => {
                let paper_receipt=res[0]
                let paid_amount=res[1]
                set_reservation_by_method(frm,"set_clinical_procedure_reservation", paper_receipt,paid_amount)
            }
        ])
   
})
}

}
function  set_reservation_by_method(frm,method,paper_receipt=null,paid_amount=null) {
    return frappe.call({
        method: method,
        doc: frm.doc,
        args: {
            paper_receipt: paper_receipt,
            paid_amount:paid_amount
        },
        callback: function (r) {
            if (r.message) {
                show_alert_message();
                if (paper_receipt) {
                    print_receipt(r.message);
                }
                frm.reload_doc();
                
            } 
        }
    });
}



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

