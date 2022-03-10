import os
import clang.cindex
from clang.cindex import CursorKind, Type, TypeKind, AccessSpecifier


def find_api(node, results):
    if node.kind == CursorKind.FUNCTION_DECL:
        if node.spelling.startswith("_") or node.spelling == 'operator new':
            return

        print(node.spelling)
        for arg in node.get_arguments():
            type_name = ''
            for x in arg.get_tokens():
                if x.spelling == '=':
                    break
                if x.spelling != arg.spelling:
                    type_name += ' ' + x.spelling
            type_name = type_name.strip()
            if type_name.find('size_t') >= 0:
                pass
            else:
                type_name = arg.type.spelling
            print(' ', type_name, arg.spelling)


_DIR = os.path.dirname(os.path.abspath(__file__))
all_structs = dict()
imgui_config = '<imconfig_user.h>'
args = [
    f"-DIMGUI_USER_CONFIG={imgui_config}",
    f"-I{_DIR}",
    f"-I{os.path.abspath(_DIR + '/../third-party/fmt/include')}",
    f"-I{os.path.abspath(_DIR + '/../third-party/nanobind/include')}",
]

index = clang.cindex.Index.create()
tu = index.parse('../third-party/imgui/imgui.cpp', args=args)
for c in tu.cursor.get_children():
    find_api(c, all_structs)


code = """#include "api.hpp"
#include <nanobind/stl/string.h>

namespace nb = nanobind;

void imgui_def_api(nb::module_ & m) {

"""

# for n, v in all_structs.items():
#     code += gen_struct_code(n, v)

code += "}\n"

with open("bind-imgui/api_auto.cpp", "w") as fp:
    print(code, file=fp)
