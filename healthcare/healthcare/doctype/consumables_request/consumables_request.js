// Copyright (c) 2024, earthians Health Informatics Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Consumables Request", {
	refresh: function(frm){
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

frappe.ui.form.on('Clinical Procedure Item', {
	qty: function (frm, cdt, cdn) {
		let d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'transfer_qty', d.qty * d.conversion_factor);
	},

	uom: function (doc, cdt, cdn) {
		let d = locals[cdt][cdn];
		if (d.uom && d.item_code) {
			return frappe.call({
				method: 'erpnext.stock.doctype.stock_entry.stock_entry.get_uom_details',
				args: {
					item_code: d.item_code,
					uom: d.uom,
					qty: d.qty
				},
				callback: function (r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				}
			});
		}
	},

	item_code: function (frm, cdt, cdn) {
		let d = locals[cdt][cdn];
		if (d.item_code) {
			let args = {
				'item_code': d.item_code,
				'transfer_qty': d.transfer_qty,
				'quantity': d.qty
			};
			return frappe.call({
				method: 'healthcare.healthcare.doctype.clinical_procedure_template.clinical_procedure_template.get_item_details',
				args: { args: args },
				callback: function (r) {
					if (r.message) {
						let d = locals[cdt][cdn];
						$.each(r.message, function (k, v) {
							d[k] = v;
						});
						refresh_field('items');
					}
				}
			});
		}
	}
});

// List Stock items
cur_frm.set_query('item_code', 'items', function () {
	return {
		filters: {
			is_stock_item: 1
		}
	};
});