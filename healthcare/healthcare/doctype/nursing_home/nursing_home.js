// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

{% include 'healthcare/healthcare/healthcare_common.js' %}
{% include 'healthcare/healthcare/doctype/reservation/reservation.js' %}


frappe.ui.form.on("Nursing Home", {
	refresh(frm) {

       
// Healthcare
frm.disable_save();

if (frm.is_dirty()){
    document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
}
content_html=
`
<div class="form-message" onclick="set_route('Reservation','clinics_tab')"> <h3>عيادات خارجية</h3></div>
<div class="form-message" onclick="set_route('Nursing Tool')"> <h3>خدمات طوارئ</h3></div>
<div class="form-message" onclick="set_new_route('Nursing Tool')"> <h3>داخلي</h3></div>
<div class="form-message" onclick="set_route('Nursing Tool')"> <h3>عناية مركزة</h3></div>
<div class="form-message" onclick="set_list_route('Nursing Tool')"> <h3>حضانات</h3></div>
<div class="form-message" onclick="set_list_route('Nursing Tool')"> <h3>عمليات</h3></div>

`

frm.get_field('html_design').$wrapper.html(content_html);
set_style()
	},
});



var e = document.querySelectorAll("[data-fieldname='html_design']")[0]
// e.style.marginLeft ='120px'
// e.style.direction="rtl"
e.style.marginRight ='85px'




window.set_style=function(){
    // Create a style element
    var style = document.createElement('style');
    style.type = 'text/css';

    var css = `
        .form-message {
            display: inline-block;
            text-align:center;
             width: 25%; margin-right: 4%; 
               cursor: pointer;
               height:65px;
                margin-bottom:5%;
                display:inline-flex;
                align-items:center;
                justify-content: center;
                background-color:#3a678b;
                text-align: center;

        }
        h3{
            color: white;
        }

    `;

    // Check if the style element supports the styleSheet property (IE)
    if (style.styleSheet) {
        style.styleSheet.cssText = css;
    } else {
        style.appendChild(document.createTextNode(css));
    }

    // Append the style element to the head
    document.head.appendChild(style);
};



window.set_route=function(doctype,tab=null){
    if (tab){
        frappe.route_options={
            "tab":tab,
            }
    }
  
        var Docname=doctype
         doctype = doctype.toLowerCase();
        doctype= doctype.replaceAll(" ", "-");  
            // frappe.model.db.clear_cache('DocType', Docname);
            // cache.clear(Docname);

		frappe.set_route("app", doctype,Docname);

}

window.set_list_route=function(doctype){
   
    frappe.set_route("List", doctype);
}

window.set_new_route=function(doctype){
    var Docname=doctype
     doctype = doctype.toLowerCase();
    doctype= doctype.replaceAll(" ", "-");
    Docname="new"+"-"+doctype+"-1"
    frappe.set_route("app", doctype,Docname);
}

window.new_patient=function(){
    new_patient_dialog();
}


 