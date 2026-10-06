# Sensor Packet Schema

Each line in a replay log and each UDP datagram contains one JSON object.

```json
{
  "sensor": "imu",
  "timestamp_s": 12.5,
  "sequence": 42,
  "values": {
    "ax_mps2": 0.012,
    "ay_mps2": -0.004,
    "dt_s": 0.5
  },
  "frame": "local_xy",
  "metadata": {}
}
```

Required fields:

| Field | Type | Meaning |
|---|---|---|
| `sensor` | string | Sensor/message type |
| `timestamp_s` | float | Sensor/scenario timestamp |
| `sequence` | integer | Monotonic source sequence identifier |
| `values` | object | Numeric observation payload |

Optional fields:

| Field | Type | Meaning |
|---|---|---|
| `frame` | string | Coordinate frame label |
| `metadata` | object | Non-numeric annotations |

The schema is intentionally small so non-Python systems can produce or consume it easily.
