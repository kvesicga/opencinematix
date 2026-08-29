# Measurements

Numbers taken on real hardware, not estimates. Later decisions reference
them.

What belongs here:

- sustained sequential write throughput of the storage target, measured for
  at least 60 seconds with the intended filesystem
- dropped frame counts during sustained recording
- CPU and thermal headroom over long runs

Throughput is the binding physical limit. Uncompressed 12-bit Bayer at
2028x1080 is roughly 3.3 MB per frame, so about 80 MB/s at 24 fps. At
4056x3040 it is around 18.5 MB per frame, roughly 440 MB/s at 24 fps, which
no USB3 SSD sustains in practice.

Record the medium, the filesystem, the duration and the exact command used.
