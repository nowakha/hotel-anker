# AnkerPI02 — Teensy discovery (2026-07-21)

## Was hängt am USB?

| Feld | Wert |
|------|------|
| Host | AnkerPI02 (`192.168.8.106`) |
| Device | **Teensyduino USB Serial** |
| USB ID | `16c0:0483` |
| Serial | `2923720` |
| Node | `/dev/ttyACM0` |
|  | `usb-Teensyduino_USB_Serial_2923720-if00` |

**Nicht** mehr der Raspberry Pi Pico (der zuvor `2e8a:0005` war).

## Reverse Engineering GPIO

- Auf dem Pi liegt **kein** Teensy-Sketch / Hex / Pin-Config.
- USB-CDC: kein Banner, `write()` → **Write timeout** (Firmware liest Serial offenbar nicht / anderes Protokoll).
- Für 8 parallele WS2812-Linien auf Teensy ist der De-facto-Standard **PJRC OctoWS2811**.

### Abgeleitete Pinbelegung (OctoWS2811 Default)

`defaultPinList = {2, 14, 7, 8, 6, 20, 21, 5}`

| Strip / Line | Teensy Pin |
|--------------|------------|
| 0 / #1 | **2** |
| 1 / #2 | **14** |
| 2 / #3 | **7** |
| 3 / #4 | **8** |
| 4 / #5 | **6** |
| 5 / #6 | **20** |
| 6 / #7 | **21** |
| 7 / #8 | **5** |

- **Teensy 3.x:** diese 8 Pins sind fest.
- **Teensy 4.x:** Default identisch; Sketch *kann* eine custom `pinList` setzen (nicht nachweisbar ohne Source).
- Mit **Octo28 Adaptor**: dieselben Kanäle auf den RJ45-Ausgängen.

Diagramm: [`teensy-octows2811-pins.png`](teensy-octows2811-pins.png)

## Offen

1. Teensy 3.2 vs 4.0/4.1 (USB-ID allein reicht nicht).
2. Ob custom pins im Flash stehen.
3. Welches USB-Framebuffer-Protokoll die Firmware erwartet (nicht unser Pico-`ANKR`).
