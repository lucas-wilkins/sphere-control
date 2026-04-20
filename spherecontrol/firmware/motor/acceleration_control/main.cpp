#include <iostream>
#include "MotorController.h"
/*
#include <x86intrin.h>
#include <windows.h>

void pin_to_core() {
    DWORD_PTR mask = 1; // core 0
    SetThreadAffinityMask(GetCurrentThread(), mask);
}*/

void forward_step(int microseconds)
{
    std::cout << "1, " << microseconds;
}

void backward_step(int microseconds)
{
    std::cout << "-1, " << microseconds;
}

void no_step()
{
    std::cout << "0, 0";
}

int main()
{

    //pin_to_core();

    long testPositions[] = {1000, 1200, 1500, 1200, 500,  0,   500, -100};
    long testLengths[] = {  1000, 200,  200,  1000, 1000, 200, 1000, 1000};

    int n = sizeof(testLengths) / sizeof(testLengths[0]);

    MotorController* controller = new MotorController(
        1.5e7,
        1e3,
        1e5,
        forward_step,
        backward_step,
        no_step,
        4.0);

    //controller->checkSteps();
    //controller->printVelocityTable();



    for (int i=0; i<n; i++)
    {
        long position = testPositions[i];
        long length = testLengths[i];

        controller->targetPosition = position;

        for (int j=0; j<length; j++)
        {
            // unsigned long long start = __rdtsc();

            controller->update();

            // unsigned long long end = __rdtsc();

            std::cout
              << ", " << controller->currentPosition
              << ", " << controller->targetPosition
              << ", " << controller->velocityIndex
              //<< ", " << (end-start)
              << std::endl;

        }
    }
}