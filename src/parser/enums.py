import clang.cindex
from clang.cindex import CursorKind
from .utils import parse_imgui_cpp_sources


def insert_if_valid_enum(node, results):
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


def find_all_enums():
    all_enums = dict()
    tu = parse_imgui_cpp_sources('imgui.cpp')  # imgui.h is included
    for c in tu.cursor.get_children():
        if c.spelling == "ImGui":
            for k in c.get_children():
                insert_if_valid_enum(k, all_enums)
        else:
            insert_if_valid_enum(c, all_enums)
    for enum in sorted(list(all_enums.keys())):
        print(enum)
    print(len(all_enums), "enums")
    return all_enums


def generate_code_enums(all_enums):

    def _gen_code(enum, values):
        _tmpl_enum_begin = '    nb::enum_<{}>(m, "{}", nb::is_arithmetic())\n'
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

    # header
    code = ''
    code += '#include "enums.hpp"\n\n'
    code += 'namespace nb = nanobind;\n\n'
    code += 'void imgui_def_enums_auto(nb::module_ & m) {\n\n'

    for enum, values in all_enums.items():
        code += _gen_code(enum, values)

    # end
    code += "}"
    return code
