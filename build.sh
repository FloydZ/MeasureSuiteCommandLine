#!/usr/bin/env bash

# build assemblyline
cd deps/AssemblyLine
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

