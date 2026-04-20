cmake_minimum_required(VERSION 4.0)
project(acceleration_control)

set(CMAKE_CXX_STANDARD 20)

add_executable(acceleration_control main.cpp
        MotorController.cpp
        MotorController.h
)

target_link_options(acceleration_control PRIVATE
        -static
        -static-libgcc
        -static-libstdc++
)