from __future__ import unicode_literals

import frappe, os
from frappe.utils import flt

def get_context(context):
	context.no_cache = True
	context.fs = frappe.form_dict.fs
	context.path = frappe.form_dict.path or ""


	if context.fs:
		context.files = []
		path = "/" + context.fs

		if context.path:
			path = os.path.join(path, context.path)

			if "/" in context.path:
				dirname = os.path.dirname(context.path)
				context.breadcrumb = {"title": dirname,
					"path": "/viewer?fs={0}&path={1}".format(context.fs, dirname)}
			else:
				context.breadcrumb = {"title": context.fs,
					"path": "/viewer?fs={0}".format(context.fs)}

		else:
			context.breadcrumb = {"title": "Home", "path": "/viewer"}

		context.title = path.strip("/")

		for name in os.listdir(path):
			filedata = {
				"name": name,
				"path": os.path.join(context.path, name) if context.path else name,
				"is_folder": os.path.isdir(os.path.join(path, name)),
			}

			if not filedata.get("is_folder"):
				filedata["size"] = os.path.getsize(os.path.join(path, name))

				if filedata["size"] > 1048576:
					filedata["size"] = str(flt(flt(filedata["size"]) / 1048576, 1)) + "M"
				elif filedata["size"] > 1024:
					filedata["size"] = str(flt(flt(filedata["size"]) / 1024, 1)) + "k"

			context.files.append(filedata)

	else:
		context.title = "Home"
		context.items = frappe.db.sql("""select name, used from `tabZFS Dataset`
			where allow_portal_access=1 and type='filesystem'""", as_dict = 1)
