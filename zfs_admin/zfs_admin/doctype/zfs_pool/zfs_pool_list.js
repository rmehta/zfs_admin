frappe.listview_settings['ZFS Pool'] = {
	add_fields: ["health"],
	get_indicator: function(doc) {
		return zfs_admin.status_map[doc.health];
	}
}
