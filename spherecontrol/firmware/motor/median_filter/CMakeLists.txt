cmake_minimum_required(VERSION 4.0)
project(median_filter)

set(CMAKE_CXX_STANDARD 20)

add_executable(median_filter
        main.cpp
        filter.cpp)
