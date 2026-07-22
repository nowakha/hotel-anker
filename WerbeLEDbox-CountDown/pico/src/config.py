# 8-line WS2812 — TOP row, toward Micro-USB (pins 24..34)
# Board: USB on LEFT. Top row L→R = physical pins 40 → 21.
# Toward USB = high pin numbers (left side of top row).

N_LED = 512
N_LINES = 8
FPS = 25

# Line 0..7 = nearest usable data pins walking AWAY from USB along top row:
# GP28@34, GP27@32, GP26@31, GP22@29, GP21@27, GP20@26, GP19@25, GP18@24
# GND (top row): 38 (near USB), 33, 28 — skip 30 RUN, skip 35..40 power
PIN_LINES = (28, 27, 26, 22, 21, 20, 19, 18)

UDP_PORT = 5005
WIFI_TIMEOUT_S = 20
MAGIC = b"ANKR"
