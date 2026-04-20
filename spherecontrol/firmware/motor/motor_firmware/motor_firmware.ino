#include <SPI.h>
#include "MotorMessages.h"
#include "filter.h"

// #define IS_STAGE

#define MOTOR_STEPS_PER_REVOLUTION 64000 // 5 x 32 x 400
#define ENCODER_STEPS_PER_REVOLUTION 4096
#define GEAR_RATIO 5

#define STEP_PIN 3
#define DIR_PIN 2

// This is the number of microseconds we expect the motor control call to take
// 500 cycles at 133MHz is around 4us
#define ACCELERATION_CONTROL_EXECUTION_CORRECTION_MICROS 0.0

/* Serial communication stuff */

#ifdef IS_STAGE
  #define MOTOR_ID STAGE_MOTOR_ID
  #define REVERSE_ENCODER
  #define MAX_SPEED_STEPS_PER_SECOND 2e4
  #define MIN_SPEED_STEPS_PER_SECOND 1e3
  #define ACCELERATION_STEPS_PER_SECOND_SQ 3e5
#else
  #define MOTOR_ID SPHERE_MOTOR_ID
  #define LINEAR
  #define REVERSE_ENCODER
  #define MAX_SPEED_STEPS_PER_SECOND 2e4
  #define MIN_SPEED_STEPS_PER_SECOND 1e3
  #define ACCELERATION_STEPS_PER_SECOND_SQ 1e5
#endif

#define BUFFER_SIZE 128

/* AMT Communication constants */

/* Pins for SPI
 *
 * MISO  GP16 (green)
 * CS    GP17 (yellow)
 * SCK   GP18 (orange)
 * MOSI  GP19 (white)
 */
#define ENCODER_CS_PIN  17
#define AMT22_NOP       0x00
#define AMT22_ZERO      0x70
#define AMT22_TURNS     0xA0
#define RESOLUTION      12
#define AMT_SPI_DELAY   3

/*
 *  State variables
 */

// Position variables
volatile long currentPosition = 0;
volatile long targetPosition = 0;
volatile long actual_position_encoder = 0;
volatile int velocityIndex = 0;

int maximumVelocityIndex;
int* velocityTable;

long low_limit = -MOTOR_STEPS_PER_REVOLUTION;
long high_limit = MOTOR_STEPS_PER_REVOLUTION;

volatile bool moving = false; // State variable for whether its moving
volatile bool lock = false; // Used to prevent motor from stepping
volatile bool lock1 = false;

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
byte limit_response[] = {REPORT_LIMITS,
                         0, 0, 0, 0,
                         0, 0, 0, 0};

// Filtering
MedianFilter3 filter = MedianFilter3(ENCODER_STEPS_PER_REVOLUTION);


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
  
  #ifdef REVERSE_ENCODER
    const long encoder = ENCODER_STEPS_PER_REVOLUTION - actual_position_encoder - 1;
  #else
    const long encoder = actual_position_encoder;
  #endif

  const long steps = currentPosition;
  
  if (moving) {
    position_response[1] = IS_MOVING;
  } else {
    position_response[1] = NOT_MOVING;
  }
  
  memcpy(&position_response[2], &encoder, 4);
  memcpy(&position_response[6], &steps, 4);
  
  Serial.write(position_response, 10);
}

void send_LIMITS() {
  // Send current limit values
  memcpy(&limit_response[1], &low_limit, 4);
  memcpy(&limit_response[5], &high_limit, 4);
  
  Serial.write(limit_response, 9);

}

void set_position(long target_position) {
  // Set the target position

  #ifdef LINEAR

    //long target = max(min(target_position, high_limit), low_limit); // This doesn't seem to work correctly
    long target;
    if (target_position > high_limit) {
      target = high_limit;
    } else {
      if (target < low_limit) {
        target = low_limit;
      } else {
        target = target_position;
      }
    }

    writeTransfer(0, target);

  #else
  
    long actual = currentPosition; // Read current position so the variable doesn't change in this method

    // Get the new actual position, and calculate how much this differs from the previous one, so the other
    //  loop can update safely
    long new_actual = currentPosition % MOTOR_STEPS_PER_REVOLUTION;
    long delta = actual - new_actual;

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

    writeTransfer(delta, target);
  
  #endif
  
  set_moving(true); // Needs to go after the target is set, otherwise
}

