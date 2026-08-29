# tests

Tests that run without camera hardware.

The parameter model, the Redis client and all HAL logic must be testable on a
development machine against a local Redis and mock devices. Only the camera
path itself needs a Pi.

If a test needs real hardware to exercise HAL logic, the layering has leaked.
