# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/home/duda/Downloads/programming/MeasureSuiteCommandLine/deps/cryptanalysislib"
  "/home/duda/Downloads/programming/MeasureSuiteCommandLine/build/_project-prefix/src/_project-build"
  "/home/duda/Downloads/programming/MeasureSuiteCommandLine/build/_project-prefix"
  "/home/duda/Downloads/programming/MeasureSuiteCommandLine/build/_project-prefix/tmp"
  "/home/duda/Downloads/programming/MeasureSuiteCommandLine/build/_project-prefix/src/_project-stamp"
  "/home/duda/Downloads/programming/MeasureSuiteCommandLine/build/_project-prefix/src"
  "/home/duda/Downloads/programming/MeasureSuiteCommandLine/build/_project-prefix/src/_project-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/duda/Downloads/programming/MeasureSuiteCommandLine/build/_project-prefix/src/_project-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/duda/Downloads/programming/MeasureSuiteCommandLine/build/_project-prefix/src/_project-stamp${cfgdir}") # cfgdir has leading slash
endif()