void increment_position(long delta) {
  // Increment the target position
  set_position(targetPosition + delta);
}

/*
 * Checksums from the examples
 */
bool verifyChecksumSPI(uint16_t message)
{
  //checksum is invert of XOR of bits, so start with 0b11, so things end up inverted
  uint16_t checksum = 0x3;
  for(int i = 0; i < 14; i += 2)
  {
    checksum ^= (message >> i) & 0x3;
  }
  return checksum == (message >> 14);
}

void readSPI() {

  //set the CS signal to low
  digitalWrite(ENCODER_CS_PIN, LOW);
  delayMicroseconds(AMT_SPI_DELAY);

  //read the two bytes for position from the encoder, starting with the high byte
  uint16_t encoderPosition = SPI.transfer(AMT22_NOP) << 8; //shift up 8 bits because this is the high byte
  delayMicroseconds(AMT_SPI_DELAY);
  encoderPosition |= SPI.transfer(AMT22_NOP); //we do not need a specific command to get the encoder position, just no-op

  //set the CS signal to high
  digitalWrite(ENCODER_CS_PIN, HIGH);


  if (verifyChecksumSPI(encoderPosition)) //position was good, print to serial stream
  {
    encoderPosition &= 0x3FFF; //discard upper two checksum bits
    if (RESOLUTION == 12) {
      encoderPosition = encoderPosition >> 2; //on a 12-bit encoder, the lower two bits will always be zero
    }

    actual_position_encoder = filter.apply(encoderPosition);
  }
  else 
  {

  }
}


/*
 *
 *    Main Arduino methods
 *
 */


void setup() {

  // Pin Modes
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(ENCODER_CS_PIN, OUTPUT);

  digitalWrite(LED_BUILTIN, HIGH);

  // Serial
  Serial.begin(57600);

  /*
   * Data for controlling motor stepping
   */

  // Parameters
  double a = ACCELERATION_STEPS_PER_SECOND_SQ * 2;
  double vMax = MAX_SPEED_STEPS_PER_SECOND * 2;
  double vMin = MIN_SPEED_STEPS_PER_SECOND * 2;
  double correction = ACCELERATION_CONTROL_EXECUTION_CORRECTION_MICROS / 2;

  // Calculate things from the table

  const double acceleration_time = (vMax - vMin) / a;
  maximumVelocityIndex = 0.5*a*acceleration_time*acceleration_time +
      acceleration_time * vMin + 1;

  velocityTable = new int[maximumVelocityIndex];

  velocityTable[0] = static_cast<int>((1e6 / vMin) - correction);

  const double v02 = vMin*vMin;
  for (int i = 0; i < maximumVelocityIndex-1; i++)
  {
      const double deltaT = (
          sqrt(v02 + 2 * a * (i+1)) -
          sqrt(v02 + 2 * a * i)) / a ;

      velocityTable[i+1] = static_cast<int>(1e6 * deltaT - correction);
  }

  // Initial state
  currentPosition = 0;
  targetPosition = 0;
  velocityIndex = 0;


  // SPI Control
  SPI.beginTransaction(SPISettings(125000, MSBFIRST, SPI_MODE0));
  SPI.begin();
  digitalWrite(ENCODER_CS_PIN, LOW); // Set chip select low
}

/*
 *
 *   Interface loop
 *
 */

