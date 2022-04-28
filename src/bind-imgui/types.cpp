#include "types.hpp"
#include <nanobind/stl/string.h>

namespace nb = nanobind;

void imgui_def_types(nb::module_ & m) {

    nb::class_<ImVec2>(m, "ImVec2")
        .def_readwrite("x", &ImVec2::x)
        .def_readwrite("y", &ImVec2::y)
        .def(nb::init<>())
        .def(nb::init<float, float>())
        .def(nb::init_implicit<const nanobind::tuple &>())
        .def("__getitem__", nb::overload_cast<size_t>(&ImVec2::operator[], nb::const_))
        .def("__getitem__", nb::overload_cast<size_t>(&ImVec2::operator[]))
        .def("__setitem__", [](ImVec2 & self, size_t idx, const float & value) { self[idx] = value; })
        .def("__repr__",    &ImVec2::to_string)
    ;

    nb::class_<ImVec4>(m, "ImVec4")
        .def_readwrite("x", &ImVec4::x)
        .def_readwrite("y", &ImVec4::y)
        .def_readwrite("z", &ImVec4::z)
        .def_readwrite("w", &ImVec4::w)
        .def(nb::init<>())
        .def(nb::init<float, float, float, float>())
        .def(nb::init_implicit<const nanobind::tuple &>())
        .def("__repr__",    &ImVec4::to_string)
    ;

    nb::class_<ImRect>(m, "ImRect")
        .def_readwrite("Min", &ImRect::Min)
        .def_readwrite("Max", &ImRect::Max)
        .def(nb::init<>())
        .def(nb::init<const ImVec2 &, const ImVec2 &>())
        .def(nb::init<const ImVec4 &>())
        .def(nb::init<float, float, float, float>())
        .def("GetCenter",    &ImRect::GetCenter)
        .def("GetSize",      &ImRect::GetSize)
        .def("GetWidth",     &ImRect::GetWidth)
        .def("GetHeight",    &ImRect::GetHeight)
        .def("GetArea",      &ImRect::GetArea)
        .def("GetTL",        &ImRect::GetTL)
        .def("GetTR",        &ImRect::GetTR)
        .def("GetBL",        &ImRect::GetBL)
        .def("GetBR",        &ImRect::GetBR)
        .def("Contains",     nb::overload_cast<const ImVec2 &>(&ImRect::Contains, nb::const_))
        .def("Contains",     nb::overload_cast<const ImRect &>(&ImRect::Contains, nb::const_))
        .def("Overlaps",     &ImRect::Overlaps)
        .def("Add",          nb::overload_cast<const ImVec2 &>(&ImRect::Add))
        .def("Add",          nb::overload_cast<const ImRect &>(&ImRect::Add))
        .def("Expand",       nb::overload_cast<const float>(&ImRect::Expand))
        .def("Expand",       nb::overload_cast<const ImVec2 &>(&ImRect::Expand))
        .def("Translate",    &ImRect::Translate)
        .def("TranslateX",   &ImRect::TranslateX)
        .def("TranslateY",   &ImRect::TranslateY)
        .def("ClipWith",     &ImRect::ClipWith)
        .def("ClipWithFull", &ImRect::ClipWithFull)
        .def("Floor",        &ImRect::Floor)
        .def("IsInverted",   &ImRect::IsInverted)
        .def("ToVec4",       &ImRect::ToVec4)
    ;

}
