import subprocess, frappe
import libzfs


def sync_disks():
	"""Sync Disk info using geom disk list"""
	out = subprocess.check_output(["geom", "disk", "list"])
	parts = out.split("Geom name:")
	valid_keys = frappe.get_meta("Disk").get_valid_columns()

	for p in parts:
		if not p: continue
		name, props = p.split('\n', 1)
		name = name.strip()

		# insert or update new disk
		if frappe.db.exists("Disk", name):
			disk = frappe.get_doc("Disk", name)
		else:
			disk = frappe.new_doc("Disk")
			disk.name = name
		
		# parse properties
		for line in props.splitlines():
			if not line: continue
			key, value = line.split(":", 1)
			key, value = key.strip().lower(), value.strip()

			if key == "mediasize":
				value = int(value.split()[0])
			if key == "sectorsize":
				value = int(value)

			if key in valid_keys and value:
				disk.set(key, value)

		disk.save()

	frappe.db.commit()

def sync_zfs():
	"""Sync ZFS Pool information"""
	zfs = libzfs.ZFS()

	valid_keys = frappe.get_meta("ZFS Pool").get_valid_columns()
	percent_keys = ("capacity", "fragmentation")
	int_keys = ("dedupditto", "freeing", "guid", "leaked", "maxblocksize")


	for p in zfs.pools:
		if frappe.db.exists("ZFS Pool", p.name):
			pool = frappe.get_doc("ZFS Pool", p.name)
		else:
			pool = frappe.new_doc("ZFS Pool")
			pool.name = p.name

		for key, prop in p.properties.iteritems():
			value = prop.value

			# convert type
			if value in int_keys:
				value = int(value)
			if value in percent_keys:
				value = int(value[:-1])
			if value == "dedupratio":
				# dedupratio is like 1.00x, remove x
				value = int(value[:-1])

			if key in valid_keys:
				pool.set(key, value)
			else:
				# missing key
				print key

		print "Saving {0}".format(pool.name)
		pool.save()


	frappe.db.commit()

