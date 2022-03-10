#pragma once
#include <nanobind/nanobind.h>

template <typename T>
struct PtrWrapper {
    T * ptr = nullptr;
};
