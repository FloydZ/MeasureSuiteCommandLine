cmake_minimum_required(VERSION 3.5)
project(MeasureSuiteCommandLine C CXX)

# set some appropriated flags and configurations
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_VERBOSE_MAKEFILE ON)



# needed for nvim
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "")
if(CMAKE_EXPORT_COMPILE_COMMANDS)
    set(CMAKE_CXX_STANDARD_INCLUDE_DIRECTORIES
            ${CMAKE_CXX_IMPLICIT_INCLUDE_DIRECTORIES})
endif()

# compile flags
set(DEBUG_FLAGS "-g -DDEBUG -Wall -Wpedantic -pedantic")
set(RELEASE_FLAGS "-g -O3 -march=native -DDEBUG -Wall -Wpedantic -pedantic")
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} ${DEBUG_FLAGS}")
set(CMAKE_C_FLAGS_RLEASE "${CMAKE_C_FLAGS_RELEASE} ${RELEASE_FLAGS}")

include(FetchContent)
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

include_directories("deps/MeasureSuite/lib/src/include")
include_directories("deps/MeasureSuite/lib/src")
include_directories("MeasureSuiteCommandLine")
link_directories("deps/MeasureSuite/lib")
link_directories("deps/AssemblyLine/.libs")


add_executable(main MeasureSuiteCommandLine/main.c)
target_link_libraries(main measuresuite assemblyline)
target_compile_options(main PRIVATE -DUSE_MAIN)

add_library(wrapper SHARED MeasureSuiteCommandLine/main.c)
target_link_libraries(wrapper measuresuite assemblyline)

add_subdirectory(test)
