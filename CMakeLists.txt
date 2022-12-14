cmake_minimum_required(VERSION 3.20.1)
project(MeasureSuiteCommandLine)

# set some appropiated flags and configs
set(CMAKE_C_STANDARD 11)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_VERBOSE_MAKEFILE ON)
set(DEBUG_FLAGS "-g -DDEBUG -Wall -Wpedantic -pedantic")

set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} ${DEBUG_FLAGS}")

include(ExternalProject)

# first build assembly line
ExternalProject_Add(AssemblyLine_project
        SOURCE_DIR        ${CMAKE_SOURCE_DIR}/deps/AssemblyLine
        CONFIGURE_COMMAND cd <SOURCE_DIR> && ./autogen.sh
        COMMAND           cd <SOURCE_DIR> && ./configure
        BUILD_COMMAND     cd <SOURCE_DIR> && make
        INSTALL_COMMAND   "" # sudo make install
        TEST_COMMAND      ""
)

ExternalProject_Add(MeasureSuite_project
        SOURCE_DIR        ${CMAKE_SOURCE_DIR}/deps/MeasureSuite
        CONFIGURE_COMMAND ""
        COMMAND           ""
        BUILD_COMMAND     cd <SOURCE_DIR> && make
        INSTALL_COMMAND   ""
        TEST_COMMAND      ""
)



include_directories("deps/MeasureSuite/src/include")
link_directories("deps/MeasureSuite")
link_directories("deps/AssemblyLine/.libs")


add_executable(main src/main.c)
target_link_libraries(main measuresuite assemblyline)

add_library(all_lib SHARED src/lib.c)
