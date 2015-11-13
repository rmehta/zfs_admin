# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from zfs_admin.utils import run_command

class ZFSDataset(Document):
	def take_snapshot(self, snapshot_name):
		"""zfs snapshot"""
		self.has_permission("write")
		out = run_command(["sudo", "zfs", "snapshot", "{0}@{1}".format(self.name, snapshot_name)])
		if out=="okay":
			frappe.get_doc("ZFS Pool", self.zfs_pool).sync_datasets()
			return out

	def destroy(self):
		"""zfs destroy"""
		self.has_permission("delete")
		out = run_command(["sudo", "zfs", "destroy", self.name])
		if out=="okay":
			self.delete()
			return out

@frappe.whitelist()
def take_snapshot(zfs_dataset, snapshot_name):
	return frappe.get_doc("ZFS Dataset", zfs_dataset).take_snapshot(snapshot_name)

@frappe.whitelist()
def destroy(name):
	return frappe.get_doc("ZFS Dataset", name).destroy()
