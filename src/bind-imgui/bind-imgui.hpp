#pragma once
#include "types.hpp"

void imgui_bind_all(nanobind::module_ & m) {
    imgui_def_types(m);
}
