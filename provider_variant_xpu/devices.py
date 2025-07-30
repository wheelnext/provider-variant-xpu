# Dictionary to match device ids of Intel GPUs with respective device type
# names as known to ocloc (see `-device` option description in `ocloc compile --help`)
#
# Support notes:
# * Add newer hardware on top
# * Add device types with better performance first
# * Refer hardware tabel in https://dgpu-docs.intel.com/devices/hardware-table.html
devices = {
    "0x0bd5": [ "pvc" ],
    "0x0bda": [ "pvc" ],
    "0xe20b": [ "bmg" ],
    "0xe20c": [ "bmg" ],
    "0x64a0": [ "lnl" ],
    "0x6420": [ "lnl" ],
    "0x64b0": [ "lnl" ],
    "0x7d51": [ "arl-h" ],
    "0x7d67": [ "arl-s" ],
    "0x7d41": [ "arl-u" ],
    "0x7dd5": [ "mtl" ],
    "0x7d45": [ "mtl" ],
    "0x7d40": [ "mtl" ],
    "0x7d55": [ "mtl" ],
    "0x56a0": [ "dg2" ],
    "0x56a1": [ "dg2" ],
    "0x56a2": [ "dg2" ],
    "0x56a5": [ "dg2" ],
    "0x56a6": [ "dg2" ],
}
