from __future__ import unicode_literals

import frappe
import os

from .utils import run_command

@frappe.whitelist()
def zpool_add(zfs_pool, type, disk1, disk2=None, is_new=None):
	"""zpool add or zpool create"""
	from zfs_admin.zfs_admin.doctype.zfs_pool.zfs_pool import zpool_create
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
def add_folder(zfs_dataset, folder_name, path=""):
	if not path:
		path = "/" + zfs_dataset
	return run_command(["sudo", "mkdir", os.path.join(path, folder_name)])
	return "okay"
