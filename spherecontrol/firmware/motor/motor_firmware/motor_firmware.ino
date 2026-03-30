#include "MotorMessages.h"

#define IS_STAGE

#define MOTOR_STEPS_PER_REVOLUTION 64000 // 5 x 32 x 400
#define ENCODER_STEPS_PER_REVOLUTION 4096
#define GEAR_RATIO 5

#define STEP_PIN 2
#define DIR_PIN 3
#define STEP_DELAY 10

#ifdef IS_STAGE
  #define MOTOR_ID STAGE_MOTOR_ID
#else
  #define MOTOR_ID SPHERE_MOTOR_ID
#endif

#define BUFFER_SIZE 128

/*
 *  State variables
 */

// Position variables
volatile long target_position_steps = 0;
volatile long actual_position_steps = 0;
long actual_position_encoder = 0;

volatile bool moving = false; // State variable for whether its moving
volatile bool lock = false; // Used to prevent motor from stepping

// Communication
byte serial_buffer[BUFFER_SIZE];
int bytesRead;


/*
 *  Messages
 */

byte identify_response[] = {IDENTIFY, MOTOR_ID};
byte unknown[] = {UNKNOWN_REQUEST};
byte serial_success[] = {SERIAL_SUCCESS};
byte serial_error[] = {SERIAL_ERROR};
byte is_moving[] = {IS_MOVING};
byte not_moving[] = {NOT_MOVING};
byte position_response[] = {REPORT_STATE, 
                            NOT_MOVING, 
                            0, 0, 0, 0, 
                            0, 0, 0, 0};




void set_moving(bool is_moving) {
  // Set the moving state variable, and show LEDS
  moving = is_moving;
  if (moving) {
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    digitalWrite(LED_BUILTIN, LOW);
  }
}


void send_OK() {
  // Send acknowledgement
  Serial.write(serial_success, 1);
}

void send_ERROR() {
  // Send an error message
  Serial.write(serial_error, 1);
}


void send_UNKNOWN() {
  // Send message for unknown request
  Serial.write(unknown, 1);
}

void send_ID() {
  // Send message identifying this component
  Serial.write(identify_response, 2);
}


void send_STATE() {
  // Send a message with the position as reported by encoder, and current step position
  const long encoder = actual_position_encoder;
  const long steps = actual_position_steps;
  
  if (moving) {
    position_response[1] = IS_MOVING;
  } else {
    position_response[1] = NOT_MOVING;
  }
  
  memcpy(&position_response[2], &encoder, 4);
  memcpy(&position_response[6], &steps, 4);
  
  Serial.write(position_response, 10);
}

void set_position(long target_position) {
  // Set the target position


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


  lock = true;
  actual_position_steps = new_actual;
  target_position_steps = target;
  lock = false;
  
  set_moving(true); // Needs to go after the target is set, otherwise

}



/*
 *
 *    Main Arduino methods
 *
 */


void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(57600);

  digitalWrite(STEP_PIN, LOW);
  set_moving(true);
}


void loop() {
  // Sensor and serial control loop

  if (Serial.available()) {
    byte first_byte = Serial.read();

    switch(first_byte) {

      case IDENTIFY:
        send_ID();
        
        break;

      case QUERY_STATE:
        send_STATE();
        
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

        break;


      default:
        send_UNKNOWN();
    }

  }
}

void loop1() {
  // Motor driver

  if (!lock) { // Don't move while locked, because the state might be inconsistent

    if (target_position_steps < actual_position_steps) {
      // Step down
      digitalWrite(DIR_PIN, LOW);
      delayMicroseconds(STEP_DELAY);

      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(STEP_DELAY);
      digitalWrite(STEP_PIN, LOW);
      
      actual_position_steps--;
      
    } else if (target_position_steps > actual_position_steps) {
      // Step up
      digitalWrite(DIR_PIN, HIGH);
      delayMicroseconds(STEP_DELAY);
      
      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(STEP_DELAY);
      digitalWrite(STEP_PIN, LOW);
      
      actual_position_steps++;

    } else {
      // Equal, set moving status
      set_moving(false);
    }
  }
}