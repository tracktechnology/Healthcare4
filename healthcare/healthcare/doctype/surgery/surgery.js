// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Surgery", {
	refresh(frm) {
		frm.add_custom_button("Create Surgery Finance",function(){
			frappe.call({
				doc: frm.doc,
				method: "create_surgery_finance",
				callback:function(r){
					frappe.show_alert("Surgery Finance Created");
				}
			})
		})
        frm.add_custom_button("Set Payment",function(){
            frappe.call({
                doc: frm.doc,
                method: "set_all_doctor_payment",
                callback: function(r){
                    frm.refresh();
                }
            })
        })
        frm.add_custom_button("New Patient",function(){
            new_patient_dialog(frm)
        })
		

	},

    surgery_type(frm){
        frappe.call({
            doc: frm.doc,
            method: "get_surgery_type_items",
            callback: function(r){
                frm.refresh();
            }
        })
    },
});


frappe.ui.form.on("Surgical Staff Detail", {
	healthcare_practitioner: function(frm,cdt,cdn){
		const practitioner = frappe.model.get_value(cdt,cdn,"healthcare_practitioner");
		if (practitioner){
			frappe.call({
				method:"healthcare.healthcare.doctype.surgery.surgery.get_surger_per_from_medical_staff_fees",
				args:{practitioner:practitioner},
				callback: function(r){
					let data = r.message;
					if (data){
						// frappe.msgprint(String(data))
						// frappe.msgprint(String(data.minimum_surgery));
						Object.keys(data).forEach(function(key) {
							frappe.model.set_value(cdt,cdn,key,data[key]);
						})
						// frappe.model.set_value(cdt,cdn,"minimum_surgery",data.minimum_surgery);
						// frappe.model.set_value(cdt,cdn,"percent_surgery",data.percent_surgery);
						frappe.model.set_value(cdt,cdn,"has_medical_staff_fees",1);
						// frm.refresh_fields()


					}
				}
			})
		}
	}
});




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