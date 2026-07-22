"""Up to 8x WS2812 output via RP2040 PIO state machines (SM0..SM7)."""

import array

import rp2
from machine import Pin
import micropython


@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    autopull=True,
    pull_thresh=24,
)
def _ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 1]
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()


@micropython.viper
def _fill_grb(buf: ptr32, rgb: ptr8, n: int):
    i = 0
    while i < n:
        o = i * 3
        r = int(rgb[o])
        g = int(rgb[o + 1])
        b = int(rgb[o + 2])
        buf[i] = (g << 16) | (r << 8) | b
        i += 1


@micropython.native
def _show_interleaved(sms, bufs, n_led, n_lines):
    i = 0
    while i < n_led:
        li = 0
        while li < n_lines:
            sms[li].put(bufs[li][i])
            li += 1
        i += 1


class Ws2812Lines:
    """Drive N parallel WS2812 strips (one PIO SM each, max 8 on RP2040)."""

    def __init__(self, pins, n_led):
        if not 1 <= len(pins) <= 8:
            raise ValueError("need 1..8 pins (SM0..SM7)")
        self.n_led = int(n_led)
        self.n_lines = len(pins)
        self._sms = []
        for i, p in enumerate(pins):
            sm = rp2.StateMachine(
                i,
                _ws2812,
                freq=8_000_000,
                sideset_base=Pin(int(p)),
            )
            sm.active(1)
            self._sms.append(sm)
        self._bufs = [array.array("I", [0] * self.n_led) for _ in range(self.n_lines)]

    def fill_rgb(self, line, rgb):
        need = self.n_led * 3
        if len(rgb) < need:
            raise ValueError("short rgb buffer")
        _fill_grb(self._bufs[line], rgb, self.n_led)

    def show(self):
        _show_interleaved(self._sms, self._bufs, self.n_led, self.n_lines)

    def black(self):
        for buf in self._bufs:
            for i in range(self.n_led):
                buf[i] = 0
        self.show()
