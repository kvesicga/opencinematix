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

## Tests

`tests/test_redis_client.py` runs against a real Redis server on database 15
and a separate channel, so it never touches live camera state. Pub/sub
channels are global in Redis, which is why the channel is overridden rather
than relying on the database number alone.

```bash
python3 -m pytest tests/test_redis_client.py -v
```
