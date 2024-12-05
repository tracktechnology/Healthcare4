




function set_emergency_tab_buttons(frm){
    
  

    if (frm.doc.emergency_patient){
        frm.add_custom_button("تسجيل مريض طوارئ", function () {
        frappe.call({
            method: "set_patient_emergency",
            doc:frm.doc,
            freeze: true,
            callback: function (r) {
                

                frm.reload_doc();
            
            },
          });
        })
    }
}


function set_inpatient_tab_buttons(frm){
        if (frm.doc.inpatient){
        frm.add_custom_button("تسجيل مريض داخلي", function () {
            // /    console.log("set_inpatient_tab_buttons")
            

            let path  = "/room_view/index";
            let params = {
                patient: frm.doc.inpatient,
                medical_insurance:frm.doc.medical_insurance_company_inpatient
            };
            let queryString = new URLSearchParams(params).toString();


            let url = `${window.location.origin}${path}?${queryString}`;
            window.location.href = url;

        })
    }
}
