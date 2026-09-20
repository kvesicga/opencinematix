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

## Drivers

| Driver | Capability | Wiring |
| ------ | ---------- | ------ |
| `rotary_encoder.py` | `RelativeDelta` | EC11 on GPIO 17 and 27 |
| `push_button.py` | `DiscreteTrigger` | GPIO 22 |
| `oled_display.py` | `TextSurface` | SH1106 over I2C, bus 1, address 0x3c |

The module carries its own pull-up resistors, so all inputs use
`pull_up = True` and need no external parts.

`close()` detaches the handlers before releasing a pin. The other order
raises, because a handler still running touches a closed object.

## quadrature.py

The encoder splits into a decoder and a driver. `QuadratureDecoder` is a
state machine with no hardware knowledge and is fully covered by
`tests/test_quadrature.py`. The driver only feeds it pin levels.

Debouncing happens in the transition table, not on a timer. A bouncing
contact produces transitions that are mechanically impossible, and those are
not in the table, so they are discarded. This is why the encoder driver must
not set `bounce_time`: a timer would swallow real edges during fast turns.

The button has no such logic and does need `bounce_time`, currently 50 ms.

`DETENT = 4` because this encoder emits four edges per detent. Others emit
two.

## oled_display.py

`luma` handles the SH1106 column offset, so the driver only has to pick the
right device class.

`show()` draws into an off-screen canvas and transfers it in one go when the
block ends. Drawing line by line straight to the display would flicker.

`capacity` is derived from the device height, so it follows a rotation
instead of being fixed. Lines beyond it are dropped; scrolling is menu logic,
not a driver concern.
