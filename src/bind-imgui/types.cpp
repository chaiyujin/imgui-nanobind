#include "types.hpp"
#include <nanobind/stl/string.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/pair.h>
#include <fmt/format.h>
#include <fmt/ostream.h>

namespace nb = nanobind;
namespace nanobind::detail {
    template <> struct type_caster<ImVec2> {
        using Type = ImVec2;
        static constexpr auto Name = const_name<Type>();
        static constexpr bool IsClass = true;
        template <typename T> using Cast = movable_cast_t<T>;
        operator Type*() { return value; }
        operator Type&() { if (!value) raise_next_overload(); return *value; }
        operator Type&&() && { if (!value) raise_next_overload(); return (Type &&) *value; }
        Type *value = nullptr;

        NB_INLINE bool from_python(handle src, uint8_t flags, cleanup_list *cleanup) noexcept {
            bool got = nb_type_get(&typeid(Type), src.ptr(), flags, cleanup, (void **) &value);
            if (got) { }
            else if (nb::isinstance<nb::tuple>(src)) {
                auto tmp = nb::cast<nb::tuple>(src);
                if (tmp.size() == 2) {
                    value = new ImVec2(nb::cast<float>(tmp[0]), nb::cast<float>(tmp[1]));
                    got = true;
                }
                else {
                    fmt::print("[Error] ImVec2: Given tuple don't has 2 elements, but {}!", tmp.size());
                }
            }
            return got;
        }
        template <typename T>
        NB_INLINE static handle from_cpp(T &&value, rv_policy policy, cleanup_list *cleanup) noexcept {
            Type *value_p;
            if constexpr (is_pointer_v<T>)
                value_p = (Type *) value;
            else
                value_p = (Type *) &value;
            return nb_type_put(&typeid(Type), value_p, infer_policy<T>(policy), cleanup, nullptr);
        }
    };
} // namespace nanobind::detail


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
}
