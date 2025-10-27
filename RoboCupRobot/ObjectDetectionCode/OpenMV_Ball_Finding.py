import sensor, image, time, math, pyb

# — LED Setup —
led_r = pyb.LED(1)  # Red
led_b = pyb.LED(3)  # Blue

# — Sensor Setup —
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

# — Digital-Out on P4 —
out_pin = pyb.Pin("P4", pyb.Pin.OUT_PP)
out_pin.value(0)

# — Orange Threshold in LAB —
ORANGE_THRESH = (48, 89, 31, 119, 39, 106)

clock = time.clock()
while True:
    clock.tick()

    # Capture & undistort
    img = sensor.snapshot()
    img.lens_corr(strength=1.5, zoom=1.0)

    # Blob detection
    blobs = img.find_blobs([ORANGE_THRESH],
                           pixels_threshold=20,
                           area_threshold=20,
                           merge=True)

    if blobs:
        # draw all blobs
        for b in blobs:
            img.draw_rectangle(b.rect(), thickness=2)
            img.draw_cross(b.cx(), b.cy(), size=10)
        # compute angle of largest blob
        b = max(blobs, key=lambda b: b.pixels())
        dx = b.cx() - img.width()  / 2
        dy = img.height()/ 2 - b.cy()
        angle = math.degrees(math.atan2(dy, dx))

        # decide output
        out = 1 if (angle < -150 or angle > 150) else 0
    else:
        out = 0

    # set P4 and LEDs
    out_pin.value(out)
    if out:
        led_r.on()
        led_b.off()
    else:
        led_r.off()
        led_b.on()

    print("Angle: %.1f°, OUT=%d" % (angle if blobs else 0, out))
    print("FPS:", clock.fps())
