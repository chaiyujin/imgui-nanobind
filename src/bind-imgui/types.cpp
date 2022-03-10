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
        .def("__repr__", &ImVec2::to_string)
    ;

    nb::class_<ImVec4>(m, "ImVec4")
        .def_readwrite("x", &ImVec4::x)
        .def_readwrite("y", &ImVec4::y)
        .def_readwrite("z", &ImVec4::z)
        .def_readwrite("w", &ImVec4::w)
        .def(nb::init<>())
        .def(nb::init<float, float, float, float>())
        .def(nb::init_implicit<const nanobind::tuple &>())
        .def("__repr__", &ImVec4::to_string)
    ;

    nb::class_<ImRect>(m, "ImRect")
        // members
        .def_readwrite("min", &ImRect::Min)
        .def_readwrite("max", &ImRect::Max)
        // repr
        .def("__repr__", [](ImRect const & r) {
            return fmt::format("ImRect{{({}, {}), ({}, {})}}", r.Min.x, r.Min.y, r.Max.x, r.Max.y);
        })
        // init
        .def(nb::init<>())
        .def(nb::init<ImVec2 const &, ImVec2 const &>())
        .def(nb::init<ImVec4 const &>())
        .def(nb::init<float, float, float, float>())
        // methods
        .def("get_center",     &ImRect::GetCenter)
        .def("get_size",       &ImRect::GetSize)
        .def("get_width",      &ImRect::GetWidth)
        .def("get_height",     &ImRect::GetHeight)
        .def("get_area",       &ImRect::GetArea)
        .def("get_TL",         &ImRect::GetTL)
        .def("get_TR",         &ImRect::GetTR)
        .def("get_BL",         &ImRect::GetBL)
        .def("get_BR",         &ImRect::GetBR)
        .def("contains",       nb::overload_cast<ImVec2 const &>(&ImRect::Contains, nb::const_))
        .def("contains",       nb::overload_cast<ImRect const &>(&ImRect::Contains, nb::const_))
        .def("overlaps",       &ImRect::Overlaps)
        .def("add",            nb::overload_cast<ImVec2 const &>(&ImRect::Add))
        .def("add",            nb::overload_cast<ImRect const &>(&ImRect::Add))
        .def("expand",         nb::overload_cast<float>         (&ImRect::Expand))
        .def("expand",         nb::overload_cast<ImVec2 const &>(&ImRect::Expand))
        .def("translate",      &ImRect::Translate)
        .def("translate_x",    &ImRect::TranslateX)
        .def("translate_y",    &ImRect::TranslateY)
        .def("clip_with",      &ImRect::ClipWith)
        .def("clip_with_full", &ImRect::ClipWithFull)
        .def("floor",          &ImRect::Floor)
        .def("is_inverted",    &ImRect::IsInverted)
        .def("to_vec4",        &ImRect::ToVec4)
    ;

    nb::class_<ImGuiIO>(m, "ImGuiIO")
        // init
        .def(nb::init<>())
        // members
        .def_readwrite("display_size", &ImGuiIO::DisplaySize)
    ;

    nb::class_<ImGuiStyle>(m, "ImGuiStyle")
        // init
        .def(nb::init<>())
        // members
        .def_readwrite("window_padding", &ImGuiStyle::WindowPadding)
    ;
}
