import os
import clang.cindex
from clang.cindex import CursorKind, Type, TypeKind, AccessSpecifier

BASIC_TYPES = set(['void', 'bool', 'int', 'char', 'double', 'float', 'int32_t', 'int64_t', 'size_t', 'va_list'])
TYPES_BLACK_LIST = set([
    "ImGuiErrorLogCallback",
    "ImFont",
    "ImFontAtlas",
    "ImDrawCmd",
    "ImDrawList",
    "ImGuiStorage",
    "ImGuiContextHook",
    "ImGuiNavItemData",
    "ImGuiOldColumns",
    "ImGuiViewportP",
    "ImVector",
])


def parse_cpp_sources():
    _DIR = os.path.dirname(os.path.abspath(__file__))
    args = [
        # f"-DIMGUI_USER_CONFIG=<imconfig_user.h>",
        f"-I{_DIR}",
        f"-I{os.path.abspath(_DIR + '/../third-party/imgui')}",
        # f"-I{os.path.abspath(_DIR + '/../third-party/fmt/include')}",
        # f"-I{os.path.abspath(_DIR + '/../third-party/nanobind/include')}",
    ]
    for arg in args:
        print(arg)

    index = clang.cindex.Index.create()
    tu = index.parse('../third-party/imgui/imgui.cpp', args=args)
    return tu


def type_name_without_decoration(name):
    type_name = name.replace("const", "").replace("*", "").replace("&", "").strip()
    if type_name.find("<") >= 0:
        t0, t1 = type_name.split("<")
        t1 = t1.replace(">", "")
        t0 = t0.strip()
        t1 = t1.strip()
        return t0, t1
    return (type_name, )


def find_api(node, export_api_names, api_dict):
    if node.kind == CursorKind.FUNCTION_DECL:
        if node.spelling not in export_api_names:
            return
        if node.spelling.startswith("_") or node.spelling == 'operator new':
            return

        no_black_list_arg = True
        method = dict(name=node.spelling, return_type=node.type.get_result().spelling, args=[])
        # print(node.type.get_result().spelling, node.spelling, end=' (')
        for t in node.get_arguments():
            type_name = ''
            for x in t.get_tokens():
                if x.spelling != t.spelling:
                    type_name += ' ' + x.spelling
            type_name = type_name.strip()
            method['args'].append(dict(type=type_name, name=t.spelling, cursor=t))
            for name in type_name_without_decoration(type_name):
                if name in TYPES_BLACK_LIST:
                    no_black_list_arg = False

        #     print(method['args'][-1]['type'], method['args'][-1]['name'], end=', ')
        # print(')')

        if no_black_list_arg:
            api_dict[node.spelling] = method


def find_structs(node, white_list, results):
    if white_list is not None and node.spelling not in white_list:
        return
    if node.kind == CursorKind.STRUCT_DECL:  # and node.spelling.startswith("Im"):

        struct_name = node.spelling
        results[struct_name] = dict(fields=[], constructors=[], methods=[])

        # inspect children
        for child in node.get_children():
            # only public
            if child.access_specifier != AccessSpecifier.PUBLIC:
                continue

            # field
            if child.kind == CursorKind.FIELD_DECL:
                field = dict(name=child.spelling, type=child.type.spelling)
                results[struct_name]['fields'].append(field)
            elif child.kind == CursorKind.CONSTRUCTOR:
                constructor = dict(args=[])
                for t in child.get_arguments():
                    constructor['args'].append(dict(type=t.type.spelling, name=t.spelling))
                results[struct_name]['constructors'].append(constructor)
            elif child.kind == CursorKind.CXX_METHOD:
                fn = child.spelling
                method = dict(name=fn, args=[], return_type=child.type.get_result().spelling, is_const=child.is_const_method())
                for t in child.get_arguments():
                    type_name = ''
                    for x in t.get_tokens():
                        if x.spelling != t.spelling:
                            type_name += ' ' + x.spelling
                    type_name = type_name.strip()
                    method['args'].append(dict(type=type_name, name=t.spelling, cursor=t))
                results[struct_name]['methods'].append(method)


def generate_binding_code():
    code = ''
    code += '#include "api.hpp"\n'
    code += '#include <nanobind/stl/string.h>\n\n'
    code += 'namespace nb = nanobind;\n\n'
    code += 'void imgui_def_api(nb::module_ & m) {\n'

    # def gen_api_code(name, children):
    #     pass

    # for n, v in all_api.items():
    #     code += gen_api_code(n, v)

    # ! handle 'va_list'

    code += '}\n'
    return code


if __name__ == "__main__":
    # Parse cpp source files
    tu = parse_cpp_sources()

    # At first, get all IMGUI_API functions
    imgui_api_names = []
    for node in tu.cursor.get_children():
        lst = -1000
        idx = 0
        for x in node.get_tokens():
            if x.spelling == "IMGUI_API":
                lst = idx
            if lst + 2 == idx:
                imgui_api_names.append(x.spelling)
            idx += 1

    # Secondly, parse api functions and get return types and arguments
    api_dict = dict()
    for c in tu.cursor.get_children():
        find_api(c, imgui_api_names, api_dict)

    # Collect all types used in api
    necessary_types = set()
    for _, method in api_dict.items():
        names = type_name_without_decoration(method['return_type'])
        for arg in method['args']:
            names += type_name_without_decoration(arg['type'])
        for n in names:
            if n in BASIC_TYPES:
                continue
            if n in TYPES_BLACK_LIST:
                continue
            necessary_types.add(n)
    for type_name in necessary_types:
        print(type_name)
    print(len(necessary_types))

    # Get all structs
    struct_dict = dict()
    for c in tu.cursor.get_children():
        find_structs(c, necessary_types, struct_dict)
    for name in struct_dict:
        print(name)

# # generate code
# code = generate_binding_code()
# with open("bind-imgui/api_auto.cpp", "w") as fp:
#     print(code, file=fp)
