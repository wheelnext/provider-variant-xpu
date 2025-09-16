# Copyright (c) 2025 Intel Corporation

from __future__ import annotations

import platform
import warnings
from dataclasses import dataclass
from functools import cache
from typing import Protocol, runtime_checkable

from intel_variant_provider.devices import *
from intel_variant_provider.ze import *

VariantNamespace = str
VariantFeatureName = str
VariantFeatureValue = str

@runtime_checkable
class VariantPropertyType(Protocol):
    """A protocol for variant properties"""

    @property
    def namespace(self) -> VariantNamespace:
        """Namespace (from plugin)"""
        raise NotImplementedError

    @property
    def feature(self) -> VariantFeatureName:
        """Feature name (within the namespace)"""
        raise NotImplementedError

    @property
    def value(self) -> VariantFeatureValue:
        """Feature value"""
        raise NotImplementedError

@dataclass(frozen=True)
class VariantFeatureConfig:
    name: str

    # Acceptable values in priority order
    values: list[str]


class IntelVariantPlugin:
    namespace = "intel"
    dynamic = False

    @cache
    def generate_all_device_ips(self) -> list[str] | None:
        pci_vendor_id_intel = 0x8086

        if platform.system() not in ["Linux", "Windows"]:
            warnings.warn(f"Unsupported OS: {system}", UserWarning, stacklevel=1)
            return []

        try:
            desc = c_ze_init_driver_type_desc_t()
            desc.flags = ZE_INIT_DRIVER_TYPE_FLAG_GPU
            drivers = zeInitDrivers(desc)

            devips = []
            for driver in drivers:
                devices = zeDeviceGet(driver)
                for device in devices:
                    devip = c_ze_device_ip_version_ext_t()
                    props = zeDeviceGetProperties(device, [devip])
                    if props.vendorId == pci_vendor_id_intel:
                        devip = IntelDeviceIp(devip.ipVersion)
                        for ip in devip.get_all_compat_ips():
                            # Filter out devices which IPs are not explicitly
                            # known to plugin. This gives consistency with the
                            # check in validate_property().
                            if ip not in get_all_ips():
                                warnings.warn(f"Intel device with {ip} device IP is filtered out as not known to plugin)")
                                continue
                            # We must return list of unique IPs as a requirement
                            # of variantlib.
                            if ip not in devips:
                                devips.append(ip)
            if not devips:
                warnings.warn("No Intel GPU detected", UserWarning, stacklevel=1)
            return devips
        except Exception as e:
            warnings.warn(f"Intel driver stack not installed or malfunctions: {e}", UserWarning, stacklevel=1)
            return []

    def get_supported_configs(self) -> list[VariantFeatureConfig]:
        keyconfigs: list[VariantFeatureConfig] = []

        if devips := self.generate_all_device_ips():
            keyconfigs.append(
                VariantFeatureConfig(
                    name="device_ip",
                    values=devips,
                    )
                )

        return keyconfigs

    def get_all_configs(self) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig(
                name="device_ip", values=get_all_ips()
            ),
        ]

if __name__ == "__main__":
    plugin = IntelVariantPlugin()
    print(plugin.get_supported_configs(None))
