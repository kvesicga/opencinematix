# ui

User interface.

First target is the OLED menu on the 1.3" I2C display with the EC11 rotary
encoder: looks, ISO, shutter angle, FPS, white balance and resolution.

The HDMI output is not driven from here. cinepi-raw renders the live preview
directly to DRM.

Talks only through `control/`. If the UI can be deleted and the camera is
still fully operable through the API and physical controls, the layering is
correct.
