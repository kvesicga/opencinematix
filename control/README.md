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
