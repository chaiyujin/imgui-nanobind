#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <GLFW/glfw3.h>

#include "bind-imgui/bind-imgui.hpp"

namespace nb = nanobind;

struct RawPtr {
    size_t addr = 0;
};

namespace nanobind::detail {
    template <> struct type_caster<RawPtr> {
        NB_TYPE_CASTER(RawPtr, const_name("RawPtr"));

        bool from_python(handle src, uint8_t flags, cleanup_list * cleanup) noexcept {
            /* Extract PyObject from handle */
            PyObject *source = src.ptr();

            Py_buffer view = {0};
            bool success = (PyObject_GetBuffer(source, &view, 0) != -1);
            if (success) {
                value.addr = ((size_t*)view.buf)[0];
                // printf("buf %lu\n", value.addr);
            }
            PyBuffer_Release(&view);
            PyErr_Clear();

            if (!success) {
                /* Try converting into a Python integer value */
                PyObject *tmp = PyNumber_Long(source);
                if (tmp) {
                    value.addr = PyLong_AsSize_t(tmp);
                    Py_DECREF(tmp);
                }
                /* Ensure return code was OK (to avoid out-of-range errors etc) */
                success = (value.addr != 0 && !PyErr_Occurred());
                if (!success) {
                    value.addr = 0;
                }
                // printf("int %lu %d\n", value.addr, success);
            }
            return success;
        }

        static handle from_cpp(RawPtr const & value, rv_policy, cleanup_list *) noexcept {
            return PyLong_FromSize_t(value.addr);
        }
    };
} // namespace nanobind::detail


static void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
    printf("press %d\n", scancode);
    if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    }
}

void set_key_callback(RawPtr window) {
    glfwSetKeyCallback((GLFWwindow*)window.addr, key_callback);
}

void test_key_callback(nanobind::module_ & m) {
    m.def("set_key_callback", &set_key_callback);
}

void naive_demo_bind(nanobind::module_ & m) {
    m.def("get_IO", &ImGui::GetIO, nb::rv_policy::reference);
    m.def("get_style", &ImGui::GetStyle, nb::rv_policy::reference);

    m.def("create_context", []() -> intptr_t {
        IMGUI_CHECKVERSION();
        return (intptr_t)ImGui::CreateContext();
    });
    m.def("destroy_context", []() {
        ImGui::DestroyContext();
    });
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

    m.def("impl_init", [](RawPtr window) {
        ImGui_ImplGlfw_InitForOpenGL((GLFWwindow *)window.addr, true);
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
