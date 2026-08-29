# core/hal

Hardware abstraction: capability contracts, device drivers, bindings.

Three parts, decoupled from each other:

**Capabilities** are a small set of abstract behaviours. Keep the set small.
A new device that fits an existing contract needs no new contract.

| Capability | Semantics | Example |
| ---------- | --------- | ------- |
| `DiscreteTrigger` | fires an event | momentary push button |
| `TwoState` | on/off with position | toggle switch |
| `RelativeDelta` | signed increments | rotary encoder |
| `AbsolutePosition` | normalized 0..1 | potentiometer |
| `Indicator` | boolean output | tally LED |
| `TextSurface` | renders lines of text | OLED display |

**Drivers** implement one or more capabilities for a device family. A driver
knows a bus (GPIO, I2C, SPI, USB HID) and nothing about cameras, parameters
or recording.

**Bindings** map a capability instance to a parameter or command. They live
in `config/`, never in code.

Acceptance test: adding a new physical control must require one new driver
file plus config entries, with no changes outside this directory. If a device
forces changes elsewhere, the abstraction is wrong.
