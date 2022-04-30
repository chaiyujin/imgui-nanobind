#include <GLFW/glfw3.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/tensor.h>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>

#include "bind-imgui/bind-imgui.hpp"

namespace nb = nanobind;

// * -------------------------------------------------------------------------------------------------------------- * //
// *                                          GLFWwindow Pointer Conversion                                         * //
// * -------------------------------------------------------------------------------------------------------------- * //

struct GLFWwindow {};  // Opaque
CYTHON_PTR_CASTER(GLFWwindow);  // Custom caster

// * -------------------------------------------------------------------------------------------------------------- * //
// *                                                      Test                                                      * //
// * -------------------------------------------------------------------------------------------------------------- * //

static void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
    printf("press %d\n", scancode);
    if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    }
}

void set_key_callback(CythonPtr<GLFWwindow> window) {
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

    nb::class_<CythonPtr<ImGuiContext>>(m, "ImGuiContextCythonPtr");

    m.def("create_context", []() {
        IMGUI_CHECKVERSION();
        auto * ptr = ImGui::CreateContext();
        printf("creat context: %u\n", (intptr_t)ptr);
        return ptr;
        // return CythonPtr<ImGuiContext>{ImGui::CreateContext()};
    }, nb::rv_policy::automatic_reference);

    // m.def("destroy_context", [](CythonPtr<ImGuiContext> context) {
    //     ImGui::DestroyContext(context.ptr);
    //     printf("Destroy! %lu\n", (intptr_t)context.ptr);
    // }, nb::arg("context") = CythonPtr<ImGuiContext>{0});

    m.def("style_colors_dark", [](ImGuiContext * _ptr) {
        ImGui::StyleColorsDark();
    }, nb::arg("_ptr").none());

    m.def("new_frame", []() {
        ImGui::NewFrame();
    });
    m.def("render", []() {
        ImGui::Render();
    });

    m.def("demo", [](nb::tensor<nb::numpy, bool, nb::shape<1>> & p_open) {
        ImGui::ShowDemoWindow((bool*)p_open.data());
    }, nb::arg("p_open"));

    m.def("impl_init", [](CythonPtr<GLFWwindow> window) {
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
