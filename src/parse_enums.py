import clang.cindex
from clang.cindex import CursorKind


def find_enums(node, results):
    if node.kind == CursorKind.ENUM_DECL:
        if node.spelling in results or not node.spelling.startswith("Im"):
            return
        if node.spelling.find("Private") >= 0 or node.spelling.find("Old") >= 0:
            return

        assert node.spelling not in results, "{} duplicated".format(node.spelling)
        results[node.spelling] = []
        enum_name = node.spelling.replace("Private_", "_")
        for child in node.get_children():
            # ImGui coding style, enum value starts with enum name.
            assert child.spelling.startswith(enum_name)
            results[node.spelling].append(child.spelling)


all_enums = dict()
# imgui.h, imgui_internal.h
index = clang.cindex.Index.create()
tu = index.parse('../third-party/imgui/imgui_internal.h')  # imgui.h is included
for c in tu.cursor.get_children():
    find_enums(c, all_enums)


def gen_enum_code(enum, values):
    _tmpl_enum_begin = '    nb::enum_<{}>(m, "{}")\n'
    _tmpl_enum_value = '        .value("{}", {}{})\n'
    _tmpl_enum_end   = '    ;\n\n'

    max_len = max(len(x) for x in values)
    code = ''

    # begin
    enum_new_name = enum
    if enum_new_name[-1] == '_':
        enum_new_name = enum_new_name[:-1]
    code += _tmpl_enum_begin.format(enum, enum_new_name)
    for val in values:
        txt = val.replace(enum, '')
        if txt.startswith("_"):
            txt = txt[1:]
        if txt == 'None':
            txt = 'NONE'
        padding = ' ' * (max_len - len(val))
        code += _tmpl_enum_value.format(txt, padding, val)
    code += _tmpl_enum_end

    return code


code = """#include "enums.hpp"

namespace nb = nanobind;

void imgui_def_enums(nb::module_ & m) {

"""

for enum, values in all_enums.items():
    code += gen_enum_code(enum, values)

code += "}"


with open("bind-imgui/enums_auto.cpp", "w") as fp:
    print(code, file=fp)
