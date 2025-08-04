# Copyright (c) 2025 Intel Corporation

# Minimal Python binding for the Intel Level Zero library:
# * https://github.com/oneapi-src/level-zero
#
# Binding works for Windows and Linux. On Linux Level Zero library is loaded
# by "libze_loader.so.1" name using default search algorithm. On Windows it's
# loaded as "ze_loader.dll" and searched in "System32" folder. "WINDIR"
# environment variable can be used to adjust default folder location (C:\Windows).
#
# "XPU_DEBUG_ZE" environment variable can be used to print debug logs.


import os
import platform
import threading

from ctypes import *

_g_debug = (os.getenv("XPU_DEBUG_ZE", "0").lower() in ["true", "1"])

def _zePrint(*args, **kwargs):
    if _g_debug:
        print(*args, **kwargs)

g_zelib = None
g_zelib_lock = threading.Lock()

def _LoadZe():
    global g_zelib

    g_zelib_lock.acquire()
    try:
        if g_zelib == None:
            try:
                system = platform.system()
                if system == "Linux":
                    g_zelib = CDLL("libze_loader.so.1")
                elif system == "Windows":
                    g_zelib = CDLL(os.path.join(
                        os.getenv("WINDIR", "C:/Windows"),
                        "System32/ze_loader.dll"))
            except OSError as e:
                pass
            if g_zelib == None:
                raise FileNotFoundError("Failed to open L0 library")
    finally:
        g_zelib_lock.release()


ZE_RESULT_SUCCESS = 0


def _zeCheck(ret):
    if ret != ZE_RESULT_SUCCESS:
        raise ValueError(f"L0 library call failed with {hex(ret)}")


g_zelib_cache = ( dict() )


def _zeGetFunctionPointer(name):
    global g_zelib

    _zePrint(f"_zeGetFunctionPointer({name}): looking...")

    if name in g_zelib_cache:
        _zePrint(f"_zeGetFunctionPointer({name}): found (cache)")
        return g_zelib_cache[name]

    g_zelib_lock.acquire()
    try:
        if g_zelib == None:
            raise ValueError("L0 library not loaded")
        g_zelib_cache[name] = getattr(g_zelib, name)
        _zePrint(f"_zeGetFunctionPointer({name}): found")
        return g_zelib_cache[name]
    finally:
        g_zelib_lock.release()

# Declaring opaque handles as just c_void_p would work on Linux,
# but fail on Windows. Thus, need to declare opaque structure
# and further declare handle as a pointer to this structure.
class _c_ze_driver_handle_t(Structure):
    pass  # opaque handle

class _c_ze_device_handle_t(Structure):
    pass  # opaque handle

c_ze_driver_handle_t = POINTER(_c_ze_driver_handle_t)
c_ze_device_handle_t = POINTER(_c_ze_device_handle_t)

ZE_MAX_DEVICE_NAME = 256
ZE_MAX_DEVICE_UUID_SIZE = 16

ZE_INIT_FLAG_GPU_ONLY = 1 << 0
ZE_INIT_FLAG_VPU_ONLY = 1 << 1
ZE_INIT_FLAG_FORCE_UINT32 = 0x7fffffff

ZE_INIT_DRIVER_TYPE_FLAG_GPU = 1 << 0
ZE_INIT_DRIVER_TYPE_FLAG_NPU = 1 << 1
ZE_INIT_DRIVER_TYPE_FLAG_FORCE_UINT32 = 0x7fffffff

ZE_STRUCTURE_TYPE_DEVICE_PROPERTIES = 0x3  # c_ze_device_properties_t
ZE_STRUCTURE_TYPE_INIT_DRIVER_TYPE_DESC = 0x00020021  # c_ze_init_driver_type_desc_t
ZE_STRUCTURE_TYPE_DEVICE_IP_VERSION_EXT = 0x1000f  # c_ze_device_ip_version_ext_t


class c_ze_init_driver_type_desc_t(Structure):
    _fields_ = [
        ("stype", c_uint32),
        ("pNext", c_void_p),
        ("flags", c_uint32),
    ]
    def __init__(self):
        self.stype = ZE_STRUCTURE_TYPE_INIT_DRIVER_TYPE_DESC

