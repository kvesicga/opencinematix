# post

Post-processing pipeline based on darktable.

Lives on the Pi and runs there, triggered once a capture finishes. Develops
recorded DNGs and applies the look selected in the menu.

Can be switched on and off at runtime. Enabled for stills, disabled for
video, where the frame rate leaves no room to process per frame. The switch
is a parameter in the registry, so it is reachable from the OLED menu and any
other client.

Stills are the primary target. A first prototype developed a 4K 12-bit DNG
with a LUT applied and wrote it out in under three seconds, fast enough to
keep up with shooting.
