"""Boot: drive 4 WS2812 lines, receive USB and optional UDP frames."""

import sys
import time

import config
import protocol
from ws2812_pio import Ws2812Lines

try:
    import uselect as select
except ImportError:
    import select

_LAST_SEQ = -1


def _has_wlan():
    try:
        import network

        return hasattr(network, "WLAN")
    except Exception:
        return False


def _wifi_connect():
    import network

    try:
        import secrets
    except ImportError:
        print("no secrets.py - USB-only mode")
        return None

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("wifi connecting to", secrets.WIFI_SSID)
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > config.WIFI_TIMEOUT_S * 1000:
                print("wifi timeout")
                return None
            time.sleep_ms(200)
    print("wifi", wlan.ifconfig())
    return wlan


def _udp_socket(port):
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", port))
    s.setblocking(False)
    return s


def _apply_frame(leds, body, n_led, n_lines):
    stride = n_led * 3
    for line in range(min(n_lines, leds.n_lines)):
        off = line * stride
        leds.fill_rgb(line, body[off : off + stride])
    leds.show()


def _drain_usb(stdin, poll_obj, usb_buf, max_bytes=8192):
    """Non-blocking drain: only read while poll says data is ready."""
    n = 0
    while n < max_bytes and poll_obj.poll(0):
        b = stdin.read(1)
        if not b:
            break
        usb_buf.extend(b)
        n += 1
    return n


def _parse_usb(leds, usb_buf):
    """Parse complete frames from usb_buf. Returns frames consumed."""
    global _LAST_SEQ
    got = 0
    while True:
        if len(usb_buf) < protocol.HDR_SIZE:
            break
        if usb_buf[:4] != config.MAGIC:
            idx = usb_buf.find(config.MAGIC)
            if idx < 0:
                del usb_buf[:-3]
                break
            del usb_buf[:idx]
            continue
        hdr = protocol.parse_header(usb_buf)
        if not hdr:
            del usb_buf[0]
            continue
        seq, n_led, n_lines, _flags = hdr
        need = protocol.frame_nbytes(n_led, n_lines)
        if len(usb_buf) < need:
            break
        body = memoryview(usb_buf)[protocol.HDR_SIZE : need]
        _apply_frame(leds, body, n_led, n_lines)
        _LAST_SEQ = seq
        got += 1
        del usb_buf[:need]
    return got


def main():
    global _LAST_SEQ
    print("anker-pico boot")
    print("platform", sys.platform)
    print("wlan", _has_wlan())

    leds = Ws2812Lines(config.PIN_LINES[: config.N_LINES], config.N_LED)
    leds.black()

    udp = None
    if _has_wlan():
        if _wifi_connect() is not None:
            try:
                udp = _udp_socket(config.UDP_PORT)
                print("udp listen", config.UDP_PORT)
            except Exception as e:
                print("udp fail", e)

    try:
        stdin = sys.stdin.buffer
    except Exception:
        stdin = None

    poll = select.poll()
    stdin_fd = None
    if stdin is not None:
        stdin_fd = sys.stdin
        poll.register(stdin_fd, select.POLLIN)
    if udp is not None:
        poll.register(udp, select.POLLIN)

    expect = protocol.frame_nbytes(config.N_LED, config.N_LINES)
    usb_buf = bytearray()
    frames = 0
    t_last = time.ticks_ms()

    print("ready expect_frame_bytes", expect, "pins", config.PIN_LINES[: config.N_LINES])

    while True:
        events = poll.poll(2)
        for fd, _ev in events:
            if udp is not None and fd is udp:
                try:
                    data, _addr = udp.recvfrom(expect + 64)
                except Exception:
                    continue
                hdr = protocol.parse_header(data)
                if not hdr:
                    continue
                seq, n_led, n_lines, _flags = hdr
                need = protocol.frame_nbytes(n_led, n_lines)
                if len(data) < need:
                    continue
                body = memoryview(data)[protocol.HDR_SIZE : need]
                _apply_frame(leds, body, n_led, n_lines)
                _LAST_SEQ = seq
                frames += 1
            elif stdin is not None and fd is stdin_fd:
                _drain_usb(stdin, poll, usb_buf)
                frames += _parse_usb(leds, usb_buf)

        if stdin is not None:
            if _drain_usb(stdin, poll, usb_buf, max_bytes=2048):
                frames += _parse_usb(leds, usb_buf)

        now = time.ticks_ms()
        if time.ticks_diff(now, t_last) >= 2000:
            print(
                "frames",
                frames,
                "last_seq",
                _LAST_SEQ,
                "usb_buf",
                len(usb_buf),
            )
            frames = 0
            t_last = now


if __name__ == "__main__":
    main()
