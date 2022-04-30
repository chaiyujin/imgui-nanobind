#include "api.hpp"

namespace nb = nanobind;

void imgui_def_api(nb::module_ & m) {

    m.def("image",
        [](int user_texture_id, const ImVec2& size, const ImVec2& uv0, const ImVec2& uv1,
           const ImVec4& tint_col, const ImVec4& border_col) -> void {
            return ImGui::Image((ImTextureID)(intptr_t)user_texture_id, size, uv0, uv1, tint_col, border_col);
        },  
        nb::arg("tex_id"),
        nb::arg("size"),
        nb::arg("uv0") = ImVec2(0, 0),
        nb::arg("uv1") = ImVec2(1, 1),
        nb::arg("tint_col") = ImVec4(1, 1, 1, 1),
        nb::arg("border_col") = ImVec4(0, 0, 0, 0)
    );

    m.def("image_button",
        [](int user_texture_id, const ImVec2& size, const ImVec2& uv0, const ImVec2& uv1,
           int frame_padding, const ImVec4& bg_col, const ImVec4& tint_col) -> bool {
            return ImGui::ImageButton((ImTextureID)(intptr_t)user_texture_id, size, uv0, uv1, frame_padding, bg_col, tint_col);
        },
        nb::arg("tex_id"),
        nb::arg("size"),
        nb::arg("uv0") = ImVec2(0, 0),
        nb::arg("uv1") = ImVec2(1, 1),
        nb::arg("frame_padding") = -1,
        nb::arg("bg_col") = ImVec4(0, 0, 0, 0),
        nb::arg("tint_col") = ImVec4(1, 1, 1, 1)
    );

}
