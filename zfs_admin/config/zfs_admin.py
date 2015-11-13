from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("ZFS"),
			"items": [
				{
					"type": "doctype",
					"name": "ZFS Pool",
					"description": _("Group disks into one logical pool")
				},
				{
					"type": "doctype",
					"name": "ZFS Dataset",
					"description": _("Define virtual file systems in pools")
				}
			]
		},
		{
			"label": _("Setup"),
			"items": [
				{
					"type": "doctype",
					"name": "Disk",
					"description": _("List of disks")
				},
				{
					"type": "doctype",
					"name": "ZFS Command Log",
					"description": _("History of commands run by ZFS Admin")
				}
			]
		}
	]
