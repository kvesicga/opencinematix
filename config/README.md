# config

Hardware description, bindings and looks.

Declarative only. Which devices exist and what they control belongs here, not
in code. Adding a physical control should mean editing these files plus one
driver in `core/hal/`.

Sketch of the intended shape:

```yaml
devices:
  - id: rec_button
    driver: gpio_button
    capability: DiscreteTrigger
    config: { pin: 5, pull: up, debounce_ms: 30 }

bindings:
  - from: rec_button
    to: command:recording.toggle
```

Format is not decided yet. See `docs/decisions/`.
