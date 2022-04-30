#pragma once

#include <array>
#include <nanobind/nanobind.h>

NAMESPACE_BEGIN(NB_NAMESPACE)
NAMESPACE_BEGIN(detail)

template <class T, size_t N> struct type_caster<std::array<T, N>> {
    using Value = std::array<T, N>;                                                     
    static constexpr bool IsClass = false;                                     
    static constexpr auto Name = const_name("array[") +
                                 concat(make_caster<T>::Name) +
                                 const_name("]");
    template <typename T_> using Cast = movable_cast_t<T_>;                    
    static handle from_cpp(Value *p, rv_policy policy, cleanup_list *list) {   
        if (!p)                                                                
            return none().release();                                           
        return from_cpp(*p, policy, list);                                     
    }                                                                          
    explicit operator Value *() { return &value; }                             
    explicit operator Value &() { return value; }                              
    explicit operator Value &&() && { return (Value &&) value; }               
    Value value;

    using Caster = make_caster<T>;

    bool from_python(handle src, uint8_t flags, cleanup_list *cleanup) noexcept {
        size_t size;
        PyObject *temp;

        /* Will initialize 'size' and 'temp'. All return values and
           return parameters are zero/NULL in the case of a failure. */
        PyObject **o = seq_get(src.ptr(), &size, &temp);

        Caster caster;
        bool success = (o != nullptr) && (size == N);

        if (success) {
            for (size_t i = 0; i < size; ++i) {
                if (!caster.from_python(o[i], flags, cleanup)) {
                    success = false;
                    break;
                }
                value[i] = ((Caster &&) caster).operator cast_t<T &&>();
            }
        }

        Py_XDECREF(temp);

        return success;
    }

    template <typename U>
    static handle from_cpp(U &&src, rv_policy policy, cleanup_list *cleanup) {
        object list = steal(PyList_New(src.size()));
        if (list) {
            Py_ssize_t index = 0;

            for (auto &value : src) {
                handle h =
                    Caster::from_cpp(forward_like<T>(value), policy, cleanup);

                PyList_SET_ITEM(list.ptr(), index++, h.ptr());
                if (!h.is_valid())
                    return handle();
            }
        }

        return list.release();
    }
};

NAMESPACE_END(detail)
NAMESPACE_END(NB_NAMESPACE)
