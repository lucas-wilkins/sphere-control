#include <FastLED.h>
#include "LightMessages.h"

#define BOTTOM_PIN    4
#define TOP_PIN       3
#define BOTTOM_N_LEDS 75
#define TOP_N_LEDS    78
#define LED_TYPE      WS2812B
#define COLOR_ORDER   GRB
#define COLOR_BYTES   459

CRGB bottom_leds[BOTTOM_N_LEDS];
CRGB top_leds[TOP_N_LEDS];

void setup() {
  FastLED.addLeds<LED_TYPE, BOTTOM_PIN, COLOR_ORDER>(bottom_leds, BOTTOM_N_LEDS);
  FastLED.addLeds<LED_TYPE, TOP_PIN, COLOR_ORDER>(top_leds, TOP_N_LEDS);
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(57600);
}

byte identify_response[] = {IDENTIFY, LIGHT_ID};
byte unknown[] = {UNKNOWN_REQUEST};
byte serial_success[] = {SERIAL_SUCCESS};
byte serial_error[] = {SERIAL_ERROR};

byte serial_buffer[COLOR_BYTES];

int bytesRead;

void send_OK() {
  Serial.write(serial_success, 1);
}

void send_ERROR() {
  Serial.write(serial_error, 1);
}

void send_UNKNOWN() {
  Serial.write(unknown, 1);
}

void send_ID() {
  Serial.write(identify_response, 2);
}

void setLightsToBuffer() {

  for (int i=0; i<BOTTOM_N_LEDS; i++) {
    int start = 3*i;
    bottom_leds[i] = CRGB(serial_buffer[start],serial_buffer[start+1],serial_buffer[start+2]);
  }
  
  for (int i=0; i<TOP_N_LEDS; i++) {
    int start = 3*(i+75);
    top_leds[i] = CRGB(serial_buffer[start],serial_buffer[start+1],serial_buffer[start+2]);
  }

  FastLED.show();

}

void setLight(int light_id, byte red, byte green, byte blue) {
  
  for (int i=0; i<TOP_N_LEDS; i++) {
    top_leds[i] = CRGB(0,0,0);
  }

  for (int i=0; i<BOTTOM_N_LEDS; i++) {
    bottom_leds[i] = CRGB(0,0,0);
  }

  if (light_id >= BOTTOM_N_LEDS) {
    top_leds[light_id - BOTTOM_N_LEDS] = CRGB(red, green, blue);
  } else {
    bottom_leds[light_id] = CRGB(red, green, blue);
  }

  FastLED.show();
}



void lightsOff() {

  for (int i=0; i<TOP_N_LEDS; i++) {
    top_leds[i] = CRGB(0,0,0);
  }

  for (int i=0; i<BOTTOM_N_LEDS; i++) {
    bottom_leds[i] = CRGB(0,0,0);
  }

  FastLED.show();
}


void loop() {

  if (Serial.available()) {
    byte first_byte = Serial.read();

    switch(first_byte) {

      case IDENTIFY:
        send_ID();
        break;

      case SINGLE_LIGHT:
        bytesRead = Serial.readBytes(serial_buffer, 1);
        if (bytesRead == 1) {
          setLight(serial_buffer[0], 255,255,255);
          send_OK();
        } else {
          send_ERROR();
        }

        break;

      case SINGLE_LIGHT_COLOR:
        bytesRead = Serial.readBytes(serial_buffer, 4);
        if (bytesRead == 4) {
          setLight(serial_buffer[0], serial_buffer[1], serial_buffer[2], serial_buffer[3]);
          send_OK();
        } else {
          send_ERROR();
        }

        break;

      case FULL_LIGHT_SPEC:

        bytesRead = Serial.readBytes(serial_buffer, COLOR_BYTES);
        if (bytesRead == COLOR_BYTES) {
          setLightsToBuffer();
          send_OK();
        } else {
          send_ERROR();
        }

        break;

      case ALL_OFF:
        lightsOff();
        send_OK();
        break;

      default:
        send_UNKNOWN();
    }

  }

}
