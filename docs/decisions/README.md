# Architecture decision records

One numbered file per decision, written before the code that implements it.
Format: `NNNN-short-title.md`.

State the context, the options considered, the choice and the reason. A
decision that turns out wrong gets a new record superseding the old one
rather than an edit.

Open decisions carried over from the project plan:

| Id | Question |
| -- | -------- |
| D-02 | Driver registration: static registry or `dlopen` plugins |
| D-06 | Reference sensor for the first working configuration |
| D-07 | Back-pressure policy when the writer cannot keep up |

Resolved: D-08 in [0001-config-format.md](0001-config-format.md).

Known gaps in `config/parameters.yaml`:

- Shutter angle and shutter speed are coupled in cinepi-raw
  (`shutter_s = 1 / (fps * 360 / shutter_a)`). Changing FPS changes the
  exposure time, so the menu has to recompute what it shows.
- Selecting a mode has to write `width`, `height`, `bit_depth` and `packing`
  to Redis, not a single key. cinepi-raw reads them separately.
