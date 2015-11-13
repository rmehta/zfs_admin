frappe.ui.form.on("ZFS Dataset", {
	refresh: function(frm) {
		if(frm.doc.__islocal) return;

		if(frm.doc.type=="snapshot") {

		} else {
			frm.events.setup_take_snapshot(frm);
			frm.events.setup_view_snapshots(frm);
		};

		frm.events.setup_destroy(frm);
	},
	setup_take_snapshot: function(frm) {
		frm.add_custom_button(__("Take Snapshot"), function() {
			var dialog = new frappe.ui.Dialog({
				title: __("Take Snapshot"),
				fields: [
					{fieldname:"snapshot_name", fieldtype:"Data", "label": __("Snapshot Name"),
						reqd: 1}
				]
			});

			dialog.set_primary_action(__("Take"), function() {
				var values = dialog.get_values();

				if(!values) return;

				frappe.call({
					method: "zfs_admin.zfs_admin.doctype.zfs_dataset.zfs_dataset.take_snapshot",
					args: {
						zfs_dataset: frm.doc.name,
						snapshot_name: values.snapshot_name
					},
					callback: function(r) {
						if(r.message==="okay") {
							dialog.hide();
							frappe.set_route("Form", "ZFS Dataset", frm.doc.name + "@" + values.snapshot_name);
						}
					}
				});
			});

			dialog.show();
		});
	},

	setup_destroy: function(frm) {
		frm.add_custom_button(__("Destroy"), function() {
			frappe.confirm(__("Destroy {0}", [frm.doc.name]), function() {
				frappe.call({
					method: "zfs_admin.zfs_admin.doctype.zfs_dataset.zfs_dataset.destroy",
					args: {
						name: frm.doc.name,
					},
					callback: function(r) {
						if(r.message==="okay") {
							if(frm.doc.snapshot_of) {
								frappe.set_route("Form", "ZFS Dataset", frm.doc.snapshot_of);
							} else {
								frappe.set_route("Form", "ZFS Pool", frm.doc.zfs_pool);
							}
							frappe.model.remove_from_locals(frm.doc.doctype, frm.doc.name);
						}
					}
				});
			});
		});
	},

	setup_view_snapshots: function(frm) {
		frm.add_custom_button(__("Snapshots"), function() {
			frappe.route_options = {"snapshot_of": frm.doc.name};
			frappe.set_route("List", "ZFS Dataset");
		});
	}
});
