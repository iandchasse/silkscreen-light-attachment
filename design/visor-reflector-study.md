# Visor reflector study (2026-10-20)

Model: `tools/visor_reflector_sim.py` (geometry only; Lambertian 120 deg LEDs at y 115.9 / z 9.5, both strings lit). Mirror = specular strip on the visor inner face, R 0.85 (aluminium / mirror tape); white print = Lambertian R 0.80. "flare" = the visor face leans outward (bottom edge further from the case), like a lampshade. Numbers are page light relative to today's mid-page.

```

=== PLAIN page (z 3.926); numbers are page light relative to TODAY's mid-page ===
case                                       d2    d10    d20    mid    d70    bot | top2-20 btmhalf top/btm
bare LEDs (today)                        0.00  12.18   4.90   1.00   0.38   0.19 |   11.60    0.46    25.4
mirror R0.85 to y113.0 tilt 0           26.49  12.18   4.90   1.00   0.38   0.19 |   17.70    0.46    38.8
mirror R0.85 to y113.0 tilt 10          18.51  12.18   4.90   1.00   0.38   0.19 |   11.60    0.46    25.4
mirror R0.85 to y113.0 tilt 20           0.00  12.18   4.90   1.00   0.38   0.19 |   11.60    0.46    25.4
mirror R0.85 to y111.0 tilt 0           26.49  25.81   4.90   1.00   0.38   0.19 |   24.30    0.46    53.2
mirror R0.85 to y111.0 tilt 10          35.33  12.18   4.90   1.00   0.38   0.19 |   20.43    0.46    44.7
mirror R0.85 to y111.0 tilt 20          40.33  12.18   4.90   1.00   0.38   0.19 |   15.57    0.46    34.1
mirror R0.85 to y109.5 tilt 0           26.49  25.81  11.06   1.00   0.38   0.19 |   25.45    0.46    55.7
mirror R0.85 to y109.5 tilt 10          35.33  27.93   4.90   1.00   0.38   0.19 |   23.95    0.46    52.4
mirror R0.85 to y109.5 tilt 20          40.33  12.18   4.90   1.00   0.38   0.19 |   18.66    0.46    40.9
white print R0.80 to y111 tilt 0        10.07  14.40   5.44   1.05   0.40   0.20 |   14.47    0.48    30.4
white print R0.80 to y111 tilt 20        7.38  12.42   4.90   1.00   0.38   0.19 |   12.68    0.46    27.8

=== FT01C page (z 4.98); numbers are page light relative to TODAY's mid-page ===
case                                       d2    d10    d20    mid    d70    bot | top2-20 btmhalf top/btm
bare LEDs (today)                       36.30  12.71   4.97   1.00   0.38   0.19 |   14.13    0.46    31.0
mirror R0.85 to y113.0 tilt 0           70.08  12.71   4.97   1.00   0.38   0.19 |   19.05    0.46    41.8
mirror R0.85 to y113.0 tilt 10          36.30  12.71   4.97   1.00   0.38   0.19 |   14.13    0.46    31.0
mirror R0.85 to y113.0 tilt 20          36.30  12.71   4.97   1.00   0.38   0.19 |   14.13    0.46    31.0
mirror R0.85 to y111.0 tilt 0           70.08  28.62   4.97   1.00   0.38   0.19 |   27.66    0.46    60.7
mirror R0.85 to y111.0 tilt 10          80.18  12.71   4.97   1.00   0.38   0.19 |   21.94    0.46    48.1
mirror R0.85 to y111.0 tilt 20          85.02  12.71   4.97   1.00   0.38   0.19 |   16.65    0.46    36.5
mirror R0.85 to y109.5 tilt 0           70.08  28.62  11.90   1.00   0.38   0.19 |   30.60    0.46    67.1
mirror R0.85 to y109.5 tilt 10          80.18  12.71   4.97   1.00   0.38   0.19 |   25.86    0.46    56.7
mirror R0.85 to y109.5 tilt 20          85.02  12.71   4.97   1.00   0.38   0.19 |   18.84    0.46    41.3
white print R0.80 to y111 tilt 0        47.57  14.87   5.48   1.05   0.40   0.20 |   17.07    0.47    36.1
white print R0.80 to y111 tilt 20       42.92  12.71   4.97   1.00   0.38   0.19 |   14.85    0.46    32.6

=== PLAIN page (z 3.926); numbers are page light relative to TODAY's mid-page ===
case                                       d2    d10    d20    mid    d70    bot | top2-20 btmhalf top/btm
bare LEDs (today)                        0.00  12.18   4.90   1.00   0.38   0.19 |   11.60    0.46    25.4
mirror R0.85 to y112.0 flare 15         10.87  20.00   8.98   2.02   0.38   0.19 |   19.11    0.67    28.7
mirror R0.85 to y112.0 flare 25          1.02  15.59   7.12   1.65   0.66   0.34 |   14.50    0.77    18.7
mirror R0.85 to y112.0 flare 35          0.00  12.18   5.26   1.23   0.50   0.26 |   11.69    0.58    20.1
mirror R0.85 to y112.0 flare 45          0.00  12.18   4.90   1.00   0.38   0.19 |   11.60    0.46    25.4
mirror R0.85 to y110.5 flare 15         10.87  20.00   8.98   2.02   0.80   0.41 |   19.11    0.94    20.2
mirror R0.85 to y110.5 flare 25          1.02  15.59   7.12   1.65   0.66   0.34 |   14.50    0.77    18.7
mirror R0.85 to y110.5 flare 35          0.00  12.18   5.26   1.23   0.50   0.26 |   11.69    0.58    20.1
mirror R0.85 to y110.5 flare 45          0.00  12.18   4.90   1.00   0.38   0.19 |   11.60    0.46    25.4
mirror R0.85 to y109.0 flare 15         10.87  20.00   8.98   2.02   0.80   0.41 |   19.11    0.94    20.2
mirror R0.85 to y109.0 flare 25          1.02  15.59   7.12   1.65   0.66   0.34 |   14.50    0.77    18.7
mirror R0.85 to y109.0 flare 35          0.00  12.18   5.26   1.23   0.50   0.26 |   11.69    0.58    20.1
mirror R0.85 to y109.0 flare 45          0.00  12.18   4.90   1.00   0.38   0.19 |   11.60    0.46    25.4
white print R0.80 to y110.5 flare 35     5.32  14.31   5.67   1.13   0.43   0.22 |   13.88    0.51    27.0

=== FT01C page (z 4.98); numbers are page light relative to TODAY's mid-page ===
case                                       d2    d10    d20    mid    d70    bot | top2-20 btmhalf top/btm
bare LEDs (today)                       36.30  12.71   4.97   1.00   0.38   0.19 |   14.13    0.46    31.0
mirror R0.85 to y112.0 flare 15         51.44  22.20   9.68   2.14   0.38   0.19 |   23.44    0.57    41.4
mirror R0.85 to y112.0 flare 25         39.60  17.20   7.63   1.73   0.69   0.35 |   18.15    0.81    22.4
mirror R0.85 to y112.0 flare 35         36.30  12.71   5.57   1.27   0.51   0.26 |   14.35    0.60    24.0
mirror R0.85 to y112.0 flare 45         36.30  12.71   4.97   1.00   0.38   0.19 |   14.13    0.46    31.0
mirror R0.85 to y110.5 flare 15         51.44  22.20   9.68   2.14   0.84   0.43 |   23.44    0.99    23.6
mirror R0.85 to y110.5 flare 25         39.60  17.20   7.63   1.73   0.69   0.35 |   18.15    0.81    22.4
mirror R0.85 to y110.5 flare 35         36.30  12.71   5.57   1.27   0.51   0.26 |   14.35    0.60    24.0
mirror R0.85 to y110.5 flare 45         36.30  12.71   4.97   1.00   0.38   0.19 |   14.13    0.46    31.0
mirror R0.85 to y109.0 flare 15         51.44  22.20   9.68   2.14   0.84   0.43 |   23.44    0.99    23.6
mirror R0.85 to y109.0 flare 25         39.60  17.20   7.63   1.73   0.69   0.35 |   18.15    0.81    22.4
mirror R0.85 to y109.0 flare 35         36.30  12.71   5.57   1.27   0.51   0.26 |   14.35    0.60    24.0
mirror R0.85 to y109.0 flare 45         36.30  12.71   4.97   1.00   0.38   0.19 |   14.13    0.46    31.0
white print R0.80 to y110.5 flare 35    42.95  15.13   5.83   1.14   0.43   0.22 |   16.79    0.52    32.5
```

Reading: a vertical or inward-leaning mirror only adds to the top 20 mm. A mirror flared 15-25 deg reaching down to y <= 110.5 roughly doubles the bottom half (0.46 -> 0.8-0.94) and mid-page (x1.65-2.0), and improves the top/bottom ratio from about 25:1 to 19-20:1. A white printed surface adds only about 10 %.
