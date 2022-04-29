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

    vec = ImVec2((10, 200))
    print(vec)
    vec[0] = 20
    print(vec)
    rect = ImRect((0, 0), (10, 20))
    print(rect.Contains((0, 0)))
    print(rect.Contains(ImRect(0, 0, 10, 22)))
    print(rect.GetCenter())
    print(rect.ToVec4())

    imgui_ctx = imgui.create_context()
    io = imgui.get_IO()
    print(io.IniFilename)
    io.IniFilename = "imgui_new.ini"

    imgui.style_colors_dark()

    imgui.test_char_ptr("Hellow!a")
    print(int(imgui.ImGuiItemFlags.ReadOnly))

    imgui.impl_init(window)

    is_open = False
    v_float = 0.0
    v_float2 = [0.0, 1.0]
    while not glfw.window_should_close(window):
        glfw.poll_events()

        imgui.impl_new_frame()
        imgui.new_frame()

        # imgui.demo()
        imgui.demo(is_open, 0, None)

        imgui.Begin("haha", True)
        imgui.Text("FUck you!")
        imgui.SliderFloat("Value", v_float, -10.0, 10.0)
        imgui.SliderFloat2("Value2", v_float2, -10.0, 10.0)
        imgui.End()

        imgui.render()
        w, h = glfw.get_framebuffer_size(window)
        gl.glViewport(0, 0, w, h)
        gl.glClearColor(0.0, 0.2, 0.2, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        imgui.impl_render()

        glfw.swap_buffers(window)

    print(io.IniFilename)
    imgui.impl_shutdown()
    imgui.destroy_context(imgui_ctx)
    glfw.terminate()


if __name__ == "__main__":
    main()
