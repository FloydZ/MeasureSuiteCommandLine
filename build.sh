#!/usr/bin/env bash

# build assemblyline
cd deps/AssemblyLine
./autogen.sh
./configure
make 
cd ../../

# build measuresuite
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

