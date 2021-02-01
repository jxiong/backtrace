cmake_minimum_required(VERSION 3.10)

# set the project name
project(Backtrace)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_CXX_COMPILER g++)

# add "no-optimize-sibling-calls" so that we can get full stack backtrace.
# add "no-builtin" to avoid compilter skipping malloc wrapper
set(CMAKE_CXX_FLAGS "-O2 -fno-omit-frame-pointer -Wall -fno-optimize-sibling-calls -fno-builtin")

find_package(absl REQUIRED)
find_package(spdlog REQUIRED)

find_package(PkgConfig REQUIRED)
pkg_search_module(Unwind REQUIRED libunwind)

#add_library(backtrace src/backtrace.cc)
#target_link_libraries(backtrace unwind absl::debugging)

add_library(malloc_wrapper src/malloc_wrapper.cc)
target_link_libraries(malloc_wrapper PRIVATE unwind absl::debugging)
target_link_options(malloc_wrapper INTERFACE "-Wl,--wrap,malloc" "-Wl,--wrap,free")

add_library(myfunc src/myfunc.cc)
target_link_libraries(myfunc malloc_wrapper)

# add the executable
add_executable(main src/main.cc)
target_link_libraries(main myfunc)
