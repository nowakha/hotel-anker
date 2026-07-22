/*
 * AnkerPI02 Teensy pixel pusher — 8×512 WS2812 via OctoWS2811
 * USB Serial: ANKR frames (same layout as Pico)
 * Pins (OctoWS2811 default): 2, 14, 7, 8, 6, 20, 21, 5
 */
#include <Arduino.h>
#include <OctoWS2811.h>

#ifndef ANKER_MCU_NAME
#define ANKER_MCU_NAME "TEENSY"
#endif

static const int N_LED = 512;
static const int N_LINES = 8;
static const int HDR_SIZE = 10;

DMAMEM int displayMemory[N_LED * 6];
int drawingMemory[N_LED * 6];

static const int config = WS2811_GRB | WS2811_800kHz;
OctoWS2811 leds(N_LED, displayMemory, drawingMemory, config);

static uint8_t hdr[HDR_SIZE];
static int hdr_pos = 0;
static uint16_t frame_n_led = 0;
static uint8_t frame_n_lines = 0;
static uint32_t body_need = 0;
static uint32_t body_got = 0;
static uint8_t rgb[3];

enum State { WAIT_MAGIC, WAIT_HDR, WAIT_BODY };
static State state = WAIT_MAGIC;

static void show_black() {
  for (int i = 0; i < N_LED * N_LINES; i++) {
    leds.setPixel(i, 0);
  }
  leds.show();
}

static void on_hdr_complete() {
  frame_n_led = (uint16_t)hdr[6] | ((uint16_t)hdr[7] << 8);
  frame_n_lines = hdr[8];
  if (frame_n_led == 0 || frame_n_led > N_LED || frame_n_lines == 0 ||
      frame_n_lines > N_LINES) {
    state = WAIT_MAGIC;
    hdr_pos = 0;
    return;
  }
  body_need = (uint32_t)frame_n_led * (uint32_t)frame_n_lines * 3u;
  body_got = 0;
  state = WAIT_BODY;
}

static void on_body_byte(uint8_t b) {
  rgb[body_got % 3] = b;
  if ((body_got % 3) == 2) {
    uint32_t pix = body_got / 3;
    uint32_t line = pix / frame_n_led;
    uint32_t led = pix % frame_n_led;
    if (line < N_LINES && led < N_LED) {
      leds.setPixel(line * N_LED + led,
                    ((int)rgb[0] << 16) | ((int)rgb[1] << 8) | (int)rgb[2]);
    }
  }
  body_got++;
  if (body_got >= body_need) {
    leds.show();
    state = WAIT_MAGIC;
    hdr_pos = 0;
    body_got = 0;
  }
}

void setup() {
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && (millis() - t0) < 2000) {
    ;
  }
  Serial.println("anker-teensy boot");
  Serial.print("mcu=");
  Serial.println(ANKER_MCU_NAME);
  Serial.println("pins=2,14,7,8,6,20,21,5");
  Serial.print("n_led=");
  Serial.println(N_LED);
  Serial.print("n_lines=");
  Serial.println(N_LINES);
  Serial.println("octo begin...");
  leds.begin();
  show_black();
  Serial.println("ready");
}

void loop() {
  while (Serial.available() > 0) {
    uint8_t b = (uint8_t)Serial.read();
    if (state == WAIT_MAGIC) {
      if (b == 'A') {
        hdr[0] = b;
        hdr_pos = 1;
        state = WAIT_HDR;
      }
    } else if (state == WAIT_HDR) {
      hdr[hdr_pos++] = b;
      if (hdr_pos == 4) {
        if (hdr[1] != 'N' || hdr[2] != 'K' || hdr[3] != 'R') {
          state = WAIT_MAGIC;
          hdr_pos = 0;
          if (b == 'A') {
            hdr[0] = 'A';
            hdr_pos = 1;
            state = WAIT_HDR;
          }
        }
      } else if (hdr_pos >= HDR_SIZE) {
        on_hdr_complete();
      }
    } else {  // WAIT_BODY
      on_body_byte(b);
    }
  }
}
