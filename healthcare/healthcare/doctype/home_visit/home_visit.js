// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Home visit", {
	refresh(frm) {
        frm.page.set_primary_action("New Patient",function(){
            new_patient_dialog(frm)
        })
	
        frappe.call({
            method: "get_visit_fees",
            doc: frm.doc,
            callback: function (r) {
                // refresh_field("visit_fees")
                frm.set_value("visit_fees",r.message)
            },
  });

    },

    total_items(frm){
        frm.set_value("total",frm.doc.total_items+frm.doc.visit_fees);
    },
    
    visit_fees(frm){
        frm.set_value("total",frm.doc.total_items+frm.doc.visit_fees);
    }



   
});


frappe.ui.form.on("Home Visit Details", {
    item:function(frm,cdt,cdn){
        get_total(frm)
    },
    qty:function(frm,cdt,cdn){
        get_total(frm)
    },
    used_qty:function(frm,cdt,cdn){
        get_total(frm)
    }
})


function get_total(frm){
    frappe.call({
        method: "get_total",
        doc: frm.doc,
        callback: function (r) {
      frm.set_value("total_items",r.message)
      
        },
    });
}


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
                label: __("Address"),
                fieldname: "address",
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
		primary_action: function ({ patient_name,mobile,dob,gender,address,uid=null }) {
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
                address:address

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