import sys
import time

try:
    import uselect as select
except ImportError:
    import select

stdin = sys.stdin.buffer
poll = select.poll()
poll.register(sys.stdin, select.POLLIN)
print("READY")
t0 = time.ticks_ms()
total = 0
while time.ticks_diff(time.ticks_ms(), t0) < 15000:
    if poll.poll(50):
        b = stdin.read(1)
        if b:
            total += 1
            if total <= 3 or total % 1000 == 0:
                print("n", total)
open("stats.txt", "w").write("total=%d\n" % total)
print("DONE", total)
