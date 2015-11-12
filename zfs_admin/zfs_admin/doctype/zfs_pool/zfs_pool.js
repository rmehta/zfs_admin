
// dashboard
frappe.ui.form.on("ZFS Pool", {
	onload: function(frm) {
		var df = frappe.meta.get_docfield("ZFS Pool VDev", "group_name", frm.doc.name);
		df.formatter = function(value, df, options, doc) {
			if(doc.parent_group_name) {
				return '<span style="display: inline-block; margin-left: 20px;">' + value + '</span>';
			} else {
				return value;
			}
		}
	},

	refresh: function(frm) {
		frm.events.show_dashboard(frm);
		frm.events.setup_add_device(frm);
	},

	setup_add_device: function(frm) {
		frm.add_custom_button("Add Device", function() {
			var dialog = new frappe.ui.Dialog({
				title: "Add Device",
				fields: [
					{ fieldname: "type", label: __("Device Type"), fieldtype: "Select",
						options: ["", "Mirror", "RAIDZ", "Disk", "Cache", "Log"], reqd:1},
					{ fieldname: "disk1", label: __("Disk 1"), fieldtype: "Link",
						options: "Disk", filters: {"zfs_pool": ""}, reqd: 1},
					{ fieldname: "disk2", label: __("Disk 2"), fieldtype: "Link",
						options: "Disk", filters: {"zfs_pool": ""}, hidden: 1},
				],
			});

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
						zfs_pool: frm.doc.name,
						type: values.type,
						disk1: values.disk1,
						disk2: values.disk2
					},
					callback: function() {
						frm.reload_doc();
						//dialog.hide();
					}
				});

			});

			dialog.show();
		});
	},

	show_dashboard: function(frm) {
		frm.dashboard.reset();

		var size = frm.doc.size;

		// progress bar
		frm.dashboard.add_progress("Status", [
			{
				title: "Alloctaed",
				width: real_size(frm.doc.allocated) / real_size(frm.doc.size) * 100,
				progress_class: "progress-bar-default"
			},
		]);

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
