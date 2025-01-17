// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Healthcare Service Unit', {
	onload: function(frm) {
		console.log(frm.doc)
		frm.list_route = 'Tree/Healthcare Service Unit';

		// get query select healthcare service unit
		frm.fields_dict['parent_healthcare_service_unit'].get_query = function(doc) {
			return {
				filters: [
					['Healthcare Service Unit', 'is_group', '=', 1],
					['Healthcare Service Unit', 'name', '!=', doc.healthcare_service_unit_name]
				]
			};
		};
	},
	refresh: function(frm) {
		frm.toggle_display(['address_html', 'contact_html'], !frm.is_new());

		if (!frm.is_new()) {
			frappe.contacts.render_address_and_contact(frm);
			frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Healthcare Service Unit'}
		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}

		frm.trigger('set_root_readonly');
		frm.set_df_property('service_unit_type', 'reqd', 1);
		frm.add_custom_button(__('Healthcare Service Unit Tree'), function() {
			frappe.set_route('Tree', 'Healthcare Service Unit');
		});

		frm.set_query('warehouse', function() {
			return {
				filters: {
					'company': frm.doc.company
				}
			};
		});
	},
	set_root_readonly: function(frm) {
		// read-only for root healthcare service unit
		frm.set_intro('');
		if (!frm.doc.parent_healthcare_service_unit) {
			frm.set_read_only();
			frm.set_intro(__('This is a root healthcare service unit and cannot be edited.'), true);
		}
	},
	allow_appointments: function(frm) {
		if (!frm.doc.allow_appointments) {
			frm.set_value('overlap_appointments', false);
		}
	},
	is_group: function(frm) {
		if (frm.doc.is_group == 1) {
			frm.set_value('allow_appointments', false);
			frm.set_df_property('service_unit_type', 'reqd', 0);
		}
		else {
			frm.set_df_property('service_unit_type', 'reqd', 1);
		}
	},
	overlap_appointments: function(frm) {
		if (frm.doc.overlap_appointments == 0) {
			frm.set_value('service_unit_capacity', '');
		}
	}
});


frappe.ui.form.on('Healthcare Service Unit', 'parent_healthcare_service_unit', function(frm) {
	if (!frm.doc.parent_healthcare_service_unit) {
	    frm.set_intro(__('This is a root healthcare service unit and cannot be edited.'), true);
	    frm.set_read_only();
	    frm.disable_save();
	} else {
	    frm.set_intro('');
	    frm.perm = frappe.perm.get_perm(frm.doc.doctype);
	    frm.enable_save();
	}
});
