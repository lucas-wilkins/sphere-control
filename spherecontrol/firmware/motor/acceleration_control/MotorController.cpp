//
// Created by lucas on 18/04/2026.
//

#include "MotorController.h"

#include <cmath>
#include <iomanip>
#include <iostream>
#include <algorithm>

MotorController::MotorController(
    double accelerationStepsPerSecondSquared,
    double minimumSpeedStepsPerSecond,
    double maximumSpeedStepsPerSecond,
    tVoidIntFunction forwardStepFunction,
    tVoidIntFunction backwardStepFunction,
    tVoidFunction noStepFunction,
    double executionTimeCorrectionMicros)
{
    // Check that input makes sense
    if (maximumSpeedStepsPerSecond <= minimumSpeedStepsPerSecond)
    {
        isError = true;
        return;
    }


    // Save the parameters
    a = accelerationStepsPerSecondSquared;
    vMax = maximumSpeedStepsPerSecond;
    vMin = minimumSpeedStepsPerSecond;
    correction = executionTimeCorrectionMicros;

    // Calculate things from the table
    minimumDtMicros = 1e6 / vMax;
    maximumDtMicros = 1e6 / vMin;

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

    // Bind the functions
    forwardStep = forwardStepFunction;
    backwardStep = backwardStepFunction;
    noStep = noStepFunction;

    // Initial state
    currentPosition = 0;
    targetPosition = 0;
    velocityIndex = 0;
}

// Destructor, just needs to remove the table we allocated
MotorController::~MotorController()
{
    delete[] velocityTable;
}

/**
 * Print out the velocity table
 */
void MotorController::printVelocityTable()
{
    for (int i = 0; i < maximumVelocityIndex; i++)
    {
        std::cout << std::setw(4) << i << ", " << velocityTable[i] << std::endl;
    }
}

/**
 * Check the motor callbacks work
 */
void MotorController::checkSteps()
{
    forwardStep(0);
    backwardStep(0);
}

bool MotorController::errorState()
{
    return isError;
}

void print(const char* msg)
{
    std::cout << msg << std::endl;
}

/**
 * Main loop of the controller
 */
void MotorController::update()
{

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
