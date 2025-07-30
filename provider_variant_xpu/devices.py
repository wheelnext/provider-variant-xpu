# Dictionary to match device ids of Intel GPUs with respective device type
# names as known to ocloc (see `-device` option description in `ocloc compile --help`)
#
# Support notes:
# * Add newer hardware on top
# * Add device types with better performance first
devices = {
    "0xe20b": [ "bmg" ],
    "0x0bd5": [ "pvc" ],
}
