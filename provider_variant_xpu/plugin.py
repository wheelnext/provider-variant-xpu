from __future__ import annotations

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

    def get_supported_configs(self) -> list[VariantFeatureConfig]:

        keyconfigs: list[VariantFeatureConfig] = []

        keyconfigs.append(
            VariantFeatureConfig(
                name="oneapi",
                values=["2025.1"],
                )
            )

        return keyconfigs

    def get_all_configs(self) -> list[VariantFeatureConfig]:
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

