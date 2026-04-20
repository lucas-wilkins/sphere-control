#define STEP_PIN 3
#define DIR_PIN 2
#define MAX_SPEED_STEPS_PER_SECOND 2e4
#define MIN_SPEED_STEPS_PER_SECOND 1e3
#define ACCELERATION_STEPS_PER_SECOND_SQ 3e5
#define ACCELERATION_CONTROL_EXECUTION_CORRECTION_MICROS 0


//MotorController* controller;

// Callback for forward stepping
void forwardStep(int microseconds) {
  digitalWrite(DIR_PIN, HIGH);
  delayMicroseconds(microseconds);

  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(microseconds);
  digitalWrite(STEP_PIN, LOW);

  //Serial.print("Forward ");
  //Serial.println(microseconds);
}

// Callback for backward stepping
void backwardStep(int microseconds) {
  digitalWrite(DIR_PIN, LOW);
  delayMicroseconds(microseconds);

  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(microseconds);
  digitalWrite(STEP_PIN, LOW);

  
  //Serial.print("Backward ");
  //Serial.println(microseconds);
}

void noStep() {
  // Serial.println("No step");
  delay(10);
}



long maximumVelocityIndex;
int* velocityTable;

volatile long currentPosition;
volatile long targetPosition;
volatile long velocityIndex;


void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

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


  Serial.begin(57600);

  delay(500);

  Serial.println("Starting...");

  for (int i=0; i<maximumVelocityIndex; i++) {
    Serial.print(i);
    Serial.print(", ");
    Serial.println(velocityTable[i]);
  }

}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  targetPosition = 5000;
  delay(1000);

  digitalWrite(LED_BUILTIN, LOW);
  targetPosition = 0;
  delay(1000);
}


void loop1() {

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

// void loop1() {
//   controller->update();
// }