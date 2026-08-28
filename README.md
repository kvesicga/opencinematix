# OpenCinematix

A modular cinema camera platform for the Raspberry Pi — with its own user
interface and post-processing pipeline, built on top of
[cinepi-raw](https://github.com/cinepi/cinepi-raw) as the recording backend.

The project is deliberately not tied to a single sensor. The current setup
uses the HQ Camera Module (IMX477); the architecture is meant to accommodate
other sensors and additional hardware.

## What it is — and what it is not

OpenCinematix uses cinepi-raw as the backend for RAW recording and talks to
it exclusively over Redis. Everything above that layer — menu navigation,
control logic, looks, post-processing — is written from scratch.

This is explicitly **not** a fork of the
[cinepi-sdk](https://github.com/cinepi/cinepi-sdk) and **not** a copy of
[cinemate](https://github.com/Tiramisioux/cinemate). Cinemate serves as a
structural reference and as a source for Pi 4 specific details, but its code
is not adopted. This repository has its own history; the code is written and
documented from the ground up.

## Hardware

The setup currently in use — not meant as a constraint:

| Component        | Model                                             |
| ---------------- | ------------------------------------------------- |
| Board            | Raspberry Pi 4B Rev 1.4, 8 GB                     |
| Sensor           | HQ Camera Module (IMX477) on CSI port `cam0`      |
| Preview          | HDMI, 1920×1080 @ 60 Hz — live sensor image only  |
| Controls         | Estardyn 1.3" OLED (I²C) + EC11 rotary encoder    |
| Operating system | Raspberry Pi OS Lite (Bookworm), 64-bit           |

The two displays serve separate purposes: HDMI carries nothing but the live
preview of the sensor image, while the OLED holds the menu (looks as well as
ISO, shutter angle, FPS, white balance and resolution).

### Sensor modes (IMX477)

The target for the Pi 4 is **2028×1080 at 12 bit**. 4K is not realistic on
this platform — the Pi 4 uses the VC4 ISP rather than the Pi 5's PiSP.

| Mode        | Format          | Max FPS |
| ----------- | --------------- | ------- |
| 2028×1080   | `SRGGB12_CSI2P` | 62.8    |
| 2028×1520   | `SRGGB12_CSI2P` | 45.2    |
| 4056×3040   | `SRGGB12_CSI2P` | 11.7    |

## Architecture

Redis acts as both **message bus and single source of truth** for the camera
state. Any process able to speak Redis is therefore a first-class client —
the OLED menu is simply another subscriber and never needs to know about
cinepi-raw directly.

```
                        ┌─────────────────┐
   SET <key> <value>    │                 │    SUBSCRIBE cp_controls
   PUBLISH cp_controls  │                 │    GET <key>
  ┌────────────────────▶│                 │◀────────────────────┐
  │                     │      Redis      │                     │
  │  ┌──────────────────│                 │─────────────────┐   │
  │  │  SUBSCRIBE       │  state +        │   PUBLISH       │   │
  │  │  cp_controls     │  pub/sub bus    │   cp_stats      │   │
  │  ▼                  └─────────────────┘                 ▼   │
┌──────────────┐                                      ┌──────────────┐
│  cinepi-raw  │                                      │  OLED menu   │
│              │                                      │  (Python)    │
│  recording + │                                      │  EC11 + I²C  │
│ HDMI preview │                                      └──────────────┘
└──────────────┘
```

### Control path (bidirectional)

A state change always consists of two steps:

```
SET <key> <value>
PUBLISH cp_controls <key>
```

The crucial detail: the published message carries **only the key name, not
the value**. Receivers then fetch the current value themselves via
`GET <key>`. This keeps Redis the single source of truth — the message is
pure notification, not data transport.

### Stats path (unidirectional)

cinepi-raw publishes once per frame:

```
PUBLISH cp_stats <json>
```

The payload includes `framerate`, `colorTemp`, `focus`, `frameCount`,
`bufferSize` and timestamps, among others.

### Echo suppression

On a bus where everyone listens, a client also receives its own messages
back. Without a countermeasure this creates feedback loops.

The pattern: whoever writes a value records the key in a `local_updates` set
and discards the matching message when it comes back. Every client written
for this project has to implement the same guard.

## Repository layout

```
src/opencinematix/   Python package: UI, Redis client, OLED menu
src/native/          C++ components
docs/                build log, architecture and hardware notes
services/            systemd units
scripts/             setup and helper scripts
config/              configuration (looks, defaults)
tests/               tests that run without hardware
```

## Status

Under development. Current stage: building the cinepi base for Pi 4 and
IMX477 (libcamera, redis-plus-plus, cpp-mjpeg-streamer, cinepi-raw).

Everything has to be built from source — the prebuilt SDK images are not
usable on the Pi 4, since the cinepi-sdk officially supports the Pi 5 only.

Planned next: a Redis client in Python (testable locally without hardware),
the OLED menu over I²C with the EC11 encoder, and a post-processing pipeline
based on darktable.

## Documentation

The build process is written down in [`docs/`](docs/) as it happens —
including the Pi 4 specifics that differ from the Pi 5.
