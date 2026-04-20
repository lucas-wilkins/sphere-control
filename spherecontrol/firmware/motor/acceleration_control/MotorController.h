
#ifndef ACCELATION_CONTROL_CONTROLLER_H
#define ACCELATION_CONTROL_CONTROLLER_H

#include <functional>
typedef std::function<void (int)> tVoidIntFunction;
typedef std::function<void (void)> tVoidFunction;

class MotorController
{
public:
    volatile long currentPosition;
    volatile long targetPosition;
    volatile int velocityIndex;

    MotorController(
        double accelerationStepsPerSecondSquared,
        double minimumSpeedStepsPerSecond,
        double maximumSpeedStepsPerSecond,
        tVoidIntFunction forwardStepFunction,
        tVoidIntFunction backwardStepFunction,
        tVoidFunction noStepFunction,
        double executionTimeCorrectionMicros);

    ~MotorController();

    void checkSteps();
    void printVelocityTable();
    bool errorState();

    void update();

private:
    double a;
    double vMax;
    double vMin;
    double correction;

    int minimumDtMicros;
    int maximumDtMicros;

    int maximumVelocityIndex;
    int* velocityTable;

    tVoidIntFunction forwardStep;
    tVoidIntFunction backwardStep;
    tVoidFunction noStep;

    bool isError = false;

};


#endif //ACCELATION_CONTROL_CONTROLLER_H