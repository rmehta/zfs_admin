
// dashboard
frappe.ui.form.on("ZFS Pool", {
	onload: function(frm) {
		// show indent if child disk
		var df = frappe.meta.get_docfield("ZFS Pool VDev", "device_name", frm.doc.name);
		df.formatter = function(value, df, options, doc) {
			if(doc.parent_device_name) {
				return '<span style="display: inline-block; margin-left: 20px;">' + value + '</span>';
			} else {
				return value;
			}
		}

		// show indicator for health
		var df = frappe.meta.get_docfield("ZFS Pool VDev", "status", frm.doc.name);
		df.formatter = function(value, df, options, doc) {
			// indicator same as ZFS Pool
			var indicator = zfs_admin.status_map[doc.status];
			return $.format('<span class="indicator {0}">{1}</span>',
				[indicator[1], indicator[0]]);
		}
	},

	refresh: function(frm) {
		frm.events.setup_add_device(frm);
		if(!frm.is_new()) {
			frm.events.show_dashboard(frm);
			frm.events.setup_destroy(frm);
			frm.events.setup_add_dataset(frm);
			frm.events.setup_view_dataset(frm);
		} else {
			setTimeout(function() {
				$(frm.wrapper).find(".empty-form-alert").html(__("Please add a device to save"));
			}, 500);
			// save happens via a device
			frm.disable_save();
		}
	},

	setup_destroy: function(frm) {
		if(frm.is_new()) return;

		frm.page.add_menu_item(__("Destroy"), function() {
			frappe.confirm(__("Do you want to destory {0}?", [frm.doc.name]), function() {
				frappe.call({
					method: "zfs_admin.zfs_admin.doctype.zfs_pool.zfs_pool.destroy",
					args: { zfs_pool: frm.doc.name },
					callback: function(r) {
						if(r.message==="okay") {
							frappe.set_route("List", "ZFS Pool");
						}
					}
				});
			});
		});
	},

	setup_add_device: function(frm) {
		var btn = frm.add_custom_button("Add Device", function() {
			var dialog = new frappe.ui.Dialog({
				title: "Add Device",
				fields: [
					{ fieldname: "pool_name", label: __("Pool Name"), fieldtype: "Data",
						hidden: frm.is_new() ? 0 : 1, reqd: frm.is_new() ? 1 : 0 },
					{ fieldname: "type", label: __("Device Type"), fieldtype: "Select",
						options: ["", "Mirror", "RAIDZ", "Disk", "Spare", "Cache", "Log"], reqd:1},
					{ fieldname: "disk1", label: __("Disk 1"), fieldtype: "Link",
						options: "Disk", filters: {"zfs_pool": ""}, reqd: 1},
					{ fieldname: "disk2", label: __("Disk 2"), fieldtype: "Link",
						options: "Disk", filters: {"zfs_pool": ""}, hidden: 1,
						description: __("You can add more disks later") },
				],
			});

			// show 2 disks when mirror-type
			dialog.get_input("type").on("change", function() {
				var value = $(this).val();
				dialog.get_field("disk2").toggle(false);
				if(value==="RAIDZ" || value==="Mirror") {
					dialog.get_field("disk2").toggle(true);
				}
			});

			dialog.set_primary_action(__("Add"), function() {
				var values = dialog.get_values();

				if(!values) return;

				frappe.call({
					method: "zfs_admin.zfs_admin.doctype.zfs_pool.zfs_pool.add",
					args: {
						zfs_pool: frm.is_new() ? values.pool_name : frm.doc.name,
						type: values.type,
						disk1: values.disk1,
						disk2: values.disk2,
						is_new: frm.is_new() ? 1 : 0
					},
					callback: function(r) {
						if(r.message==="okay") {
							if(frm.is_new()) {
								frappe.model.remove_from_locals(frm.doc.doctype, frm.doc.name);
								frappe.set_route("Form", "ZFS Pool", values.pool_name);
							} else {
								frm.reload_doc();
							}
							dialog.hide();
						}
					}
				});

			});

			dialog.show();
		});

		if(frm.is_new()) btn.addClass("btn-primary");
	},

	setup_add_dataset: function(frm) {
		frm.add_custom_button(__("Create Dataset"), function() {
			var dialog = new frappe.ui.Dialog({
				title: __("Create Dataset"),
				fields: [
					{fieldname: "dataset_name", label: "Dataset Name", fieldtype:"Data",
						reqd: 1}
				],
			});

			dialog.set_primary_action(__("Create"), function() {
				var values = dialog.get_values();

				if(!values) return;

				frappe.call({
					method: "zfs_admin.zfs_admin.doctype.zfs_pool.zfs_pool.create_dataset",
					args: {
						zfs_pool: frm.doc.name,
						dataset_name: values.dataset_name
					},
					callback: function(r) {
						if(r.message==="okay") {
							frappe.set_route("Form", "ZFS Dataset",
								frm.doc.name + "/" + values.dataset_name);
							dialog.hide();
						}
					}
				});
			});

			dialog.show();
		});
	},

	setup_view_dataset: function(frm) {
		frm.add_custom_button(__("Datasets"), function() {
			frappe.route_options = {"zfs_pool": frm.doc.name};
			frappe.set_route("List", "ZFS Dataset");
		});
	},

	show_dashboard: function(frm) {
		frm.dashboard.reset();

		var size = frm.doc.size;

		if(!size) return;

		// progress bar
		frm.dashboard.add_progress("Status", [
			{
				title: "Alloctaed",
				width: real_size(frm.doc.allocated) / real_size(frm.doc.size) * 100,
				progress_class: "progress-bar-default"
			},
		]);

		// text
		$($.format('<div class="text-muted text-center small" style="margin-top: -10px;">\
			{0} used of {1}</div>', [frm.doc.allocated, frm.doc.size]))
			.appendTo($(frm.wrapper).find(".progress-area"));

	}
});

frappe.ui.form.on("ZFS Pool VDev", {
	detach: function(frm, row_dt, row_dn) {
		// button action for detach disk
		var row = frappe.get_doc(row_dt, row_dn);
		frappe.call({
			method: "zfs_admin.zfs_admin.doctype.zfs_pool.zfs_pool.detach",
			args: {
				zfs_pool: frm.doc.name,
				disk: row.device_name
			},
			callback: function(r) {
				if(r.message==="okay") {
					frm.reload_doc();
				}
			}
		});
	}
});

var real_size = function(txt) {
	var number = txt.slice(0, -1);
	var unit = txt.slice(-1).toLowerCase();
	var conv = {
		"k": 1024,
		"m": 1024 * 1024,
		"g": 1024 * 1024 * 1024,
		"t": 1024 * 1024 * 1024 * 1024
	}
	return parseFloat(number) * conv[unit];
}
