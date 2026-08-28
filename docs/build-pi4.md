# Building the cinepi base on a Raspberry Pi 4

Automated by [`scripts/build-cinepi-base.sh`](../scripts/build-cinepi-base.sh),
pinned revisions in [`scripts/versions.env`](../scripts/versions.env).

```bash
./scripts/build-cinepi-base.sh            # everything
./scripts/build-cinepi-base.sh list       # stage names
./scripts/build-cinepi-base.sh libcamera  # a single stage
```

Stages are idempotent. `FORCE_WIPE=1` discards Meson build dirs, `JOBS=n`
overrides parallelism.

## Which upstream

`cinepi/cinepi-raw` has not moved since February 2024 and still uses CMake; it
does not build against a current libcamera. This project builds
`Tiramisioux/cinepi-raw` and `Tiramisioux/libcamera` (branch `cinemate`), the
forks cinemate uses.

The packaged `libcamera-dev` is not enough: the fork carries sensor support and
gcc-12 fixes, and `cinepi-raw` installs `rpicam-*` binaries into
`/usr/local/bin` that must shadow the distribution ones.

## Pi 4 specifics

Cinemate's guide targets the Pi 5. This setup skips the kernel baseline (`apt-mark hold`,
`-rpi-2712`) and the RP1 overclock. The Pi 4 uses the VC4 ISP;
both pipelines are still enabled at build time to match the reference config.

`nproc` reports 3, not 4 — `cmdline.txt` has
`isolcpus=managed_irq,domain,3`, reserving core 3 for the camera pipeline.

`cinepi_raw.cpp` needs ~2 GB at `-O3`. Fine with 8 GB and no swap; boards under
3 GB need temporary zram.

Bookworm ships `libtiff.so.6` while the apps link `.so.5` — the
`libtiff_compat` stage symlinks it.

## Verified result

```
$ cinepi-raw --version
rpicam-apps build: 774402cb3f6f-intree 28-08-2026
libcamera build: v0.0.0+5539-3c7b9abd

$ cinepi-raw --list-cameras
0 : imx477 [4056x3040 12-bit RGGB] (/base/soc/i2c0mux/i2c@1/imx477@1a)
```

`ldd` resolves against `/usr/local/lib/aarch64-linux-gnu/libcamera.so.0.5` and
`/usr/local/lib/libredis++.so.1`.

12-bit modes, Pi 4 target first: 2028×1080 @ 62.8 fps, 2028×1520 @ 45.2,
4056×3040 @ 11.7.
