import glfw
import ctypes
import imgui


def cpp_address(p):
    return ctypes.cast(p, ctypes.c_void_p).value


def main():

    if not glfw.init():
        return

    window = glfw.create_window(720, 600, "Opengl GLFW Window", None, None)

    # imgui.set_key_callback(cpp_address(window))
    imgui.set_key_callback(window)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
