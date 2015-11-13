from __future__ import unicode_literals

import frappe

def get_context(context):
	context.no_cache = True
	context.fs = frappe.form_dict.fs
	if not context.fs:
		context.items = frappe.db.sql("""select name, used from `tabZFS Dataset`
			where allow_portal_access=1 and type='filesystem'""", as_dict = 1)
