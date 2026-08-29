# core

Parameter model and hardware abstraction.

The parameter registry is the only way to read or mutate camera state. Every
controllable property is a parameter with a stable id, type, valid range,
current value and whether it can change while recording.

The UI, a rotary encoder and a network client are all clients of this
registry. None of them is special-cased anywhere else in the system.

Depends on nothing above it. No Redis, no display code, no device drivers.
