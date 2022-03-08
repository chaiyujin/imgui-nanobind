#include <nanobind/nanobind.h>
#include <GLFW/glfw3.h>

namespace nb = nanobind;

static void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
    printf("press %d\n", scancode);
    if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    }
}

void set_key_callback(int* window) {
    glfwSetKeyCallback((GLFWwindow*)window, key_callback);
}

NB_MODULE(imgui, m) {
    m.def("set_key_callback", &set_key_callback);
}
