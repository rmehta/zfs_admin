# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import libzfs
from frappe.model.document import Document

class ZFSPool(Document):
	@property
	def zpool(self):
		if not hasattr(self, "_zpool"):
			self._zpool = libzfs.ZFS().get(self.name)
		return self._zpool

	def sync(self):
		self.sync_properties()
		self.sync_vdev()
		self.save()

	def sync_vdev(self):
		"""Sync virtual devices"""

		for group in ("data", "cache", "log", "spare"):
			for vdev in self.zpool.groups.get(group):
				row = self.get_vdev_row(vdev.guid)
				if not row:
					row = self.append("virtual_devices", {"guid": vdev.guid})

				row.status = vdev.status
				row.type = vdev.type
				row.guid = vdev.guid
				row.size = vdev.size

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
			if d.guid == guid:
				return d
