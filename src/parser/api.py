import os
import clang.cindex
from clang.cindex import CursorKind, Type, TypeKind, AccessSpecifier
from .utils import parse_imgui_cpp_sources, snake_style, type_names_without_decorations, Method, Argument

BASIC_TYPES = set(['void', 'bool', 'int', 'char', 'double', 'float', 'int32_t', 'int64_t', 'size_t', 'va_list'])
NUMBER_TYPES = set(['int', 'bool', 'float', 'double', 'size_t'])
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


def find_api(node, export_api_names, api_dict):
    if node.kind == CursorKind.FUNCTION_DECL:
        if node.spelling not in export_api_names:
            return
        if node.spelling.startswith("_") or node.spelling == 'operator new':
            return
        if node.spelling.startswith("Debug"):
            return
        if node.spelling.find("Callback") >= 0:
            return
        
        if node.spelling in api_dict:
            return

        method = Method(node)
        no_black_list_arg = True
        for arg in method.args:
            for n in type_names_without_decorations(arg.type):
                if n in TYPES_BLACK_LIST:
                    no_black_list_arg = False

        # method = dict(name=node.spelling, return_type=node.type.get_result().spelling, args=[])
        # # print(node.type.get_result().spelling, node.spelling, end=' (')
        # for t in node.get_arguments():
        #     type_name = ''
        #     for x in t.get_tokens():
        #         if x.spelling != t.spelling:
        #             type_name += ' ' + x.spelling
        #     type_name = type_name.strip()
        #     default_value = None
        #     if type_name.find("=") > 0:
        #         type_name, default_value = type_name.split("=")
        #         type_name = type_name.strip()
        #         default_value = default_value.strip()
        #     method['args'].append(dict(type=type_name, name=t.spelling, default_value=default_value, cursor=t))
        #     for name in type_names_without_decorations(type_name):
        #         if name in TYPES_BLACK_LIST:
        #             no_black_list_arg = False

        #     print(method['args'][-1]['type'], method['args'][-1]['name'], end=', ')
        # print(')')

        if no_black_list_arg:
            api_dict[node.spelling] = method


def generate_api_binding_code(api_dict):
    code = ''
    code += '#include "api.hpp"\n\n'
    code += 'namespace nb = nanobind;\n\n'
    code += 'void imgui_def_api_auto(nb::module_ & m) {\n\n'
    indent = '    '

    def gen_api_code(name, method: Method):
        part = indent
        # print(name, info)
        if method.return_type in ['void *']:
            return None

        # start
        part += f'm.def(\"{snake_style(name)}\", []('
        # args
        for i, arg in enumerate(method.args):
            # change name
            arg.name = '_' + arg.name
            type_name = arg.type

            # ! cannot handle so far
            if type_name in ['va_list', 'void *', 'void **', 'const void *', 'ImTextureID']:
                return None
            if type_name == "const char * const[]":
                return None

            # special
            base_type_name = type_names_without_decorations(type_name)[0]
            if type_name in ['const char *', 'char const *']:
                if arg.default_value not in ["NULL", "nullptr"]:
                    part += f'nb::str & {arg.name}'
                else:
                    part += f'std::optional<std::string> {arg.name}'
            elif type_name.find("*") >= 0 and base_type_name in NUMBER_TYPES:
                # print(type_name, name)
                part += f'IMBIND_Data<{base_type_name}> {arg.name}'
            elif type_name.find("[") >= 0 and base_type_name in NUMBER_TYPES:
                size = int(type_name.split('[')[1].replace(']', '').strip())
                # print(type_name, name, base_type_name, size)
                part += f'IMBIND_Array<{base_type_name}, {size}> {arg.name}'
            else:
                part += f'{type_name} {arg.name}'
            if i + 1 < len(method.args):
                part += ', '

        # return type
        part += f') -> {method.return_type}'
        # main body
        part += ' { '
        if method.return_type != 'void':
            part += 'return '
        part += f'ImGui::{name}('
        for i, arg in enumerate(method.args):
            type_name = arg.type

            # special
            base_type_name = type_names_without_decorations(type_name)[0]
            if type_name in ['const char *', 'char const *']:
                if arg.default_value not in ["NULL", "nullptr"]:
                    part += f'{arg.name}.c_str()'
                else:
                    part += f'(({arg.name}.has_value()) ? {arg.name}.value().c_str(): nullptr)'
            elif type_name.find("*") >= 0 and base_type_name in NUMBER_TYPES:
                part += f'(({arg.name}.has_value()) ? ({base_type_name}*){arg.name}.value().data(): nullptr)'
            elif type_name.find("[") >= 0 and base_type_name in NUMBER_TYPES:
                size = int(type_name.split('[')[1].replace(']', '').strip())
                part += f'(({arg.name}.has_value()) ? ({base_type_name}*){arg.name}.value().data(): nullptr)'
            else:
                part += f'{arg.name}'
            if i + 1 < len(method.args):
                part += ', '

        part += '); }, '

        # arg list
        for i, arg in enumerate(method.args):
            type_name = arg.type
            base_type_name = type_names_without_decorations(type_name)[0]

            part += f'nb::arg("{arg.name}")'
            if (
                (type_name.find("*") >= 0 or type_name.find("[") >= 0) and  # base_type_name in NUMBER_TYPES and
                (arg.default_value == "NULL")
            ):
                part += '.none()=nb::none()'
            elif arg.default_value is not None:
                part += f'={arg.default_value}'
            part += ', '
        
        # return policy
        part += 'nb::rv_policy::automatic_reference'

        # end
        part += ');'
        # print(part)
        return part

    for n, v in api_dict.items():
        part = gen_api_code(n, v)
        if part is not None:
            code += part + '\n'
    print(len(api_dict))

    # ! handle 'va_list'

    code += '\n}'
    return code


if __name__ == "__main__":
    # Parse cpp source files
    tu = parse_imgui_cpp_sources("imgui_demo.cpp")

    # At first, get all IMGUI_API functions
    imgui_api_names = []
    for node in tu.cursor.get_children():
        lst = -1000
        idx = 0
        last_name = None
        line = ""
        for x in node.get_tokens():
            if x.spelling == "IMGUI_API":
                lst = idx
            if x.spelling == "(" and lst >= 0:
                lst = -1000
                if last_name is not None:
                    imgui_api_names.append(last_name)
                # if last_name == "Text":
                #     print(line, node.spelling)
                last_name = None
                line = ""
            if lst >= 0:
                last_name = x.spelling
                line += x.spelling + ' '
            idx += 1
    assert "Text" in imgui_api_names
    assert "CreateContext" in imgui_api_names

    # Secondly, parse api functions and get return types and arguments
    api_dict = dict()
    for c in tu.cursor.get_children():
        if c.spelling == 'ImGui':
            for k in c.get_children():
                find_api(k, imgui_api_names, api_dict)
        # else:
        #     find_api(c, imgui_api_names, api_dict)
    assert "Text" in api_dict

    # Collect all types used in api
    necessary_types = set()
    for _, method in api_dict.items():
        names = type_names_without_decorations(method.return_type)
        for arg in method.args:
            names += type_names_without_decorations(arg.type)
        for n in names:
            if n in BASIC_TYPES:
                continue
            if n in TYPES_BLACK_LIST:
                continue
            necessary_types.add(n)
    for type_name in necessary_types:
        print(type_name)
    print(len(necessary_types))

    # generate api
    code = generate_api_binding_code(api_dict)
    with open("bind-imgui/api_auto.cpp", "w") as fp:
        print(code, file=fp)
