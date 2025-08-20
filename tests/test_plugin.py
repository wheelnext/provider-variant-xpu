# Copyright (c) 2025 Intel Corporation

import pytest
from variantlib.models.variant import VariantProperty

# Importing the whole module to be able to access modifications
# to internal module variables (such as _g_zelib).
import intel_variant_provider.ze as ze
from intel_variant_provider.devices import _intel_devips
from intel_variant_provider.plugin import IntelVariantPlugin
from intel_variant_provider.ze import *


@pytest.fixture
def plugin() -> IntelVariantPlugin:
    return IntelVariantPlugin()

def test_validate_property(plugin):
    for key in _intel_devips.keys():
        prop = f"intel :: device_ip :: {key}"
        assert plugin.validate_property(VariantProperty.from_str(prop))

def test_validate_property_assert(plugin):
    with pytest.raises(AssertionError):
        plugin.validate_property(VariantProperty.from_str(
            "notintel :: device_ip :: 12.55.8"))

def test_validate_property_fail_warn(plugin):
    with pytest.warns(UserWarning):
        assert not plugin.validate_property(VariantProperty.from_str(
            "intel :: nosuchprop :: 12.55.8"))

def test_validate_property_fail(plugin):
    assert not plugin.validate_property(VariantProperty.from_str(
        "intel :: device_ip :: 0.0.0"))


class TestGetSupportedConfigs:
    zelib_orig = None
    zelib_cache_orig = ( dict() )
    cdll_name = "intel_variant_provider.ze.CDLL"

    def setup_method(self, method):
        self.zelib_orig = ze.g_zelib
        self.zelib_cache_orig = ze.g_zelib_cache
        ze.g_zelib = None
        ze.g_zelib_cache = ( dict() )

    def teardown_method(self, method):
        ze.g_zelib = self.zelib_orig
        ze.g_zelib_cache = self.zelib_cache_orig

    def test_no_L0_library(self, plugin, mocker):
        mocker.patch(self.cdll_name, side_effect=OSError("No such file"))
        with pytest.warns(UserWarning):
            assert not plugin.get_supported_configs(None)
