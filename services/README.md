# services

systemd unit files.

The camera has to come up on power-on without a keyboard, a login or an SSH
session. These units make that happen and restart a component if it dies.

Planned units:

| Unit | Purpose |
| ---- | ------- |
| `cinepi-raw.service` | recording backend with the verified parameters |
| `opencinematix-ui.service` | OLED menu |

Redis comes from the distribution package and needs no unit here.

The files live in `/etc/systemd/system/` at runtime. An install script copies
or links them there. They are versioned here so a fresh Pi can be brought to
a working state from the repository alone.

Ordering matters: cinepi-raw needs Redis, so its unit declares
`After=redis-server.service`.
