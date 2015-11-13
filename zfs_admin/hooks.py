# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "zfs_admin"
app_title = "ZFS Admin"
app_publisher = "Frappe Technologies"
app_description = "Web Admin for ZFS"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hello@frappe.io"
app_version = "0.0.1"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/zfs_admin/css/zfs_admin.css"
app_include_js = "/assets/zfs_admin/js/zfs_admin.js"

# include js, css files in header of web template
# web_include_css = "/assets/zfs_admin/css/zfs_admin.css"
# web_include_js = "/assets/zfs_admin/js/zfs_admin.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "zfs_admin.install.before_install"
after_install = "zfs_admin.utils.sync_zfs"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "zfs_admin.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"zfs_admin.tasks.all"
# 	],
# 	"daily": [
# 		"zfs_admin.tasks.daily"
# 	],
# 	"hourly": [
# 		"zfs_admin.tasks.hourly"
# 	],
# 	"weekly": [
# 		"zfs_admin.tasks.weekly"
# 	]
# 	"monthly": [
# 		"zfs_admin.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "zfs_admin.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "zfs_admin.event.get_events"
# }
