#pragma once
#include "enums.hpp"
#include "types.hpp"

void imgui_bind_all(nanobind::module_ & m) {
    imgui_def_enums(m);
    imgui_def_types(m);
}
