// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

{% include 'healthcare/healthcare/healthcare_common.js' %}
{% include 'healthcare/healthcare/doctype/reservation/reservation.js' %}


frappe.ui.form.on("Nursing Home Two", {
	refresh(frm) {

       
// Healthcare
frm.disable_save();

if (frm.is_dirty()){
    document.querySelectorAll("span.indicator-pill.whitespace-nowrap.orange")[0].style.display ="none";
}
content_html=
`
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Horizontal Card with Circular Image and Label</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">

    <style>
        .card {
            display: flex;
            align-items: center;
            width: 300px;
            border: 1px solid #ccc;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
            background-color: #293889;
        }

        .card img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            margin: 10px;
        }

        .card .label {
            padding: 15px;
            font-size: 26px;
            font-weight: bold;
            text-align: center;
            flex: 1;
            color: #fff;
        }

        .card:hover {
            transform: scale(1.05);
        }
        @font-face {
  font-family: 'beIN Normal';
  src: url('/http://hms2.trackintltrade.com/files/fonts/beINNormal.ttf') format('ttf');
  font-weight: normal;
  font-style: normal;
}
       
    </style>
</head>
<body style="margin-top: 30px;">
    <div class="row">
        <div class="col-md-8"><img src="http://hms2.trackintltrade.com/files/heroImage.png" alt="hospital" width="400" height="350" style="margin-left: 252px;"></div>
        <div class="col-md-4">
            <img src="http://hms2.trackintltrade.com/files/logo.png" alt="hospital" width="200" height="200">
            <div style="color: #293889;">
                <p style="font-size: 40px; font-family:'beIN Normal';margin-top: -24px; margin-left: 27px;">مستشفى </p>
                <p style="font-size: 40px; font-family:'beIN Normal';margin-top: -8px; margin-left: -60px;">   الشـفـا &nbsp;   &nbsp;التخصصي</p>
            </div>     
      </div>
      
    <div class="row col-md-12" style="margin-top: 20px; margin-left: 250px;">
        <div class="col-md-4" style="margin-right: -155px;"> <div class="card">
            <div class="label">عيادات خارجية </div>
            <img src="http://hms2.trackintltrade.com/files/clinic.png" alt="Card Image">
        </div></div>
       <div class="col-md-4" style="margin-right: -155px;"> <div class="card">
        <div class="label">خدمات الطوارئ</div>
        <img src="http://hms2.trackintltrade.com/files/amb.png" alt="Card Image">
    </div></div>
       <div class="col-md-4"> <div class="card">
        <div class="label"> داخلي</div>
        <img src="http://hms2.trackintltrade.com/files/bed.png" alt="Card Image">
    </div></div>
    </div>
    
    <div class="row col-md-12" style="margin-top: 20px; margin-left: 250px;">
        <div class="col-md-4"  style="margin-right: -155px;"> <div class="card">
            <div class="label">عتاية مركزة</div>
            <img src="http://hms2.trackintltrade.com/files/icu.png" alt="Card Image">
        </div></div>
       <div class="col-md-4"  style="margin-right: -155px;"> <div class="card">
        <div class="label">حضانات</div>
        <img src="http://hms2.trackintltrade.com/files/nur.png" alt="Card Image">
    </div></div>
       <div class="col-md-4"> <div class="card">
        <div class="label">عمليات</div>
        <img src="http://hms2.trackintltrade.com/files/emr.png" alt="Card Image">
    </div></div>
    </div>
   

</body>
</html>




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


 