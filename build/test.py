import glfw
import ctypes
import imgui
from imgui import ImVec2, ImVec4, ImRect
from OpenGL import GL as gl


def cpp_address(p):
    return ctypes.cast(p, ctypes.c_void_p).value


def main():

    if not glfw.init():
        return

    window = glfw.create_window(720, 600, "Opengl GLFW Window", None, None)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # imgui.set_key_callback(cpp_address(window))
    imgui.set_key_callback(window)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)  # enable vsync

    rect = ImRect((0, 0), (10, 20))
    print(rect.contains((0, 0)))
    print(rect.contains(ImRect((0, 0), (10, 22))))
    print(rect.get_center())
    print(rect.to_vec4())

    imgui.create_context()
    imgui.style_colors_dark()

    print(int(imgui.ImGuiItemFlags.ReadOnly))

    imgui.impl_init(window)
    io = imgui.get_IO()
    style = imgui.get_style()
    style.window_padding = (20, 20)
    print(io.display_size)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        imgui.impl_new_frame()
        imgui.new_frame()

        imgui.demo()
        print(io.display_size)

        imgui.render()
        w, h = glfw.get_framebuffer_size(window)
        gl.glViewport(0, 0, w, h)
        gl.glClearColor(0.0, 0.2, 0.2, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        imgui.impl_render()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
