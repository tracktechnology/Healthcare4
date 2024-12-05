
function set_route_options(frm) {
    let data=frappe.route_options;
    if (data) {
        for([key, val] of Object.entries(data)) {
          if (key =="tab"){
           document.querySelectorAll(`[data-fieldname='${val}']`)[0].click()
           continue;
          }
          frm.set_value(key,val);
          }

        } 
    
    // frappe.route_options = {};
    frappe.route_options = null; // Set to null

    
}

function get_redirect_tabs(){
    var tab = localStorage.getItem("tab");
    localStorage.removeItem("tab");  // Removes the item with the key "myKey"
    if (tab){
        document.querySelectorAll(`[data-fieldname='${tab}']`)[0].click()
    }

// console.log(storedValue);  // Ou
}


function get_current_tab(frm,callback) {  
    var currentTab=null
    frm.$wrapper.on('shown.bs.tab', 'a[data-toggle="tab"]', function(e,val) {
         currentTab = $(e.target).attr('data-fieldname'); // Remove the '#' from the href
       return   callback(currentTab); // Execute the callback with the current tab name

        })
        // return (currentTab); //Prints 'value'
        var initialTab = frm.$wrapper.find('.nav-link.active[data-toggle="tab"]').attr('data-fieldname');
        callback(initialTab); 
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




          
function check_mandatory_fields_tab(frm) {
  let active_tab = frm.$wrapper.find('.form-section:visible'); // Select the visible section (active tab)
  let fields_in_current_tab = [];
  $.each(frm.fields_dict, function(fieldname, field) {
      if (active_tab.find('[data-fieldname="' + fieldname + '"]').length > 0) {
          if (field.df.reqd) {
              fields_in_current_tab.push(field);
              if (frm.doc[field.df.fieldname]==null || frm.doc[field.df.fieldname]=='') {
                  frappe.throw("field have missing values:  "+field.df.label)
              }

          }
      }
  });

}

function freezeForm(frm, message) {
    var freezeDiv = document.createElement('div');
    freezeDiv.id = 'custom-freeze-form';
    freezeDiv.style.position = 'absolute';
    freezeDiv.style.top = 0;
    freezeDiv.style.left = 0;
    freezeDiv.style.width = '100%';
    freezeDiv.style.height = '100%';
    freezeDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    freezeDiv.style.color = 'white';
    freezeDiv.style.display = 'flex';
    freezeDiv.style.justifyContent = 'center';
    freezeDiv.style.alignItems = 'center';
    freezeDiv.style.zIndex = 9999;
    freezeDiv.innerHTML = `<div>${message}</div>`;
    frm.$wrapper.append(freezeDiv);
}

// Function to remove the freeze overlay from the form
function unfreezeForm(frm) {
    var freezeDiv = frm.$wrapper.find('#custom-freeze-form');
    if (freezeDiv) {
        freezeDiv.remove();
    }
}



// function unfreezeUI() {
//     var freezeDiv = document.getElementById('custom-freeze-ui');
//     if (freezeDiv) {
//         document.body.removeChild(freezeDiv);
//     }
// }