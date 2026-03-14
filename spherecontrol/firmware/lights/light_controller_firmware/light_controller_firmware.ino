#include <FastLED.h>

#define BOTTOM_PIN    4
#define TOP_PIN       3
#define BOTTOM_N_LEDS 75
#define TOP_N_LEDS    78
#define LED_TYPE      WS2812B
#define COLOR_ORDER   GRB

CRGB bottom_leds[BOTTOM_N_LEDS];
CRGB top_leds[TOP_N_LEDS];

void setup() {
  FastLED.addLeds<LED_TYPE, BOTTOM_PIN, COLOR_ORDER>(bottom_leds, BOTTOM_N_LEDS);
  FastLED.addLeds<LED_TYPE, TOP_PIN, COLOR_ORDER>(top_leds, TOP_N_LEDS);
  pinMode(LED_BUILTIN, OUTPUT);
}

#define DELAY_TIME 500

void loop() {
  for (int i=0; i<TOP_N_LEDS; i++) {
    top_leds[i] = CRGB(0,255,0);
  }

  for (int i=0; i<BOTTOM_N_LEDS; i++) {
    bottom_leds[i] = CRGB(255,0,0);
  }

  FastLED.show();
  delay(DELAY_TIME);

}

/*
void loop() {

  digitalWrite(LED_BUILTIN, HIGH);

  for (int i=0; i<TOP_N_LEDS; i++) {
    top_leds[i] = CRGB(0,0,0);
  }

  for (int i=0; i<BOTTOM_N_LEDS; i++) {
    bottom_leds[i] = CRGB(255,0,0);
  }

  FastLED.show();
  delay(DELAY_TIME);


  for (int i=0; i<BOTTOM_N_LEDS; i++) {
    bottom_leds[i] = CRGB(0,255,0);
  }

  FastLED.show();
  delay(DELAY_TIME);


  for (int i=0; i<BOTTOM_N_LEDS; i++) {
    bottom_leds[i] = CRGB(0,0,255);
  }

  FastLED.show();
  delay(DELAY_TIME);

  
  digitalWrite(LED_BUILTIN, LOW);

  for (int i=0; i<BOTTOM_N_LEDS; i++) {
    bottom_leds[i] = CRGB(0,0,0);
  }

  for (int i=0; i<TOP_N_LEDS; i++) {
    top_leds[i] = CRGB(255,0,0);
  }

  FastLED.show();
  delay(DELAY_TIME);
  for (int i=0; i<TOP_N_LEDS; i++) {
    top_leds[i] = CRGB(0,255,0);
  }

  FastLED.show();
  delay(DELAY_TIME);
  for (int i=0; i<TOP_N_LEDS; i++) {
    top_leds[i] = CRGB(0,0,255);
  }

  FastLED.show();
  delay(DELAY_TIME);


}*/

