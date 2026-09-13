# control

Redis client and control plane.

Talks to cinepi-raw over Redis, which is both the message bus and the single
source of truth for camera state. Translates between the parameter registry
in `core/` and the wire protocol.

Two paths:

- **Controls**, bidirectional. `SET <key> <value>` then
  `PUBLISH cp_controls <key>`. The message carries only the key name.
  Receivers fetch the value with `GET <key>`.
- **Stats**, inbound only. cinepi-raw publishes JSON on `cp_stats` once per
  frame.

Every writer must suppress its own echo. Record the key in a `local_updates`
set on write and discard the matching message when it comes back, otherwise
the bus feeds back on itself.

Testable without hardware against a local Redis instance.

## redis_client.py

`RedisClient` wraps the two paths above. `set()` writes the value and
publishes the key in one call, so the second step cannot be forgotten.

```python
from control.redis_client import RedisClient

def on_change(key, value):
    print(key, value)

client = RedisClient(on_change = on_change)
client.set("iso", 800)
client.get("iso")          # "800", Redis stores everything as text
```

| Parameter | Default | Purpose |
| --------- | ------- | ------- |
| `host` | `127.0.0.1` | Redis server |
| `port` | `6379` | Redis port |
| `db` | `0` | database number |
| `channel` | `cp_controls` | pub/sub channel |
| `on_change` | `None` | called with key and value on remote changes |

The listener runs in a daemon thread. Own writes are suppressed, so
`on_change` only fires for changes made by others. A suppression entry is
consumed by one message, so the next change to the same key is reported
normally.

Not yet handled: reconnection after a dropped connection, explicit shutdown,
and type conversion.

## camera_state.py

`CameraState` ties the registry and the client together. Callers use
parameter names, not Redis keys, and values are validated before they are
written.

```python
from control.camera_state import CameraState
from control.redis_client import RedisClient
from core.parameters import ParameterRegistry

camera = CameraState(ParameterRegistry("config/parameters.yaml"), RedisClient())

camera.set("iso", 1600)
camera.get("iso")                       # 1600, as an int
camera.set("sensor_mode", "2028x1520x12")
camera.set("iso", 6400)                 # raises ValueError
```

Registry and client are passed in rather than created here, so tests can
supply a client bound to a different database.

An invalid value raises `ValueError` and nothing is written. This matters:
cinepi-raw terminates on a malformed mode string, so the check is the last
line of defence.

### Sensor mode

Setting a mode writes three keys and then triggers a reinit, all verified
against a running camera.

The `mode` key must use the colon form, `2028:1520:12:P`. The parser in
cinepi-raw reads it with `sscanf("%u:%u:%u:%c")`, so any other separator
throws `Invalid mode` and kills the process.

Writing the keys alone does nothing. The handler for `mode` only updates
options in memory and never sets `cameraInit_`, so `cam_init` has to follow.
The preview goes black briefly while the camera restarts.

`shutter_s` is not written back when the shutter angle changes, even though
cinepi-raw recomputes it internally. Only `shutter_a` is reliable.

### Remote changes

Pass `on_change` to be told when another client writes a value. The callback
receives a parameter name and a converted value, not a Redis key and text.

```python
def on_change(parameter, value):
    print(parameter, value)          # "shutter_angle", 90.0

menu = CameraState(registry, RedisClient(), on_change = on_change)
```

`CameraState` inserts itself between the client and the caller, translating
the key back to a name and converting the value. Keys that are not in the
configuration, such as `frameCount`, are dropped.

Echo suppression still happens in the client, so a client is never told about
its own writes.

Note that cinepi-raw never publishes on `cp_controls`. It writes defaults at
startup without notifying anyone, and only publishes frame data on
`cp_stats`. This callback therefore only fires for other clients of this
project, not for cinepi-raw itself.

### Recording guard

A parameter marked `live: false` cannot be changed while `is_recording` is
set. `set` raises `RuntimeError` and writes nothing.

```python
camera.set("is_recording", True)
camera.set("sensor_mode", "2028x1520x12")   # raises RuntimeError
camera.set("iso", 1600)                     # fine, iso is live
```

This protects a running take. A mode change writes `cam_init`, which stops
and restarts the camera and would cut the recording short.

The guard sits here rather than in the menu, so a script or a second client
cannot bypass it. If `is_recording` is absent, changes are allowed, which
matters before the first start.

Booleans are written as `1` and `0`, since Redis rejects Python bool values.

## Tests

Both test files run against a real Redis server on database 15 and a
separate channel, so they never touch live camera state. Pub/sub channels are
global in Redis, which is why the channel is overridden rather than relying
on the database number alone.

```bash
python3 -m pytest tests/test_redis_client.py tests/test_camera_state.py -v
```
