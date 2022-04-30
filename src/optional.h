#pragma once

#include <nanobind/nanobind.h>
#include <optional>

NAMESPACE_BEGIN(NB_NAMESPACE)
NAMESPACE_BEGIN(detail)

template <typename T> struct type_caster<std::optional<T>> {
    using Value = std::optional<T>;
    using Caster = make_caster<T>;

    static constexpr auto Name = Caster::Name;
    static constexpr bool IsClass = true;
    template <typename T_> using Cast = movable_cast_t<T_>;

    bool from_python(handle src, uint8_t flags,
                     cleanup_list *cleanup) noexcept {
        if (!src.ptr()) {
            return false;
        }
        if (src.is_none()) {
            value = std::nullopt;
            return true;
        }

        Caster caster;
        if (!caster.from_python(src, flags, cleanup)) {
            return false;
        }

        value.emplace(((Caster &&) caster).operator cast_t<T &&>());
        return true;
    }

    static handle from_cpp(Value *src, rv_policy policy,
                           cleanup_list *cleanup) noexcept {
        if (!src)
            return none().release();
        return from_cpp(*src, policy, cleanup);
    }

    template <typename U>
    static handle from_cpp(U &&src, rv_policy policy,
                           cleanup_list *cleanup) noexcept {
        if (src.has_value()) {
            handle h = Caster::from_cpp(forward_like<U>(src), policy, cleanup);
            if (h.is_valid())
                return h;
        }

        return none().release();
    }

    explicit operator Value *() { return &value; }
    explicit operator Value &() { return value; }
    explicit operator Value &&() && { return (Value &&) value; }

    Value value;
};

NAMESPACE_END(detail)
NAMESPACE_END(NB_NAMESPACE)
