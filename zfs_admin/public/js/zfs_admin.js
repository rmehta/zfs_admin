frappe.provide("zfs_admin")

zfs_admin.status_map = {
	"ONLINE": [__("Online"), "green", "status,=,ONLINE"],
	"OFFLINE": [__("Offline"), "darkgrey", "status,=,OFFLINE"],
	"FAULTED": [__("Faulted"), "red", "status,=,FAULTED"],
	"DEGRADED": [__("Degrated"), "orange", "status,=,DEGRADED"],
	"UNAVAIL": [__("Unavailable"), "darkgrey", "status,=,UNAVAIL"],
	"REMOVED": [__("Removed"), "darkgrey", "status,=,REMOVED"]
}
