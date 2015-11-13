from __future__ import unicode_literals

import frappe
import os
import base64
import mimetypes
from werkzeug.wrappers import Response
from frappe.utils import cint

from .utils import run_command

@frappe.whitelist()
def zpool_add(zfs_pool, type, disk1, disk2=None, is_new=None):
	"""zpool add or zpool create"""
	from .zfs_admin.doctype.zfs_pool.zfs_pool import zpool_create
	if cint(is_new):
		return zpool_create(zfs_pool, type, disk1, disk2)
	else:
		zfs_pool = frappe.get_doc("ZFS Pool", zfs_pool)
		return zfs_pool.zpool_add(type, disk1, disk2)

@frappe.whitelist()
def zpool_detach(zfs_pool, disk):
	"""zpool detach"""
	zfs_pool = frappe.get_doc("ZFS Pool", zfs_pool)
	return zfs_pool.zpool_detach(disk)

@frappe.whitelist()
def zpool_destroy(zfs_pool):
	"""zpool destroy"""
	zfs_pool = frappe.get_doc("ZFS Pool", zfs_pool)
	return zfs_pool.zpool_destroy()

@frappe.whitelist()
def zpool_sync(zfs_pool):
	zfs_pool = frappe.get_doc("ZFS Pool", zfs_pool)
	if zfs_pool.has_permission("write"):
		zfs_pool.sync()

@frappe.whitelist()
def zfs_create(zfs_pool, dataset_name):
	frappe.has_permission("ZFS Dataset", "write")
	if run_command(["sudo", "zfs", "create", zfs_pool + "/" + dataset_name])=="okay":
		frappe.get_doc("ZFS Pool", zfs_pool).sync_datasets();
		return "okay"

@frappe.whitelist()
def zfs_snapshot(zfs_dataset, snapshot_name):
	return frappe.get_doc("ZFS Dataset", zfs_dataset).take_snapshot(snapshot_name)

@frappe.whitelist()
def zfs_destroy(name):
	return frappe.get_doc("ZFS Dataset", name).destroy()

@frappe.whitelist()
def add_folder(fs, folder_name, path=""):
	"""Add a folder in a given dataset"""
	folder_path = get_path(fs, path)
	return run_command(["sudo", "mkdir", os.path.join(folder_path, folder_name)])
	return "okay"

@frappe.whitelist()
def upload_file(filedata, filename, fs, path=""):
	"""Save a file in the filesystem"""
	zfs_dataset = frappe.get_doc("ZFS Dataset", fs)
	zfs_dataset.has_permission("write")

	if isinstance(filedata, unicode):
		filedata = filedata.encode("utf-8")

	if "," in filedata:
		filedata = filedata.rsplit(",", 1)[1]
	filedata = base64.b64decode(filedata)

	file_path = get_path(fs, path)

	# save in tmp as there may be no permission in target dataset
	tmp_path = os.path.join("/tmp", filename).encode("utf-8")
	with open(tmp_path, "w+") as w:
		w.write(filedata)

	if run_command(["sudo", "mv", tmp_path, file_path])=="okay":
		zfs_dataset.sync_zfs()
		return "okay"

@frappe.whitelist()
def download(fs, file_path):
	"""Download file"""
	frappe.get_doc("ZFS Dataset", fs).has_permission("read")
	file_path = get_path(fs, file_path)

	filename = os.path.basename(file_path)

	try:
		f = open(file_path, 'rb')
		frappe.local.response.filename = filename
		frappe.local.response.filecontent = f.read()
		frappe.local.response.type = "download"

	except IOError:
		raise frappe.NotFound


def get_path(fs, path):
	"""Get path with filesyste mount, currently uses /"""
	out = "/" + fs
	if path:
		out = os.path.join(out, path)

	return out.encode("utf-8")
