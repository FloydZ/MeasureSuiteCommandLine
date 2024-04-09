#!/usr/bin/env bash

# build assemblyline
cd deps/AssemblyLine
./autogen.sh
./configure
make 
cd ../../

# build MeasureSuite
cd deps/MeasureSuite
patch -N Makefile < ../measuresuite.patch
make
cd ../../

# build local project
mkdir -p build
cd build 
cmake ..
make 
cd ..

# build tests
cd test
cc c/test.c -c -o test.o
cc c/test2.c -c -o test2.o
