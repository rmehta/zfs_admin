frappe.listview_settings['Disk'] = {
	add_fields: ["health"],
	get_indicator: function(doc) {
		return zfs_admin.status_map[doc.health];
	}
}
