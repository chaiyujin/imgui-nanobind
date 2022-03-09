CMAKE_MINIMUM_REQUIRED(VERSION 3.17)
PROJECT(imgui)
SET(CMAKE_C_STANDARD 11)
SET(CMAKE_CXX_STANDARD 17)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)
SET(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Get external libs
SET(EXT_ROOT ${PROJECT_SOURCE_DIR}/../third-party)

ADD_SUBDIRECTORY("${EXT_ROOT}/fmt" fmt)
ADD_SUBDIRECTORY("${EXT_ROOT}/nanobind" nanobind)

# ImGui
LIST(APPEND IMGUI_INC_DIRS "${EXT_ROOT}/imgui")
LIST(APPEND IMGUI_HEADERS
    "${EXT_ROOT}/imgui/imconfig.h"
    "${EXT_ROOT}/imgui/imgui_internal.h"
    "${EXT_ROOT}/imgui/imgui.h"
    "${EXT_ROOT}/imgui/imstb_rectpack.h"
    "${EXT_ROOT}/imgui/imstb_textedit.h"
    "${EXT_ROOT}/imgui/imstb_truetype.h"
)
LIST(APPEND IMGUI_SOURCES
    "${EXT_ROOT}/imgui/imgui_demo.cpp"
    "${EXT_ROOT}/imgui/imgui_draw.cpp"
    "${EXT_ROOT}/imgui/imgui_tables.cpp"
    "${EXT_ROOT}/imgui/imgui_widgets.cpp"
    "${EXT_ROOT}/imgui/imgui.cpp"
)
# ImGui backends
LIST(APPEND IMGUI_IMPL_INC_DIRS "${EXT_ROOT}/imgui/backends")
LIST(APPEND IMGUI_IMPL_SOURCES
    "${EXT_ROOT}/imgui/backends/imgui_impl_glfw.cpp"
    "${EXT_ROOT}/imgui/backends/imgui_impl_opengl3.cpp"
)

find_package(glfw3 REQUIRED)
find_package(Python COMPONENTS Interpreter Development Development.Module REQUIRED)

add_executable(test_glfw main.cpp)
target_link_libraries(test_glfw glfw)

nanobind_add_module(imgui ${IMGUI_SOURCES} ${IMGUI_IMPL_SOURCES}
    bind.cpp
    bind-imgui/enums_auto.cpp
    bind-imgui/types.cpp
)
target_include_directories(imgui PRIVATE ${IMGUI_INC_DIRS} ${IMGUI_IMPL_INC_DIRS})
target_link_libraries(imgui PRIVATE glfw fmt)
