#include "types.hpp"
#include <nanobind/stl/string.h>
#include <fmt/format.h>
#include <imgui.h>
#include <imgui_internal.h>

namespace nb = nanobind;

void imgui_def_types(nb::module_ & m) {

    nb::class_<ImVec2>(m, "ImVec2")
        // members
        .def_readwrite("x", &ImVec2::x)
        .def_readwrite("y", &ImVec2::y)
        // init
        .def(nb::init<>())
        .def(nb::init<float, float>())
        // operators
        .def("__getitem__", [](ImVec2 const & v, int idx) {
            return v[idx];
        })
        // repr
        .def("__repr__", [](ImVec2 const & v) {
            return fmt::format("ImVec2({}, {})", v.x, v.y);
        })
    ;

    nb::class_<ImVec4>(m, "ImVec4")
        // members
        .def_readwrite("x", &ImVec4::x)
        .def_readwrite("y", &ImVec4::y)
        .def_readwrite("z", &ImVec4::z)
        .def_readwrite("w", &ImVec4::w)
        // init
        .def(nb::init<>())
        .def(nb::init<float, float, float, float>())
        // repr
        .def("__repr__", [](ImVec4 const & v) {
            return fmt::format("ImVec4({}, {}, {}, {})", v.x, v.y, v.z, v.w);
        })
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
        .def("contains_point", [](ImRect const & r, ImVec2 const & p) -> bool { return r.Contains(p); })
        .def("contains_rect",  [](ImRect const & r, ImRect const & b) -> bool { return r.Contains(b); })
        .def("overlaps",       [](ImRect const & r, ImRect const & b) -> bool { return r.Overlaps(b); })
        .def("add_point",      [](ImRect & r, ImVec2 const & p) { r.Add(p); })
        .def("add_rect",       [](ImRect & r, ImRect const & b) { r.Add(b); })
        .def("expand_both",    [](ImRect & r, float b) { r.Expand(b); })
        .def("expand_each",    [](ImRect & r, ImVec2 const & b) { r.Expand(b); })
        .def("translate",      &ImRect::Translate)
        .def("translate_x",    &ImRect::TranslateX)
        .def("translate_y",    &ImRect::TranslateY)
        .def("clip_with",      &ImRect::ClipWith)
        .def("clip_with_full", &ImRect::ClipWithFull)
        .def("floor",          &ImRect::Floor)
        .def("is_inverted",    &ImRect::IsInverted)
        .def("to_vec4",        &ImRect::ToVec4)
    ;
}
