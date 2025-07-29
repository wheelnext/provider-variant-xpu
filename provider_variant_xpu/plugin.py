from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from typing import Protocol
from typing import runtime_checkable

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

    @property
    def detect_intel_gpu(self):
        pci_base_class_mask = 0x00ff0000
        pci_base_class_display = 0x00030000
        pci_vendor_id_intel = 0x8086

        devices_path = "/sys/bus/pci/devices"
        if not os.path.isdir(devices_path):
            return False  # Not a Linux system with PCI devices

        for device in os.listdir(devices_path):
            dev_path = os.path.join(devices_path, device)
            try:
                # Read class and vendor files
                with open(os.path.join(dev_path, "class")) as f:
                    pci_class = int(f.read().strip(), 16)
                with open(os.path.join(dev_path, "vendor")) as f:
                    pci_vendor = int(f.read().strip(), 16)

                # Check for display controller and Intel vendor
                if (pci_class & pci_base_class_mask) == pci_base_class_display and pci_vendor == pci_vendor_id_intel:
                    print(f"Detected Intel GPU at {dev_path} (vendor=0x{pci_vendor:04x})")
                    return True
            except Exception:
                continue  # Ignore devices we can't parse

        warnings.warn(
            "No Intel GPU detected",
            UserWarning,
            stacklevel=1,
        )
        return False

    def get_supported_configs(
        self, known_properties: frozenset[VariantPropertyType] | None
    ) -> list[VariantFeatureConfig]:

        keyconfigs: list[VariantFeatureConfig] = []

        if self.detect_intel_gpu:
            keyconfigs.append(
                VariantFeatureConfig(
                    name="oneapi",
                    values=["2025.1"],
                    )
                )

        return keyconfigs

    def get_all_configs(
        self, known_properties: frozenset[VariantPropertyType] | None
    ) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig(
                name="oneapi",
                values=["2025.0", "2025.1", "2025.2"],
            )
        ]

    def validate_property(self, variant_property: VariantPropertyType) -> bool:
        assert isinstance(variant_property, VariantPropertyType)
        assert variant_property.namespace == self.namespace

        if variant_property.feature == "oneapi":
            return variant_property.value in ["2025.1"]

        warnings.warn(
            "Unknown variant feature received: "
            f"`{namespace} :: {variant_property.feature}`.",
            UserWarning,
            stacklevel=1,
        )
        return False

if __name__ == "__main__":
    plugin = XpuVariantPlugin()
    print(  # noqa: T201
        plugin.validate_property(
            VariantProperty(namespace="xpu", feature="oneapi", value="2025.1")
        )
    )

