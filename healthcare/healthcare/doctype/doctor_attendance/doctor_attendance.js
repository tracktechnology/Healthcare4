// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Doctor Attendance", {
	refresh(frm) {
        const today = frappe.datetime.get_today();
        frm.set_value("date", today)
        if (frm.is_new()){
            frappe.call({
                method: "get_slots",
                doc: frm.doc,
                callback: function (r) {
                    // frm.refresh()
                        refresh_field("doctor_attendance_details")
                },
              });
            
          }
          
	},
    
    date: function(frm){
      var day=  get_day_by_date(frm.doc.date)
        frm.set_value("day", day)

    },

    
});




frappe.ui.form.on("Doctor Attendance Details", {
    attend:function (frm, cdt, cdn) {
    check_validation(frm, cdt, cdn);

    
    },
    replacement_doctor:function (frm, cdt, cdn) {
        check_validation(frm, cdt, cdn)
        
    },
    non_attend:function (frm, cdt, cdn) {
        check_validation(frm, cdt, cdn)
        
    },

});


function check_validation(frm, cdt, cdn){
    var attend = frappe.model.get_value(cdt, cdn, 'attend') 
    var non_attend = frappe.model.get_value(cdt, cdn, 'non_attend') 
    var replacement_doctor = frappe.model.get_value(cdt, cdn, 'replacement_doctor')
    
    if (attend && (replacement_doctor||non_attend) ){
     frappe.model.set_value(cdt, cdn, 'attend',0) 
     frappe.model.set_value(cdt, cdn, 'non_attend',0) 
     frappe.model.set_value(cdt, cdn, 'replacement_doctor',null) 

    frappe.throw("Not valid check Attend  and Replacement Doctor  ") 
   }else {
    var slot_name=frappe.model.get_value(cdt, cdn, 'slot_name') 
    var from_time=frappe.model.get_value(cdt, cdn, 'from_time') 
    var to_time=frappe.model.get_value(cdt, cdn, 'to_time') 
    if (!attend){
    frappe.call({
        method: "replace_doctor",
        doc: frm.doc,
        args:{
            "slot_name":slot_name,
            "replacement_doctor":replacement_doctor,
            "from_time":from_time,
            "to_time":to_time,
        },
        callback: function (r) {
            // frm.refresh()
                // refresh_field("doctor_attendance_details")
        frm.save()

        },
      });
    }

   }
   frm.save()


}


function get_day_by_date(date) {
    var day = new Date(date).getDay();

    let weekday=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    return weekday[day]
}
