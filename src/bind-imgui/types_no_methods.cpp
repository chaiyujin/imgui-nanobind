#include "types.hpp"

namespace nb = nanobind;

void imgui_def_types_no_methods(nb::module_ & m) {
    // ! Temporary working around for structs we don't access methods or fields,
    // ! but necessary as parameters for API.

    nb::class_<ImDrawData>(m, "ImDrawData");

}
