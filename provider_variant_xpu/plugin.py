# Copyright (c) 2025 Intel Corporation

from __future__ import annotations

import os
import platform
import subprocess
import re
import warnings
from dataclasses import dataclass
from functools import cache
from typing import Protocol
from typing import runtime_checkable

from provider_variant_xpu.devices import devices as devmap
from provider_variant_xpu.ze import *

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


class XpuVariantPlugin:
    namespace = "xpu"
    dynamic = False

    @cache
    def generate_all_device_types(self) -> list[str] | None:
        pci_vendor_id_intel = 0x8086

        if platform.system() not in ["Linux", "Windows"]:
            warnings.warn(f"Unsupported OS: {system}", UserWarning, stacklevel=1)
            return []

        try:
            desc = c_ze_init_driver_type_desc_t()
            desc.stype = ZE_STRUCTURE_TYPE_INIT_DRIVER_TYPE_DESC
            desc.flags = ZE_INIT_DRIVER_TYPE_FLAG_GPU
            drivers = zeInitDrivers(desc)

            devtypes = []
            for driver in drivers:
                devices = zeDeviceGet(driver)
                for device in devices:
                    props = zeDeviceGetProperties(device)
                    if props.vendorId == pci_vendor_id_intel:
                        device_id = props.deviceId
                        if device_id not in devmap:
                            warnings.warn("Intel GPU not in the devmap", UserWarning, stacklevel=1)
                            continue
                        for d in devmap[device_id]:
                            if d not in devtypes:
                                devtypes.append(d)
            if not devtypes:
                warnings.warn("No Intel GPU detected", UserWarning, stacklevel=1)
            return devtypes
        except Exception as e:
            warnings.warn(f"Intel driver stack not installed or malfunctions: {e}", UserWarning, stacklevel=1)
            return []

    def get_supported_configs(
        self, known_properties: frozenset[VariantPropertyType] | None
    ) -> list[VariantFeatureConfig]:

        keyconfigs: list[VariantFeatureConfig] = []

        if devtypes := self.generate_all_device_types():
            keyconfigs.append(
                VariantFeatureConfig(
                    name="device_type",
                    values=devtypes,
                    )
                )

        return keyconfigs

    def validate_property(self, variant_property: VariantPropertyType) -> bool:
        assert isinstance(variant_property, VariantPropertyType)
        assert variant_property.namespace == self.namespace

        if variant_property.feature == "device_type":
            return variant_property.value in sum(devmap.values(), [])

        warnings.warn(
            "Unknown variant feature received: "
            f"`{namespace} :: {variant_property.feature}`.",
            UserWarning,
            stacklevel=1,
        )
        return False
