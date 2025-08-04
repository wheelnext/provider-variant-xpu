# XPU Variant Provider Plugin

A variant provider plugin for the Wheel Variant upcoming proposed standard
that enables automatic detection and selection of Intel GPU-optimized
Python packages.

## Detected Hardware Properties

1. GPU Architecture (Compute Capability)

   * Determines the compute capability available on the system.
   * Resolves with compute capability compatibility in mind.
   * Returns feature list in the form of `xpu::device_ip::<ip>`
   * Each value (`<ip>`) in the list represents human readable form of
     Intel hardware device IP (GMDID) quariable via Level Zero [ZE_extension_device_ip_version]

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

## Understanding Intel Device IP Values

Device IP is an identifier (GMDID) assigned to differentiate architectures of
compute platforms of Intel GPU devices. Few different Intel GPU devices (with
the different device IDs) might be built on the same compute platform.

Programmatically device IP can be queried for each Intel GPU device using
Level Zero [ZE_extension_device_ip_version] API. Returned value format is
Intel specific and requires conversion to human readable form.

Intel offline compiler (`ocloc`) generates code for one or few target compute
platforms passed in `-device <device_type>` argument. Each `<device type> in
the list can be set as Device IP or via acronym name internally mapped to the
respective Device IP. To query Device IP(s) for the specific acronym
`ocloc ids` command can be used. For example:

```
$ ocloc ids bmg
Matched ids:
20.1.0

$ ocloc ids xe3
Matched ids:
30.0.0
30.0.4
30.1.0
30.1.1
```

For Python package to target specific Intel architectures using XPU variant
provider plugin, it's required to build package variants for these
architectures and set `xpu::device_ip::<ip>` properties accordingly. For the
above example of `bmg` and `xe3` that would be:

```
# for bmg variant:
xpu::device_ip::20.1.0

# for xe3 variant:
xpudevice_ip::30.0.0
xpudevice_ip::30.0.4
xpudevice_ip::30.1.0
xpudevice_ip::30.1.1
```

[ZE_extension_device_ip_version]: https://oneapi-src.github.io/level-zero-spec/level-zero/latest/core/EXT_DeviceIpVersion.html#ze-extension-device-ip-version
