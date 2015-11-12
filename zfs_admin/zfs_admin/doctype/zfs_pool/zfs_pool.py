# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import os
import frappe
import libzfs
import subprocess
from frappe.model.document import Document
from zfs_admin.utils import sync_zfs

class ZFSPool(Document):
	@property
	def zpool(self):
		if not hasattr(self, "_zpool"):
			self._zpool = libzfs.ZFS().get(self.name)
		return self._zpool

	def sync(self):
		self.sync_properties()
		self.sync_vdev()
		self.update_disks()
		self.save()

	def sync_vdev(self):
		"""Sync virtual devices"""
		self.load_vdevs()
		self.fix_vdev_ordering()

	def update_disks(self):
		"""Update Disk with pool and health status"""
		for vdev in self.virtual_devices:
			if vdev.type == "disk":
				disk_name = vdev.group_name

				# TODO: diskname wit partion suffix like ada0p1
				# this needs to be synced better
				if disk_name[-2] == "p":
					disk_name = disk_name[:-2]

				disk = frappe.get_doc("Disk", disk_name)
				disk.zfs_pool = self.name
				disk.health = vdev.status
				disk.save()

	def load_vdevs(self):
		"""Load videvs from libzfs"""
		for group in ("data", "cache", "log", "spare"):
			group_vdevs = self.zpool.groups.get(group)
			added = {}

			for i, vdev in enumerate(group_vdevs):
				parent_row = self.add_vdev(vdev)

				if parent_row.type == "disk":
					parent_row.group_name = self.get_disk_name(vdev.path)
				else:
					vdev_len = len([v for v in group_vdevs if v.type==vdev.type])
					if vdev_len > 1:
						# name as mirror-1, mirror-2 etc.
						vdev_id = added.setdefault(vdev.type, 1)
						parent_row.group_name = "{0}-{1}".format(vdev.type, vdev_id)
						added[vdev.type] += 1
					else:
						parent_row.group_name = vdev.type

					for disk in vdev.children:
						row = self.add_vdev(disk, True)
						row.group_type = parent_row.type
						row.group_name = self.get_disk_name(disk.path)
						row.parent_group_name = parent_row.group_name

	def fix_vdev_ordering(self):
		"""Remove unused vdev records and order them so that the groups and disks
		appear below each other"""
		new_list = []
		for d in self.virtual_devices:
			if getattr(d, "mapped", False):
				new_list.append(d)

		# reorder in groups
		new_order = []
		for d in new_list:
			if d.parent_group_name: continue
			new_order.append(d)
			d.idx = len(new_order)
			if d.type != "disk":
				for child in new_list:
					if child.parent_group_name == d.group_name:
						new_order.append(child)
						child.idx = len(new_order)

		self.virtual_devices = new_order

	def get_disk_name(self, disk_path):
		return os.path.split(disk_path)[-1]

	def add_vdev(self, vdev, is_child=False):
		"""Add a new virtual device row"""
		row = self.get_vdev_row(vdev.guid)
		if not row:
			row = self.append("virtual_devices", {"guid": vdev.guid})

		row.status = vdev.status
		row.type = vdev.type
		row.guid = vdev.guid
		if not is_child:
			row.size = vdev.size

		row.mapped = True

		return row

	def sync_properties(self):
		"""Sync ZFS Pool properties"""

		valid_keys = self.get_valid_columns()
		percent_keys = ("capacity", "fragmentation")
		int_keys = ("dedupditto", "freeing", "guid", "leaked", "maxblocksize")

		for key, prop in self.zpool.properties.iteritems():
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
				self.set(key, value)
			else:
				# missing key
				print key

	def get_vdev_row(self, guid):
		for d in self.virtual_devices:
			if str(d.guid) == str(guid):
				return d

@frappe.whitelist()
def add(zfs_pool, type, disk1, disk2=None):
	"""zpool add"""
	frappe.has_permission("ZFS Pool", "write")

	try:
		if type.lower()=="disk":
			args = ["sudo", "zpool", "add", zfs_pool, disk1]
		else:
			args = ["sudo", "zpool", "add", zfs_pool, type.lower(), disk1, disk2]

		out = subprocess.check_output(args)
		sync_zfs()
	except subprocess.CalledProcessError as e:
		frappe.msgprint(e.output)
