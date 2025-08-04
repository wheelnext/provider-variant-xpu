# Copyright (c) 2025 Intel Corporation

import pytest
import re

from provider_variant_xpu.devices import *
from provider_variant_xpu.devices import _intel_devips

pattern = re.compile("^[a-z0-9_.]+$")

def test_pattern():
    """Sanity test for the pattern"""
    assert pattern.fullmatch("abc")
    assert pattern.fullmatch("abc_1")
    assert pattern.fullmatch("abc.1")
    assert not pattern.fullmatch("abc-1")
    assert not pattern.fullmatch("ABC")

def to_uint32_devip(ip: str):
    devip = [int(x) for x in ip.split('.')]
    assert len(devip) == 3
    (arch, release, revision) = devip
    assert (revision & ~0x3F) == 0
    assert (release & ~0xFF) == 0
    assert (arch & ~0xFF) == 0
    return (revision & 0x3F) | (release << 14) | (arch << 22)

def test_to_uint32_devip():
    assert to_uint32_devip("12.60.7") == 0x030f0007
    assert to_uint32_devip("12.55.8") == 0x030dc008
    bad_revision = 0x4F
    with pytest.raises(AssertionError):
        to_uint32_devip(f"0.0.{bad_revision}")
    with pytest.raises(AssertionError):
        to_uint32_devip(f"0.256.0")
    with pytest.raises(AssertionError):
        to_uint32_devip(f"256.0.0")
    with pytest.raises(AssertionError):
        to_uint32_devip(f"1.2.3.4")

def test_intel_devips():
    """Test internal device IP table"""
    for key, value in _intel_devips.items():
        assert pattern.fullmatch(key)
        ignore_result = to_uint32_devip(key)
        assert value
        assert "devices" in value
        for d in value["devices"]:
            assert isinstance(d, str)
            assert d != ""
        if "compat" in value:
            assert isinstance(value["compat"], str)
            compat = value["compat"]
            assert compat in _intel_devips
            assert "compat_name" not in value
        elif "compat_name" in value:
            assert isinstance(value["compat_name"], str)
            assert value["compat_name"] != ""
            assert pattern.fullmatch(value["compat_name"])

def test_IntelDeviceIp_not_in_table():
    """Test device IP handling of the IP not in the internal table"""
    ip = IntelDeviceIp(0x12341234)
    str_ip = str(ip)
    # sanity check that we did not hit table entry
    assert str_ip not in _intel_devips
    # any IP should match the pattern
    assert pattern.fullmatch(str_ip)
    assert str_ip == "72.208.52"
    # should not have compat as it's not in table
    assert not ip.get_compat()
    # all compat should just have single entry of IP itself
    all_ips = ip.get_all_compat_ips()
    assert len(all_ips) == 1
    assert all_ips[0] == str_ip

def test_IntelDeviceIp_in_table():
    for key, value in _intel_devips.items():
        ip = IntelDeviceIp(to_uint32_devip(key))
        str_ip = str(ip)
        compat_ip = ip.get_compat()
        all_ips = ip.get_all_compat_ips()
        assert str_ip == key
        if "compat" in value:
            assert len(all_ips) == 2
            assert all_ips[0] == str_ip
            assert all_ips[1] == value["compat"]
            assert compat_ip == value["compat"]
        else:
            assert len(all_ips) == 1
            assert all_ips[0] == str_ip
            assert compat_ip == ""
