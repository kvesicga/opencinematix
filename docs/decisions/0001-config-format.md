# 0001: YAML for configuration files

Status: accepted, 2026-08-31

Resolves D-08.

## Context

Hardware description, bindings and the parameter registry are written and
read by hand. They need comments, since a pin number or an ISO step is
meaningless without one. The files are nested: a device has a driver, a
capability and driver specific settings.

`python3-yaml` is already installed as a build dependency of cinepi-raw.

## Options

**JSON** cannot carry comments. For files describing hardware that is a
practical problem, not a stylistic one.

**JSONC**, which cinemate uses, adds comments to JSON but is not
standardised. Every language handles it differently.

**TOML** avoids YAML's type surprises and is in the standard library from
Python 3.11. Deeply nested lists read poorly, and the bindings are exactly
that.

**YAML** reads well when nested, allows comments and is available already.

## Decision

YAML.

## Consequences

YAML has known traps. Unquoted `on`, `off`, `yes` and `no` become booleans,
and indentation errors are easy to make. Loading must use `yaml.safe_load`,
never `yaml.load`, which can construct arbitrary Python objects.

Values that could be misread as booleans get quoted. A schema check on load
is needed so a malformed file fails with a clear message rather than a
confusing error later.
