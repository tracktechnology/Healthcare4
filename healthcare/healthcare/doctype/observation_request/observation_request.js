// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Observation Request", {
	refresh(frm) {
        // frm.disable_save();
        // if (frm.is_dirty()){
        //     document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
        // }
       if(frm.doc.status=="Pending"){
        frm.fields_dict['observation'].df.allow_on_submit =1;
    
        frm.add_custom_button("Confirm Request", function () {
            frm.set_value("status", 'Unpaid')
            frm.save('Update');
            frm.reload_doc();

            
        });
       }
        
        frm.set_query("observation", function() {  
            return {
                "filters": 	
                {'observation_category':frm.doc.observation_category}
            };
        });     
	},

    observation:function(frm) {

         if ((frm.doc.observation).length>0){

            frappe.call({
                method: "get_duplicate_observation",
                doc:frm.doc,
                args:{
                    observation:(frm.doc.observation)[(frm.doc.observation).length-1]['observation']
                },
                callback: function (r) {
                    if (r.message) {
                    frm.set_intro(`The patient has an incomplete previous Test :  ${r.message}`, 'red');
    
                }
            },
              });            
            frappe.call({
                method: "healthcare.healthcare.doctype.reservation.reservation.get_total",
                args:{
                    items:frm.doc.observation
                },
                callback: function (r) {
                  frm.doc.total=r.message
                 refresh_field("total");
                },
              });
            }
            else{
                frm.doc.total=0;
            refresh_field("total")
        
            }
    },
   
});





