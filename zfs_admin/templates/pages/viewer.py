from __future__ import unicode_literals

import frappe, os

def get_context(context):
	context.no_cache = True
	context.fs = frappe.form_dict.fs

	if not "path" in context:
		context.path = ""

	if context.fs:
		context.files = []
		path = "/" + context.fs
		for name in os.listdir(path):
			filedata = {
				"name": name,
				"is_folder": os.path.isdir(os.path.join(path, name))
			}
			if not filedata.get("is_folder"):
				filedata["size"] = os.path.getsize(os.path.join(path, name))

			context.files.append(filedata)

	else:
		context.items = frappe.db.sql("""select name, used from `tabZFS Dataset`
			where allow_portal_access=1 and type='filesystem'""", as_dict = 1)