void loop() {
  // Sensor and serial control loop

  readSPI();
  delayMicroseconds(50);

  if (Serial.available()) {
    byte first_byte = Serial.read();

    switch(first_byte) {

      case IDENTIFY:
        send_ID();
        
        break;

      case QUERY_STATE:
        send_STATE();
        
        break;

      case QUERY_LIMITS:
        send_LIMITS();

        break;

      case SET_LIMITS:

        // Set the limits (measured in steps)
        bytesRead = Serial.readBytes(serial_buffer, 8);
        if (bytesRead == 8) {
          long low;
          long high;

          memcpy(&low, &serial_buffer[0], 4);
          memcpy(&high, &serial_buffer[4], 4);
          
          if (high >= low) {
            low_limit = low;
            high_limit = high;
            send_OK();
          } else {
            send_ERROR();
          }

        } else {
          send_ERROR();
        }

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


      case INCREMENT_STEPS:

        // Set the position in steps

        bytesRead = Serial.readBytes(serial_buffer, 4);
        if (bytesRead == 4) {
          long delta;
          memcpy(&delta, &serial_buffer[0], 4);
          increment_position(delta);
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

/*
 *   Motor controll stuff
 */

// Callback for forward stepping
void forwardStep(int microseconds) {
  digitalWrite(DIR_PIN, HIGH);
  delayMicroseconds(microseconds);

  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(microseconds);
  digitalWrite(STEP_PIN, LOW);
}

// Callback for backward stepping
void backwardStep(int microseconds) {
  digitalWrite(DIR_PIN, LOW);
  delayMicroseconds(microseconds);

  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(microseconds);
  digitalWrite(STEP_PIN, LOW);
}

void noStep() {
  set_moving(false);
}

/*
 *  These are for safely communicating betwen threads
 */

long transferDelta = 0;
long transferTarget = 0;
volatile int transferLock = 0;

void acquire_lock() {
    while (__atomic_test_and_set(&transferLock, __ATOMIC_ACQUIRE)) {
        // spin
    }
}

void release_lock() {
    __atomic_clear(&transferLock, __ATOMIC_RELEASE);
}

void writeTransfer(long positionDelta, long positionTarget) {
  
  acquire_lock();

  transferDelta += positionDelta;
  transferTarget = positionTarget;

  release_lock();

}

void readTransfer(volatile long* delta, volatile long* target) {
  
  acquire_lock();

  *delta += transferDelta;
  transferDelta = 0;
  *target = transferTarget;

  release_lock();
}

/*
 *
 *  Main motor driver thread
 *
 */

void loop1() {

    readTransfer(&currentPosition, &targetPosition); // Update the position and target position if set in loop

    const int dt = velocityTable[abs(velocityIndex)];

    // Positive overshoot
    if ((velocityIndex > 0) && (currentPosition + velocityIndex > targetPosition))
    {
        velocityIndex -= 1;
        currentPosition += 1;
        forwardStep(dt);
        return;
    }

    // Negative overshoot
    if ((velocityIndex < 0) && (currentPosition + velocityIndex < targetPosition))
    {
        velocityIndex += 1;
        currentPosition -= 1;
        backwardStep(dt);
        return;
    }

    // Positive long distance
    if (currentPosition + velocityIndex < targetPosition)
    {
        velocityIndex = std::min(velocityIndex + 1, maximumVelocityIndex - 1);
        currentPosition += 1;
        forwardStep(dt);
        return;
    }

    // Positive, slow down
    if ((currentPosition < targetPosition) && (targetPosition <= currentPosition + velocityIndex))
    {
        velocityIndex -= 1;
        currentPosition += 1;
        forwardStep(dt);
        return;
    }

    // Negative long distance
    if (currentPosition + velocityIndex > targetPosition)
    {
        velocityIndex = std::max(velocityIndex - 1, 1-maximumVelocityIndex);
        currentPosition -= 1;
        backwardStep(dt);
        return;
    }

    // Negative slow down
    if ((currentPosition > targetPosition) && (targetPosition >= currentPosition + velocityIndex))
    {
        velocityIndex += 1;
        currentPosition -= 1;
        backwardStep(dt);
        return;
    }

    noStep();


}