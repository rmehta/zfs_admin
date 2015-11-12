import subprocess, frappe
import libzfs

# test
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

		disk.zfs_pool = None
		disk.health = None
		disk.save()

	frappe.db.commit()

def sync_zfs():
	"""Sync ZFS Pool information"""
	sync_disks()
	zfs = libzfs.ZFS()

	for p in zfs.pools:
		if frappe.db.exists("ZFS Pool", p.name):
			pool = frappe.get_doc("ZFS Pool", p.name)
		else:
			pool = frappe.new_doc("ZFS Pool")
			pool.name = p.name

		print "Saving {0}".format(pool.name)
		pool.sync()

	frappe.db.commit()

def run_command(args):
	"""Run a command via subprocess. Returns "okay" if process when okay
		or the stderr"""
	try:
		out = subprocess.check_output(args, stderr=subprocess.STDOUT)
		return "okay"
	except subprocess.CalledProcessError as e:
		frappe.msgprint("<b>" + " ".join(args) + "</b>")
		frappe.msgprint(e.output)
		return e.output
