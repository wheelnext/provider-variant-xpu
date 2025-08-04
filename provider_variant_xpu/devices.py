# Copyright (c) 2025 Intel Corporation

import ctypes

# Dictionary describing Intel device IPs (platforms).
#
# Dictionary keys are represented by device IP versions which can be queried
# with Level Zero "ZE_extension_device_ip_version" API. Version value format
# is driver specific and requires decoding to the human readable format we
# use in the table below. For Intel devices values encode GMDID identifiers.
#
# Dictionary values provide the following information for each device IP:
# * `devices` - list of strings each representing device name built with this
#   device IP. These names are synonims which can be used in `ocloc` compiler
#   to build code for this device IP.
# * `compat` - device IP of the base platform. Code for the base platform can
#   be executed on all the platforms with the same compatible name.
# * `compat_name` - name assigned to device IP of the base platform. This name
#   is used in `ocloc` compiler to build code for the base platform.
_intel_devips = {
    "20.4.4": {
        "devices": ["lnl-m"],
        "compat": "20.1.0",
    },
    "20.2.0": {
        "devices": ["bmg-g31"],
        "compat": "20.1.0"
    },
    "20.1.0": {
        "devices": ["bmg-g21"],
        "compat_name": "bmg",
    },
    "12.74.4": {
        "devices": ["arl-h"]
    },
    "12.71.4": {
        "devices": ["mtl-h"],
        "compat": "12.70.4",
    },
    "12.70.4": {
        "devices": ["mtl-u", "arl-u", "arl-s"],
        "compat_name": "mtl",
    },
    "12.60.7": {
        "devices": ["pvc"],
    },
    "12.57.0": {
        "devices": ["acm-g12", "dg2-g12"],
        "compat": "12.55.8",
    },
    "12.56.5": {
        "devices": ["acm-g11", "dg2-g11", "ats-m75"],
        "compat": "12.55.8",
    },
    "12.55.8": {
        "devices": ["acm-g10", "dg2-g10", "ats-m150"],
        "compat_name": "dg2",
    },
    "12.10.0": {
        "devices": ["dg1"],
    },
    "12.4.0": {
        "devices": ["adl-n"],
    },
    "12.3.0": {
        "devices": ["adl-p", "rpl-p"],
    },
    "12.2.0": {
        "devices": ["adl-s", "rpl-s"],
    },
    "12.1.0": {
        "devices": ["rkl"],
    },
    "12.0.0": {
        "devices": ["tgllp", "tgl"],
    },
}

def get_all_ips():
    return list(_intel_devips.keys())

# See: https://github.com/intel/compute-runtime/blob/25.27.34303.6/shared/source/helpers/hw_ip_version.h
class c_intelIPVersion_t(ctypes.Union):
    _fields_ = [
        ("revision", ctypes.c_uint32, 6),
        ("reserved", ctypes.c_uint32, 8),
        ("release", ctypes.c_uint32, 8),
        ("architecture", ctypes.c_uint32, 10),
        ("value", ctypes.c_uint32)
    ]

# NOTE: The better way would be to inherit from ctypes.Union and use bit fields.
# NOTE: Unfortunately python ctypes seems to have bug handling bit fields...
class IntelDeviceIp:
    # See: https://github.com/intel/compute-runtime/blob/25.27.34303.6/shared/source/helpers/hw_ip_version.h
    ip_version = 0
    revision = 0
    release = 0
    architecture = 0

    def __init__(self, devip: ctypes.c_uint32):
        self.ip_version = devip
        self.revision = devip & 0x3F  # 6 bits value
        self.release = (devip >> 14) & 0xFF
        self.architecture = devip >> 22

    def __str__(self):
        return f"{self.architecture}.{self.release}.{self.revision}"

    def get_compat(self):
        ip = str(self)
        if ip in _intel_devips:
            if "compat" in _intel_devips[ip]:
                return _intel_devips[ip]["compat"]
        return ""

    def get_all_compat_ips(self):
        ips = [ str(self) ]
        compat = self.get_compat()
        if compat:
            ips += [compat]
        return ips
