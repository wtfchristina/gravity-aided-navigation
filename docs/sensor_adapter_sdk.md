# Sensor Adapter SDK

Version 0.6 introduces a small adapter contract so customer-specific sensor payloads can be integrated without modifying the estimator core.

## Core interface

```python
from gravity_nav.adapters import SensorAdapter
from gravity_nav.packets import SensorPacket

class VendorSensorAdapter(SensorAdapter):
    name = "vendor_sensor"

    def adapt(self, payload) -> SensorPacket:
        ...
```

Adapters are responsible only for translating an external payload into the canonical `SensorPacket` schema. Filtering, timing policy, innovation gating, replay, and SIL/HIL behavior remain in the core package.

## Entry-point plug-ins

Private integration wheels can register adapters using standard Python package entry points:

```toml
[project.entry-points."gravity_nav.sensor_adapters"]
vendor_imu = "customer_qpnt.adapters:VendorIMUAdapter"
```

Then list installed adapters with:

```bash
qpnt adapters
```

This design keeps customer hardware code separate from the public research core and provides a natural boundary for commercial integrations.

## Included reference adapters

- `PacketJSONAdapter` — canonical JSON packet schema
- `MappingAdapter` — declarative mapping from arbitrary dictionaries
- `ExampleTacticalIMUAdapter` — fictional example demonstrating unit conversion and metadata

The example adapter is not tied to a real device or vendor specification.
