#include <GLFW/glfw3.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>

#include "bind-imgui/bind-imgui.hpp"
#include "bind-imgui/raw_ptr.hpp"


namespace nb = nanobind;

// * -------------------------------------------------------------------------------------------------------------- * //
// *                                          GLFWwindow Pointer Conversion                                         * //
// * -------------------------------------------------------------------------------------------------------------- * //

// Opaque
struct GLFWwindow {};
// Custom caster
namespace nanobind::detail {
template <> struct type_caster<PtrWrapper<GLFWwindow>> {
    NB_TYPE_CASTER(PtrWrapper<GLFWwindow>, const_name("PtrWrapper<GLFWwindow>"));

    bool from_python(handle src, uint8_t flags, cleanup_list * cleanup) noexcept {
        /* Extract PyObject from handle */
        PyObject *source = src.ptr();

        Py_buffer view = {0};
        bool success = (PyObject_GetBuffer(source, &view, 0) != -1);
        if (success) {
            value.ptr = (GLFWwindow*)(((size_t*)view.buf)[0]);
            // printf("buf %lu\n", value.addr);
        }
        PyBuffer_Release(&view);
        PyErr_Clear();

        if (!success) {
            /* Try converting into a Python integer value */
            PyObject *tmp = PyNumber_Long(source);
            if (tmp) {
                value.ptr = (GLFWwindow*)PyLong_AsSize_t(tmp);
                Py_DECREF(tmp);
            }
            /* Ensure return code was OK (to avoid out-of-range errors etc) */
            success = (value.ptr != nullptr && !PyErr_Occurred());
            if (!success) {
                value.ptr = nullptr;
            }
            // printf("int %lu %d\n", value.addr, success);
        }
        return success;
    }

    static handle from_cpp(PtrWrapper<GLFWwindow> const & value, rv_policy, cleanup_list *) noexcept {
        return PyLong_FromSize_t((size_t)(intptr_t)value.ptr);
    }
};
} // namespace nanobind::detail


// namespace nanobind::detail {
// template <> struct type_caster<const char *> {
//     NB_TYPE_CASTER(const char *, const_name("const_char_ptr"));

//     bool from_python(handle src, uint8_t flags, cleanup_list * cleanup) noexcept {
//         /* Extract PyObject from handle */
//         PyObject *source = src.ptr();
//         const char * value = PyUnicode_AsUTF8AndSize(src.ptr(), nullptr);
//         printf("%s\n", value);
//         return true;
//     }

//     static handle from_cpp(const char * const & value, rv_policy, cleanup_list *) noexcept {
//         return nb::str(value);
//     }
// };
// } // namespace nanobind::detail

// * -------------------------------------------------------------------------------------------------------------- * //
// *                                                      Test                                                      * //
// * -------------------------------------------------------------------------------------------------------------- * //

static void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
    printf("press %d\n", scancode);
    if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    }
}

void set_key_callback(PtrWrapper<GLFWwindow> window) {
    glfwSetKeyCallback(window.ptr, key_callback);
}

void test_key_callback(nanobind::module_ & m) {
    m.def("set_key_callback", &set_key_callback);
}

void naive_demo_bind(nanobind::module_ & m) {

    m.def("test_char_ptr", [](nb::str & str) {
        printf("%s\n", str.c_str());
    });

    m.def("get_IO", &ImGui::GetIO, nb::rv_policy::reference);
    m.def("get_style", &ImGui::GetStyle, nb::rv_policy::reference);

    nb::class_<PtrWrapper<ImGuiContext>>(m, "ImGuiContextPtrWrapper");

    m.def("create_context", []() {
        IMGUI_CHECKVERSION();
        return PtrWrapper<ImGuiContext>{ImGui::CreateContext()};
    }, nb::rv_policy::move);

    m.def("destroy_context", [](PtrWrapper<ImGuiContext> context) {
        ImGui::DestroyContext(context.ptr);
        printf("Destroy! %lu\n", (intptr_t)context.ptr);
    }, nb::arg("context") = PtrWrapper<ImGuiContext>{0});

    m.def("style_colors_dark", []() {
        ImGui::StyleColorsDark();
    });

    m.def("new_frame", []() {
        ImGui::NewFrame();
    });
    m.def("render", []() {
        ImGui::Render();
    });

    m.def("demo", []() {
        ImGui::ShowDemoWindow();
    });

    m.def("impl_init", [](PtrWrapper<GLFWwindow> window) {
        ImGui_ImplGlfw_InitForOpenGL(window.ptr, true);
        ImGui_ImplOpenGL3_Init("#version 150");
    });
    m.def("impl_shutdown", []() {
        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplGlfw_Shutdown();
    });
    m.def("impl_new_frame", []() {
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
    });
    m.def("impl_render", []() {
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
    });
}

NB_MODULE(imgui, m) {
    imgui_bind_all(m);

    test_key_callback(m);

    naive_demo_bind(m);
}
