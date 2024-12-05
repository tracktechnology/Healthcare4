// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Warehouse Inventory", {
    refresh: function(frm){
        frm.add_custom_button("Load Items",function(){
            frappe.call({
                doc: frm.doc,
                method:"load_items",
                callback: function(r){
                    frm.refresh();
                }
            })
        })
        
        //View Buttons
        if(frm.doc.stock_entry) {
			frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.stock_entry,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date
					//company: frm.doc.company
				};
				frappe.set_route("query-report", "Stock Ledger");
			}, __("View"));

            frm.add_custom_button(__("Account Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.stock_entry,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date
					//company: frm.doc.company
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
    },
    request_from: function(frm) {
        frappe.call({
            doc: frm.doc,
            method:"set_to_warehouse",
            callback: function(r){
                frm.refresh();
            }
        })
	},
});