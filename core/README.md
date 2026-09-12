# core

Parameter model and hardware abstraction.

The parameter registry is the only way to read or mutate camera state. Every
controllable property is a parameter with a stable id, type, valid range,
current value and whether it can change while recording.

The UI, a rotary encoder and a network client are all clients of this
registry. None of them is special-cased anywhere else in the system.

Depends on nothing above it. No Redis, no display code, no device drivers.

## parameters.py

`ParameterRegistry` loads the definitions and answers three questions: which
Redis key a parameter uses, whether a value is allowed, and which type a
value from Redis should be converted to.

```python
from core.parameters import ParameterRegistry

registry = ParameterRegistry("config/parameters.yaml")

registry.redis_key("shutter_angle")          # "shutter_a"
registry.parameter_name("shutter_a")         # "shutter_angle"
registry.is_valid("iso", 6400)               # False
registry.convert("iso", "800")               # 800
```

| Attribute | Content |
| --------- | ------- |
| `parameters` | parameter definitions from `config/parameters.yaml` |
| `modes` | sensor modes from `config/sensors/<sensor>.yaml` |
| `default_mode` | mode to start with |

The sensor file is found through the `sensor` field of the parameter file, so
swapping sensors means one changed line and a new file under
`config/sensors/`.

Validation depends on the declared type. A `mode` is checked against the
sensor's modes, a `bool` against being a real boolean, everything else
against its `values` list. For an enum, `values` is a mapping and the numeric
keys are what counts, since that is what goes to Redis.

Conversion turns Redis text into the declared type. `bool` compares against
`"1"` rather than using `bool()`, which would treat `"0"` as true. An
unknown type raises `ValueError` instead of returning `None`.

`parameter_name` is the reverse of `redis_key` and returns `None` for keys
that are not in the configuration, such as `frameCount`. Those are normal in
Redis, so an unknown key is not an error here.

Not yet handled: shutter angle and shutter speed are coupled through the
frame rate, and `live: false` is not enforced.

## Tests

```bash
python3 -m pytest tests/test_parameters.py -v
```
