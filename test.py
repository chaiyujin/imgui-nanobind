import glfw
import ctypes
from build import imgui


def main():

    if not glfw.init():
        return

    window = glfw.create_window(720, 600, "Opengl GLFW Window", None, None)
    print(type(window), window.dummy)
    # imgui.set_key_callback(window)

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