class c_ze_device_properties_t(Structure):
    _fields_ = [
        ("stype", c_uint32),
        ("pNext", c_void_p),
        ("type", c_uint32),
        ("vendorId", c_uint32),
        ("deviceId", c_uint32),
        ("flags", c_uint32), # ze_device_property_flags_t
        ("subdeviceId", c_uint32),
        ("coreClockRate", c_uint32),
        ("maxMemAllocSize", c_uint64),
        ("maxHardwareContexts", c_uint32),
        ("maxCommandQueuePriority", c_uint32),
        ("numThreadsPerEU", c_uint32),
        ("physicalEUSimdWidth", c_uint32),
        ("numEUsPerSubslice", c_uint32),
        ("numSubslicesPerSlice", c_uint32),
        ("numSlices", c_uint32),
        ("timerResolution", c_uint64),
        ("timestampValidBits", c_uint32),
        ("kernelTimestampValidBits", c_uint32),
        ("uuid", c_uint8 * ZE_MAX_DEVICE_UUID_SIZE), # ze_device_uuid_t
        ("name", c_char * ZE_MAX_DEVICE_NAME),
    ]
    def __init__(self):
        self.stype = ZE_STRUCTURE_TYPE_DEVICE_PROPERTIES

class c_ze_device_ip_version_ext_t(Structure):
    _fields_ = [
        ("stype", c_uint32),
        ("pNext", c_void_p),
        ("ipVersion", c_uint32),
    ]
    def __init__(self):
        self.stype = ZE_STRUCTURE_TYPE_DEVICE_IP_VERSION_EXT

def zeInitDrivers(desc: c_ze_init_driver_type_desc_t):
    _LoadZe()

    version_less_than_1_10 = False
    try:
        fn = _zeGetFunctionPointer("zeInitDrivers")
    except:
        fn = _zeGetFunctionPointer("zeInit")
        _zePrint("L0 library API is less than 1.10, going to use zeInit()")
        version_less_than_1_10 = True

    if not version_less_than_1_10:
        driverCount = c_uint32()

        ret = fn(byref(driverCount), None, byref(desc))
        _zeCheck(ret)

        values_arr = c_ze_driver_handle_t * int(driverCount.value)
        values = values_arr()

        ret = fn(byref(driverCount), byref(values), byref(desc))
        _zeCheck(ret)
        return values
    else:
        # NOTE: This path works for the L0 library built with API less than 1.10.
        # NOTE: At 1.10 zeInit() and zeDriverGet() were deprecated in the favor of
        # NOTE: zeInitDrivers(). We wont't expose deprecated APIs in this Python
        # NOTE: binding module, but instead implement a fallback for the new API.
        ret = fn(desc.flags)
        _zeCheck(ret)

        fn = _zeGetFunctionPointer("zeDriverGet")

        driverCount = c_uint32()
        ret = fn(byref(driverCount), None)
        _zeCheck(ret)

        values_arr = c_ze_driver_handle_t * int(driverCount.value)
        values = values_arr()

        ret = fn(byref(driverCount), byref(values))
        _zeCheck(ret)
        return values


def zeDeviceGet(driver):
    fn = _zeGetFunctionPointer("zeDeviceGet")

    deviceCount = c_uint32()
    ret = fn(driver, byref(deviceCount), None)
    _zeCheck(ret)

    values_arr = c_ze_device_handle_t * int(deviceCount.value)
    values = values_arr()

    ret = fn(driver, byref(deviceCount), byref(values))
    _zeCheck(ret)
    return values


def zeDeviceGetProperties(device, extprops):
    fn = _zeGetFunctionPointer("zeDeviceGetProperties")

    props = c_ze_device_properties_t()
    props.stype = ZE_STRUCTURE_TYPE_DEVICE_PROPERTIES

    prev = props
    for p in extprops:
        prev.pNext = cast(pointer(p), c_void_p)

    ret = fn(device, byref(props))
    _zeCheck(ret)
    return props
