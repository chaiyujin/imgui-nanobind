#pragma once
#include <imgui.h>
#include <imgui_internal.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/tensor.h>
#include "stl/array.h"
#include "stl/optional.h"

template <typename T, size_t N>
using IMBIND_Array = std::optional<
    nanobind::tensor<nanobind::numpy, T, nanobind::shape<N>>
>;
template <typename T>
using IMBIND_Data = std::optional<
    nanobind::tensor<nanobind::numpy, T>
>;

// * -------------------------------------------------------------------------------------------------------------- * //
// *                                               Pointer From Cython                                              * //
// * -------------------------------------------------------------------------------------------------------------- * //

template <typename T>
struct CythonPtr {
    T * ptr = nullptr;
};

#define CYTHON_PTR_CASTER(TYPE)                                                         \
namespace nanobind::detail {                                                            \
template <> struct type_caster<CythonPtr<TYPE>> {                                       \
    NB_TYPE_CASTER(CythonPtr<TYPE>, const_name("CythonPtr<TYPE>"));                     \
    bool from_python(handle src, uint8_t flags, cleanup_list * cleanup) noexcept {      \
        PyObject *source = src.ptr();                                                   \
        Py_buffer view = {0};                                                           \
        bool success = (PyObject_GetBuffer(source, &view, 0) != -1);                    \
        if (success) { value.ptr = (TYPE*)(((size_t*)view.buf)[0]); }                   \
        PyBuffer_Release(&view);                                                        \
        PyErr_Clear();                                                                  \
        if (!success) {                                                                 \
            PyObject *tmp = PyNumber_Long(source);                                      \
            if (tmp) {                                                                  \
                value.ptr = (TYPE*)PyLong_AsSize_t(tmp);                                \
                Py_DECREF(tmp);                                                         \
            }                                                                           \
            success = (value.ptr != nullptr && !PyErr_Occurred());                      \
            if (!success) { value.ptr = nullptr; }                                      \
        }                                                                               \
        return success;                                                                 \
    }                                                                                   \
    static handle from_cpp(CythonPtr<TYPE> const & value,                               \
                           rv_policy, cleanup_list *) noexcept {                        \
        return PyLong_FromSize_t((size_t)(intptr_t)value.ptr);                          \
    }                                                                                   \
};                                                                                      \
} 
