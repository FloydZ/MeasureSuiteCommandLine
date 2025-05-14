#!/usr/bin/env bash
# make sure everything is there
git submodule update --init

# go into the main directory
cd src/MeasureSuiteCommandLine

# build assemblyline
cd deps/AssemblyLine
./autogen.sh
./configure
make 
cd ../../

# build MeasureSuite
cd deps/MeasureSuite
git apply < ../measuresuite.patch
make
cd ../../

# build local project
#mkdir -p build
#cd build 
#cmake ..
#make 
#cd ..

# build tests
cc test/c/test.c -c -o test/test.o
cc test/c/test2.c -c -o test/test2.o
cc test/test.o -shared -o test/test.so

#cc test/c/test.c -c -o build/test/test.o
#cc test/c/test2.c -c -o build/test/test2.o
#cc build/test/test.o -shared -o build/test/test.so

# going back to the main project directory (not package directory)
cd ../..
