#pragma once
#include <nanobind/nanobind.h>
#include <imgui.h>
#include <imgui_internal.h>

void imgui_def_types(nanobind::module_ & m);

#define CLASS_CASTER(Value_)                                                                        \
    using Value = Value_;                                                                           \
    static constexpr bool IsClass = true;                                                           \
    static constexpr auto Name = const_name<Value>();                                               \
    template <typename T_> using Cast = movable_cast_t<T_>;                                         \
    operator Value*() { return value; }                                                             \
    operator Value&() { if (!value) raise_next_overload(); return *value; }                         \
    operator Value&&() && { if (!value) raise_next_overload(); return (Value &&) *value; }          \
    Value *value = nullptr;                                                                         \
    template <typename T>                                                                           \
    NB_INLINE static handle from_cpp(T &&value, rv_policy policy, cleanup_list *cleanup) noexcept { \
        Value *value_p;                                                                             \
        if constexpr (is_pointer_v<T>) value_p = (Value *) value;                                   \
        else                           value_p = (Value *) &value;                                  \
        return nb_type_put(&typeid(Value), value_p, infer_policy<T>(policy), cleanup, nullptr);     \
    }                                                                                               \
    bool try_init(handle src, uint8_t flags, cleanup_list *cleanup) noexcept {                      \
        return nb_type_get(&typeid(Value), src.ptr(), flags, cleanup, (void **) &value);            \
    }
