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
            frm.add_custom_button("تسجيل", function () {
                set_patient_due(frm, [{"item_group":"كشف","doctor":frm.doc.doctor,
                "reservation_type":frm.doc.reservation_type}],
                "request_doctor","Emergency")
            })
    }
}
function set_lab_tab_buttons(frm) {
    if (frm.doc.laboratory_patient){
 
        frm.add_custom_button("تسجيل", function () {
            // var items=set_items(frm,frm.doc.laboratory)
            // set_patient_due(frm,items,"observation",frm.doc.laboratory_patient)
            set_observation_request(frm,"Laboratory")
        })
    }
}

function set_imaging_tab_buttons(frm) {
    if (frm.doc.imaging_patient){
    
        frm.add_custom_button("تسجيل", function () {
            // var items=set_items(frm,frm.doc.imaging)
            // set_patient_due(frm,items,"observation",frm.doc.imaging_patient)
            set_observation_request(frm,"Imaging",frm.doc.imaging_type)
       
        })
    }
  
}


function set_clinical_procedure_tab_buttons(frm) {
    if (frm.doc.clinical_procedure_patient){
        frm.add_custom_button("تسجيل", function () {
            // var items=set_items(frm,frm.doc.clinical_procedure)
            // set_patient_due(frm,items,"clinical_procedure","Clinical Procedure")
            frappe.call({
                method: "set_clinical_procedure_items",
               doc:frm.doc,
                callback: function (r) {
                    show_alert_message()
                    frm.reload_doc();
        
        
                },
              });
        })
   
}

}



function set_medications_tab_buttons(frm) {
    if (frm.doc.medication_patient){
    
        frm.add_custom_button("تسجيل", function () {
            var data=frm.doc.drug_prescription
            var items=[]
            data.forEach((item)=>{
            items.push({"item_name":item["medication"],"reservation_type":frm.doc.reservation_type})
            })

            set_patient_due(frm,items,"medication","Medications")
        })
    }
  
}

function show_alert_message(){
    frappe.msgprint("Added Successfully")
	// frappe.show_alert({
	// 	message: __("Thank you for reading the notice!"),
	// 	indicator: 'green'
	// });
}




function set_items(frm,data){
            var items=[]
            data.forEach((item)=>{
            items.push({"item_name":item["observation"],"reservation_type":frm.doc.reservation_type})
            })
            return items
}


function set_patient_due(frm,items,items_type,department) {
    frappe.call({
        method: "set_patient_items",
       doc:frm.doc,
        args: {
            patient_name: frm.doc.patient_name,
            items:items,
            items_type:items_type,
            department:department,
        },
        callback: function (r) {
            show_alert_message()
            frm.reload_doc();
        },
      });
}

function set_observation_request(frm,observation_type,imaging_type=null)
{

    frappe.call({
        method: "set_observation_request",
       doc:frm.doc,
        args: {
            observation_type:observation_type,
            imaging_type:imaging_type
        },
        callback: function (r) {
            show_alert_message()

            frm.reload_doc();


        },
      });

}