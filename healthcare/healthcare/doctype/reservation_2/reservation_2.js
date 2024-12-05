// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reservation 2", {
	before_load(frm) {
        var dialog = new frappe.ui.Dialog({
            title: __("دفع إجراءات الأسنان"),
            fields: [
                {
                    label: __("Action"),
                    fieldname: "action",
                    fieldtype: "Select",
                    options: ["Select Patient","New Patient"],
                    default:"Select Patient"
                },

                {
                    label: __("Patient"),
                    fieldname: "patient",
                    fieldtype: "Link",
                    options: "Patient",
                },
                {
                    label: __("Medical Insurance"),
                    fieldname: "medical_insurance",
                    fieldtype: "Link",
                    options: "Medical Insurance",
                },
                {
                    label: __("Medical insurance company"),
                    fieldname: "medical_company",
                    fieldtype: "Link",
                    options: "Medical insurance company",
                    depends_on: "eval: doc.medical_insurance",  // Visibility based on medical_insurance

                },
                {
                    fieldtype: "Column Break"
                },
                {
                    label: __("Patient Name"),
                    fieldname: "patient_name",
                    fieldtype: "Data",
                    mandatory_depends_on:true,
                    depends_on: "eval: doc.action=='New Patient'", 
              
                  },
                  {
                      label: __("Gender"),
                      fieldname: "gender",
                      fieldtype: "Link",
                      options:"Gender",
                      mandatory_depends_on:true,
                      depends_on: "eval: doc.action=='New Patient'", 
                    
                    },
                    {
                      label: __("Mobile"),
                      fieldname: "mobile",
                      fieldtype: "Data",
                      mandatory_depends_on:true,
                      depends_on: "eval: doc.action=='New Patient'", 
                  
                    },
                    {
                      label: __("Age"),
                      fieldname: "age",
                      fieldtype: "Data",
                      mandatory_depends_on:true,
                      depends_on: "eval: doc.action=='New Patient'", 
                  
                    },
                    {
                      label: __("Address"),
                      fieldname: "address",
                      fieldtype: "Data",
                      mandatory_depends_on:true,
                      depends_on: "eval: doc.action=='New Patient'", 
                  
                    },
                    {
                      label: __("National ID"),
                      fieldname: "uid",
                      fieldtype: "Data",
                      depends_on: "eval: doc.action=='New Patient'", 
                  
                    },
                    {
                        fieldtype: "Section Break"
                    },
                    {
                        label: __("Clinics"),
                        fieldname: "clincs",
                        fieldtype: "Button",
                    },
                    {
                        label: __("Clinical Procedure"),
                        fieldname: "imaging",
                        fieldtype: "Button",
                    },
                    {
                        label: __("Pay Requests"),
                        fieldname: "imaging",
                        fieldtype: "Button",
                    },
                
                    {
                        fieldtype: "Column Break"
                    },
                    {
                        label: __("Lab"),
                        fieldname: "lab",
                        fieldtype: "Button",
                    },
                    {
                        label: __("Dental"),
                        fieldname: "imaging",
                        fieldtype: "Button",
                    },
                    
                    {
                        fieldtype: "Column Break"
                    },
                    {
                        label: __("Imaging"),
                        fieldname: "imaging",
                        fieldtype: "Button",
                    },
                    {
                        label: __("Cancel Reservation"),
                        fieldname: "imaging",
                        fieldtype: "Button",
                    },
                    {
                        fieldtype: "Column Break"
                    },
                    
         
                    // {
                    //     fieldtype: "Column Break"
                    // },
                    // {
                    //     fieldtype: "Column Break"
                    // },
                    
                    // {
                    //     fieldtype: "Column Break"
                    // },
                    
            ],
            static:true,
    //         primary_action_label: 'Print',
    //         primary_action: function () {
    //             dialog.hide();
    //         },
    //         secondary_action_label: __("Exit"),
    // secondary_action() {
    //   let prev_route = frappe.get_prev_route();
    //   prev_route.length ? frappe.set_route(...prev_route) : frappe.set_route();
    // },
    // secondary_action_label: __("create"),
    // secondary_action() {
    //   let prev_route = frappe.get_prev_route();
    //   prev_route.length ? frappe.set_route(...prev_route) : frappe.set_route();
    // },
        });
        

        dialog.fields_dict["medical_company"].get_query = function() {
            let selectedInsurance = dialog.get_value("medical_insurance");
            return {
                filters: {
                    "company_name": selectedInsurance  // Assuming the "insurance" field in "Medical insurance company" matches
                }
            };
        };
    },
    
    health_insurance_clinics(frm){
    // insertElements();  // Call the async function
        // frm.refresh();
        alert("HealthInsurance")
    },
    refresh(frm){
        manipulateTabPanels()
    }


    
});
async function manipulateTabPanels() {
        const tabPanels = Array.from(document.querySelector('[role="tabpanel"]'))
            .filter(panel => panel.id !== 'reservation-2-master_sections_tab')[0];
    
        const elementToCopy = document.querySelector('[data-fieldname="patient"]'); // Element to copy
    
        console.log(tabPanels)    
        const fieldValue = elementToCopy.outerHTML; // Get the inner HTML of the element
    
        // for (const panel of tabPanels) {
        //     await new Promise(resolve => setTimeout(resolve, 500)); // Async delay
    
            // Use insertAdjacentHTML to insert the copied value directly
            // panel.insertAdjacentElement('beforeend', elementToCopy.cloneNode(true))
            // panel.appendChild(elementToCopy .cloneNode(true)); 
// panel.appe

tabPanels.appendChild(elementToCopy);

            // console.log(`Inserted copied value into tabpanel with id: ${panel.id}`);
        // }
    
}

// Call the async function to manipulate the tab panels
