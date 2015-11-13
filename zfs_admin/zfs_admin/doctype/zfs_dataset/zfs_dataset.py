# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import libzfs
from frappe.model.document import Document
from zfs_admin.utils import run_command, sync_properties

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

	def sync_zfs(self, zfs_dataset=None):
		"""sync"""
		if not zfs_dataset:
			zfs = libzfs.ZFS()
			zfs_dataset = zfs.get_dataset(self.name)

		self.sync_properties(zfs_dataset)
		self.save()

		zpool = frappe.get_doc("ZFS Pool", self.zfs_pool)
		zpool.sync_properties()
		zpool.save()

	def sync_properties(self, zfs_dataset):
		sync_properties(self, zfs_dataset.properties)
		if zfs_dataset.type.name.lower()=="snapshot":
			self.snapshot_of = zfs_dataset.parent.name
