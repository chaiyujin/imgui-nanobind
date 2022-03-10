import os
import clang.cindex
from clang.cindex import CursorKind, Type, TypeKind, AccessSpecifier


# WHITE_LIST = None
WHITE_LIST = ["ImVec2", "ImVec4", "ImRect", "ImGuiIO", "ImGuiStyle"]  # , "ImFontAtlas", "ImFont"]


def find_structs(node, results):
    if node.kind == CursorKind.STRUCT_DECL and node.spelling.startswith("Im"):
        if WHITE_LIST is not None and node.spelling not in WHITE_LIST:
            return

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
    find_structs(c, all_structs)


def gen_struct_code(struct_name, children):
    _tmpl_begin  = '    nb::class_<{0}>(m, "{0}")\n'
    _tmpl_field  = '        .def_readwrite("{1}", &{0}::{1})\n'
    _tmpl_indent = '        '
    _tmpl_end    = '    ;\n\n'

    code = ''
    code += _tmpl_begin.format(struct_name)

    # fields
    for field in children['fields']:
        # simple fields
        if field['type'] == "const char *":
            code += _tmpl_indent
            code += f'.def_property_readonly("{field["name"]}", []({struct_name} const & self) {{ return self.{field["name"]}; }})\n'
        elif field['type'].find("*") >= 0:
            continue
        elif field['type'].find("[") >= 0 and field['type'].find("]") >= 0:
            continue
        else:
            code += _tmpl_field.format(struct_name, field['name'])
    
    # constructors
    for ctor in children['constructors']:
        args_txt = ', '.join(x['type'] for x in ctor['args'])
        # implicit for nanabind
        if args_txt.find("nanobind::") >= 0:
            code += _tmpl_indent + f'.def(nb::init_implicit<{args_txt}>())\n'
        else:
            code += _tmpl_indent + f'.def(nb::init<{args_txt}>())\n'
    
    # methods
    count_method = dict()
    max_name_len = 11
    for method in children['methods']:
        name = method['name']
        if name not in count_method:
            count_method[name] = 0
        count_method[name] += 1
        max_name_len = max(max_name_len, len(name))
    
    def _method_prefix(n):
        return '"' + n + '",' + ' ' * (max_name_len - len(n))

    for method in children['methods']:
        fn_name = method['name']
        args_types = ', '.join(f"{x['type']}" for x in method['args'])
        args_names = ', '.join(f"{x['name']}" for x in method['args'])
        args_list = ', '.join(f"{x['type']} {x['name']}" for x in method['args'])

        args_has_const_char_ptr = False
        for arg in method['args']:
            if arg['cursor'].type.spelling == "const char *":
                args_has_const_char_ptr = True
        if args_has_const_char_ptr:
            continue

        if fn_name == 'operator[]':
            # must overload
            if method['is_const']:
                code += _tmpl_indent
                code += f'.def({_method_prefix("__getitem__")} nb::overload_cast<{args_types}>(&{struct_name}::operator[], nb::const_))\n'
            else:
                val_type = method['return_type']
                code += _tmpl_indent
                code += f'.def({_method_prefix("__getitem__")} nb::overload_cast<{args_types}>(&{struct_name}::operator[]))\n'
                code += _tmpl_indent
                code += f'.def({_method_prefix("__setitem__")} []({struct_name} & self, {args_list}, const {val_type} value) {{ self[{args_names}] = value; }})\n'

        elif fn_name == 'to_string':
            assert len(method['args']) == 0
            assert method['is_const']
            assert method['return_type'] == 'std::string'
            # gen code
            code += _tmpl_indent + f'.def({_method_prefix("__repr__")} &{struct_name}::to_string)\n'

        elif count_method[fn_name] == 1:
            code += _tmpl_indent + f'.def({_method_prefix(fn_name)} &{struct_name}::{fn_name})\n'

        else:
            code += _tmpl_indent
            code += f'.def({_method_prefix(fn_name)} nb::overload_cast<{args_types}>(&{struct_name}::{fn_name}'
            if method['is_const']:
                code += ", nb::const_"
            code += "))\n"

    code += _tmpl_end
    print(code, end='')
    return code


code = """#include "types.hpp"
#include <nanobind/stl/string.h>

namespace nb = nanobind;

void imgui_def_types(nb::module_ & m) {

"""

for n, v in all_structs.items():
    code += gen_struct_code(n, v)

code += "}\n"

with open("bind-imgui/types_auto.cpp", "w") as fp:
    print(code, file=fp)
