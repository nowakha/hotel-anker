"""Frame protocol: ANKR | seq:u16le | n_led:u16le | n_lines:u8 | flags:u8 | RGB..."""

import struct

import config

# magic(4) + seq(u16) + n_led(u16) + n_lines(u8) + flags(u8)
HDR_FMT = "<4sHHBB"
HDR_SIZE = 10


def frame_nbytes(n_led, n_lines):
    return HDR_SIZE + n_led * n_lines * 3


def pack_frame(seq, rgb, n_led=None, n_lines=None):
    if n_led is None:
        n_led = config.N_LED
    if n_lines is None:
        n_lines = config.N_LINES
    need = n_led * n_lines * 3
    if len(rgb) != need:
        raise ValueError("rgb size %d != %d" % (len(rgb), need))
    return struct.pack(HDR_FMT, config.MAGIC, seq & 0xFFFF, n_led, n_lines, 0) + rgb


def parse_header(buf):
    if len(buf) < HDR_SIZE:
        return None
    magic, seq, n_led, n_lines, flags = struct.unpack(HDR_FMT, bytes(buf[:HDR_SIZE]))
    if magic != config.MAGIC:
        return None
    return seq, n_led, n_lines, flags
