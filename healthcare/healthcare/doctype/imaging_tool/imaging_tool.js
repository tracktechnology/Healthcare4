// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/doctype/reservation/reservation_utils.js' %}
{% include 'healthcare/healthcare/healthcare_common.js' %}
frappe.ui.form.on("Imaging Tool", {

    confirm_request(frm){

        frappe.call({
            method: "set_observation_request",
            doc: frm.doc,
            freeze:true,

            callback: function (r) {
                frappe.run_serially([
                    () => {
                        frappe.show_alert({
                            message:__('Request created successfully'),
                            indicator:'green'
                        }, 5);
                    },
                    () => {
                        refresh_field("requests")
             
                        get_observation_request(frm)
                        frm.reload_doc();
            
                    },
                ])
        
            }
        }) 
    }, 
	refresh(frm) {
        var encounter_id= Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        frm.set_value("encounter_id",encounter_id)

        frm.page.set_secondary_action("Home", function () {
            frappe.set_route("app", "healthcare-home","Healthcare Home")
            }).addClass('btn-primary primary-action');	

        frm.disable_save();

        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
        }
        if (frm.doc.requests=[]){
            get_observation_request(frm)
        }
        setInterval(function() {
            get_observation_request(frm);
        }, 30000);
        frm.set_query("observation", function() {  
            return {
                "filters": 	
                {'observation_category':"Imaging"}
            };
        }); 
	},
    observation:function(frm) {

        if ((frm.doc.observation).length>0){

                
           frappe.call({
               method: "healthcare.healthcare.doctype.lab_test_tool.lab_test_tool.get_item_price",

               args:{
                   items:frm.doc.observation
               },
               callback: function (r) {
                frm.doc.observation_details=[]
                var data=r.message
                var total=0;

                for (var i=0 ;i<data.length ;i++) {
                    total+=data[i]['price']
                    frm.add_child('observation_details', {
                        observation: data[i]['observation'],
                        price:data[i]['price'] 
                    });
                    
                    frm.refresh_field('items');
                }
                 frm.doc.total=total
                 frm.doc.amount_due=total
                 if (frm.doc.company_percentage!=0||frm.doc.hospital_percentage){
                    frm.doc.amount_due=frm.doc.patient_percentage*total/100

                 }
                 refresh_field("total");
                 refresh_field("amount_due");
                refresh_field("observation_details");
               },
             });
           }
           else{
               frm.doc.total=0;
           refresh_field("total")
        
       
           }
    },
});


frappe.ui.form.on("Observation Request Details", {
    
    select:function(frm,cdt,cdn){
    var observation_request=frappe.model.get_value(cdt,cdn,'observation_request');
    var patient=frappe.model.get_value(cdt,cdn,'patient');
    var reservation_type=frappe.model.get_value(cdt,cdn,'reservation_type');
    frm.set_value("reservation_type",reservation_type)
    frm.set_value("observation_request",observation_request)
    frm.set_value("patient",patient)        // alert("Please")
    },
    cancel:function(frm,cdt,cdn){
        var observation_request=frappe.model.get_value(cdt,cdn,'observation_request');
        frappe.call({
            method: "cancel_observation_request",
            doc: frm.doc,
            args: {
                observation_request: observation_request,
            },
            callback: function (r) {
              frm.refresh()
            },
          });
    
        }
  })



function get_observation_request(frm) {
    
    frappe.call({
        method: "get_observation_request",
        doc: frm.doc,
        callback: function (r) {
         refresh_field("requests")
        color_child_table_rows(frm);

       
        }
    })
  }


  function color_child_table_rows(frm) {
    // Iterate over each row in the child table
    frm.fields_dict['requests'].grid.grid_rows.forEach(function(row) {
        let reservation_type = row.doc.reservation_type; // Get the value of the status field (or any field you want to base your condition on)
        var color="#c9c9c9"
        if (reservation_type=="Emergency"){
            color = "#AF0000"
        }
        $(row.row).css('background-color', color); 
        $(row.row).css('color', "black"); 
        $(row.row).css('font-weight', "bolder"); 
    });
}