#include "MotorMessages.h"

#define IS_STAGE

#define MOTOR_STEPS_PER_REVOLUTION 25600 // 64 x 400
#define ENCODER_STEPS_PER_REVOLUTION 4096

#ifdef IS_STAGE
  #define MOTOR_ID STAGE_MOTOR_ID
#else
  #define MOTOR_ID SPHERE_MOTOR_ID
#endif

#define BUFFER_SIZE 128

volatile long target_position_steps = 0;
volatile long actual_position_steps = 0;
volatile bool moving = false;
long actual_position_encoder = 0;

void setup() {
  Serial.begin(57600);
}


byte identify_response[] = {IDENTIFY, MOTOR_ID};
byte unknown[] = {UNKNOWN_REQUEST};
byte serial_success[] = {SERIAL_SUCCESS};
byte serial_error[] = {SERIAL_ERROR};
byte position_response[] = {REPORT_POSITION, 0, 0, 0, 0, 0, 0, 0, 0};

byte serial_buffer[BUFFER_SIZE];

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


void send_POSITION() {
  const long encoder = actual_position_encoder;
  const long steps = actual_position_steps;
  memcpy(&position_response[1], &encoder, 4);
  memcpy(&position_response[5], &steps, 4);
  Serial.write(position_response, 9);
}

void set_position(long target_position) {
  long new_actual = actual_position_steps % MOTOR_STEPS_PER_REVOLUTION;

  long mid = target_position % MOTOR_STEPS_PER_REVOLUTION;
  
  long low = mid - MOTOR_STEPS_PER_REVOLUTION;
  long hi = mid + MOTOR_STEPS_PER_REVOLUTION;

  // Relative distance to each
  long low_dist = labs(low - new_actual);
  long mid_dist = labs(mid - new_actual);
  long hi_dist = labs(hi - new_actual);

  // Get the shortest of these
  long target;
  if (low_dist < mid_dist) {
    if (hi_dist < low_dist) {
      target = hi;
    } else {
      target = low;
    }
  } else {
    if (hi_dist < mid_dist) {
      target = hi;
    } else {
      target = mid;
    }
  }

  actual_position_steps = new_actual;
  target_position_steps = target;
  moving = true;

}

void loop() {
  // Sensor and serial control loop

  if (Serial.available()) {
    byte first_byte = Serial.read();

    switch(first_byte) {

      case IDENTIFY:
        send_ID();
        break;

      case GET_POSITION:
        send_POSITION();
        break;

      case GOTO_STEPS:

        // Set the position in steps

        bytesRead = Serial.readBytes(serial_buffer, 4);
        if (bytesRead == 4) {
          long target;
          memcpy(&target, &serial_buffer[0], 4);
          set_position(target);
          send_OK();
        } else {
          send_ERROR();
        }


      default:
        send_UNKNOWN();
    }

  }
}

void loop1() {
  // Motor driver

  /* Need to work out the direction it needs to turn in */

  if (target_position_steps < actual_position_steps) {
    // Step down
    actual_position_steps--;
  } else if (target_position_steps > actual_position_steps) {
    // Step up
    actual_position_steps++;
  } else {
    moving = false;
  }

  delayMicroseconds(20);
}