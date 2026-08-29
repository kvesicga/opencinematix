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
| D-08 | Config file format for hardware description |
