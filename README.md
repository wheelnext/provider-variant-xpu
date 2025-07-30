# XPU Variant Provider Plugin

A variant provider plugin for the Wheel Variant upcoming proposed standard
that enables automatic detection and selection of Intel GPU-optimized
Python packages.

## Detected Hardware Properties

1. GPU Architecture (Compute Capability)

   * Determines the compute capability available on the system.
   * Resolves with compute capability compatibility in mind.
   * Returns feature list in the form of `xpu::device_type::<arch>`

## Configuring Your Project

Add variant configuration to your `pyproject.toml`:

```
[variant.default-priorities]
namespace = ["xpu"]

[variant.providers.xpu]
requires = ["provider_variant_xpu"]
enable-if = "platform_system == 'Linux'"
plugin-api = "provider_variant_xpu.plugin:XpuVariantPlugin"
```
