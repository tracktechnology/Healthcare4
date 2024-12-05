// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt
{% include 'healthcare/healthcare/healthcare_common.js' %}

let observationIdx = 0;
frappe.ui.form.on("Lab Test Tool", {
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

    add_external_lab: function(frm){
        frappe.prompt([{
            label: 'Observation ',
            fieldname: 'observation',
            fieldtype: 'Link',
            options:"Observation Template"
        },{
            label: 'External Lab',
            fieldname: 'external_lab',
            fieldtype: 'Link',
            get_query() {
                return {
                    filters: { docstatus: 1 }
                }
            },
            options:"External Lab"
        }], (values) => {
            frappe.call({
                doc: frm.doc,
                method:"add_external_lab",
                args:{observation:values.observation,external_lab:values.external_lab},
                freeze: true,
                callback: function(r){
                    frm.add_child('observation', {
                        observation: values.observation
                        // price:data[i]['price'] 
                    });
                    frm.trigger("observation")
                    frm.refresh();
                }
            })
            // frm.add_child('external_labs', {
            //     observation: values.observation,
            //     external_lab: values.external_lab
            //     // price:data[i]['price'] 
            // });
            // frm.refresh();
            // console.log(frm.doc.observation[observationIdx].observation);
            
        })
    },
    observation:function(frm) {
        

        if ((frm.doc.observation).length>0){
            // if( (frm.doc.observation).length > observationIdx){
            //     console.log(frm.doc.observation[observationIdx].observation);
                
            //     observationIdx = (frm.doc.observation).length;
            // }
           frappe.call({
               method: "healthcare.healthcare.doctype.lab_test_tool.lab_test_tool.get_item_price",
               args:{
                   items:frm.doc.observation
               },
               callback: function (r) {
                // reset_external_labs(frm);
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
//    total:function(frm){

//    },
    observation_details_remove: function(frm, cdt, cdn){
        console.log("observation_details_remove")
    },
    // observation_add: function(frm, cdt, cdn){
    //     console.log("observation_added")
    // },
    observation_details_on_form_rendered: function (frm, cdt, cdn) {
        on_render_ct("observation_details",frm)
    },
    requests_on_form_rendered: function (frm, cdt, cdn) {
        on_render_ct("requests",frm)
    },
	refresh(frm) {
        var encounter_id= Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        frm.set_value("encounter_id",encounter_id)
        if (frm.doc.requests=[]){
            get_observation_request(frm)
        }
        setInterval(function() {
            get_observation_request(frm);
        }, 30000);
        frm.set_query("observation", function() {  
            return {
                "filters": 	
                {'observation_category':"Laboratory"}
            };
        });  

  
        $('*[data-fieldname="items"]').find(".grid-remove-rows").hide();
        $('*[data-fieldname="print_items"]').find(".grid-remove-rows").hide();
        $('*[data-fieldname="observation_details"]').find(".grid-remove-rows").hide();
        $('*[data-fieldname="observation_details"]').find(".btn-open-row").hide();

        $(frm.fields_dict['observation_details'].grid.wrapper).find('.btn-open-row').hide();
        
        frm.get_field('items').grid.cannot_add_rows = true;
        frm.get_field('print_items').grid.cannot_add_rows = true;   
        frm.get_field('observation_details').grid.cannot_add_rows = true;   
   
        frm.add_custom_button("استعلامات اسعار الخدمات", function () {
            frappe.route_options={
                "tab":"laboratory_tab"
            }
        		frappe.set_route("app", "patient-inquiry","Patient Inquiry")
            });

            frm.page.set_secondary_action("Home", function () {
                frappe.set_route("app", "healthcare-home","Healthcare Home")
                }).addClass('btn-primary primary-action');	

    
        frm.disable_save();

        if (frm.is_dirty()){
            document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
        }
        get_current_tab(frm,function(currentTab){
        if (currentTab=="input_result_tab"){            
        frm.page.set_primary_action("Set Result",function(){
            frappe.call({
                method: "update_lab_items",
                doc: frm.doc,
                callback: function (r) {
                 refresh_field("items")

                 frappe.show_alert({
                    message:__('Updated result successfully'),
                    indicator:'green'
                }, 5);
                frm.reload_doc();
        
                
                }
            })    
    
        });      
    } 
    else if (currentTab == "print_result_tab" ) {
        frm.page.set_primary_action("Print Result",function(){
          
            frappe.call({
                doc: frm.doc,
                method: "get_pdf_test",
                callback: function (r) {
                    var message = r.message;
                    var w = window.open();
                    w.document.open();
                    // for (var i = 0; i <message.length; i++) {
                        var res=message+"</div></body></html>"
                        if (frm.doc.print_custom_result){
                            res+=frm.doc.print_custom_result
                        }
                        w.document.write(res);
            
                    // }
                    w.print();
                    w.close();    

              frm.trigger("print_patient")

                },
              });
            
    
        });
    }
    
		})
        frm.set_df_property('html_test_status', 'hidden', 1)
        frm.set_df_property('html_test_print', 'hidden', 1)
	},
    lab_test: function(frm){
        frappe.call({
            method: "get_lab_items",
            doc: frm.doc,
        
            callback: function (r) {
             refresh_field("items")
                refresh_field("custom_result")

            }
        })    
    },
    print_lab_test: function(frm){
        frappe.call({
            method: "get_lab_test_details",
           doc:frm.doc,
            callback: function (r) {
                refresh_field("print_items")     
                refresh_field("print_custom_result")     

    
            }
        })
    },
    reprint:function(frm){
        frm.set_intro("Can Print the latest Test of each type of Tests",'orange')
        if (!frm.doc.reprint) {
            frm.set_intro('');

        }
        frm.set_value("print_items",null)
        frm.set_value("print_custom_result",null)
        frm.trigger("print_patient")

    },
    print_patient:function(frm){
        if (!frm.doc.patient){
            frm.set_value("patient",frm.doc.print_patient)
        }
        frm.set_df_property('html_test_print', 'hidden', 1)

        var content_html=`<div></div>`;

        frappe.call({
            method: "get_print_test",
            doc: frm.doc,
        
            callback: function (r) {
              var tests=r.message;
              tests.forEach(test => {
                var div_color="green";
                if (test.is_printed){
                    div_color="orange";
                }
                content_html+=`
          <div onclick="printResult('${test.template}', '${frm.doc.name}','${test.name}','${test.observation_request}')" class="form-message ${div_color   }" style="display: inline-block ;text-align:center; width: 25%; margin-right: 1%;   cursor: pointer; width:150px;    ">${test['template']}</div>
                `;

              });
              
        frm.set_df_property('html_test_print', 'hidden', 0)


        frm.get_field('html_test_print').$wrapper.html(content_html);
            }
        })  
    },
    edit:function(frm){
        frm.trigger("patient")
        frm.set_value("items",null)
        frm.set_value("custom_result",null)
    },
    
    patient:function(frm){
        if (!frm.doc.print_patient){
            frm.set_value("print_patient",frm.doc.patient)
        }
        frm.set_df_property('html_test_status', 'hidden', 1)

        var content_html=`<div></div>`;
        var test_options=[]
        frappe.call({
            method: "get_lab_test",
            doc: frm.doc,
        
            callback: function (r) {
              var tests=r.message;

              tests.forEach(test => {
                var test_color="blue"
                if (test.status=="Completed"){
                    test_color="green"
                }
                content_html+=`
    <div onclick="setTestOptions('${test.template}', '${frm.doc.name}','${test.name}','${test.observation_request}','${test.is_external_lab}')" class="form-message ${test_color}" style="display: inline-block ;text-align:center; width: 25%; margin-right: 1%;   cursor: pointer; width:150px;    ">${test['template']}</div>
                `;
              test_options.push(test['template'])

              });
            //   frm.fields_dict['html_test_status'].df.hidden =0;
        frm.set_df_property('html_test_status', 'hidden', 0)


        frm.get_field('html_test_status').$wrapper.html(content_html);
        frm.set_df_property('test_options', 'options', test_options)

            },
          });
    },

   
});


// frappe.ui.form.on("Observation Details", {
//     refresh: function(frm,cdt,cdn){
//         alert("rrrr");
//     },

//     observation_details_add: function(frm,cdt,cdn){
//         let observation_t = frappe.model_get_value(cdt,cdn,"observation");
//         alert(observation_t);
//     }

// });
window.setTestOptions = function(template, docname,lab_test,observation_request,is_external_lab) {
    // Use Frappe's model to update the field value
    frappe.model.set_value(docname, docname, 'test_options', template);
    frappe.model.set_value(docname, docname, 'observation_request', observation_request);
    frappe.model.set_value(docname, docname, 'lab_test', lab_test);
    if(is_external_lab == 0){
        frappe.model.set_value(docname, docname, 'is_external_lab', 0);
    }else{
        frappe.model.set_value(docname, docname, 'is_external_lab', 1);

    }
    
    
}


window.printResult = function(observation, docname,lab_test_name,observation_request) {
    frappe.model.set_value(docname, docname, 'print_test',observation);  
    frappe.model.set_value(docname, docname, 'print_lab_test',lab_test_name);  
    frappe.model.set_value(docname, docname, 'print_observation_request',observation_request);  
}






function hide_add_row() {
    var add_btns=document.querySelectorAll(".grid-add-row")
	for (let i = 0; i < add_btns.length; i++) {
		add_btns[i].style.display = "none"
	}
}


frappe.ui.form.on("Observation Request Details", {
    
    refresh:function(frm,cdt,cdn){
    },
    select:function(frm,cdt,cdn){
    var observation_request=frappe.model.get_value(cdt,cdn,'observation_request');
    var patient=frappe.model.get_value(cdt,cdn,'patient');
    var reservation_type=frappe.model.get_value(cdt,cdn,'reservation_type');
        frm.set_value("r_observation_request",observation_request)
        frm.set_value("r_patient",patient)
        frm.set_value("reservation_type",reservation_type)
        // alert("Please")
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


function on_render_ct(ct_name,frm) {
    frm.fields_dict[ct_name].grid.wrapper.find(".grid-delete-row").hide();
frm.fields_dict[ct_name].grid.wrapper.find(".grid-delete-row").hide();
frm.fields_dict[ct_name].grid.wrapper.find(".grid-duplicate-row").hide();
frm.fields_dict[ct_name].grid.wrapper.find(".grid-move-row").hide();
frm.fields_dict[ct_name].grid.wrapper.find(".grid-append-row").hide();
frm.fields_dict[ct_name].grid.wrapper.find(".grid-insert-row-below").hide();
frm.fields_dict[ct_name].grid.wrapper.find(".grid-insert-row").hide();
}


function reset_external_labs(frm){
    frappe.call({
        doc: frm.doc,
        method:"reset_external_labs_on_change_in_observation",
        callback: function(r){
            frm.refresh_field("external_labs")
        }
    })
}