import os
import clang.cindex
from clang.cindex import CursorKind, Type, TypeKind, AccessSpecifier


WHITE_LIST = ["ImVec2", "ImVec4"]


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
                method = dict(name=fn, args=[], return_type=child.type.get_result().spelling)
                for t in child.get_arguments():
                    method['args'].append(dict(type=t.type.spelling, name=t.spelling))
                results[struct_name]['methods'].append(method)


all_structs = dict()
imgui_config = '<imconfig_user.h>'
args = [
    f"-DIMGUI_USER_CONFIG={imgui_config}",
    f"-I{os.path.abspath(os.path.dirname(__file__))}"
]

index = clang.cindex.Index.create()
tu = index.parse('../third-party/imgui/imgui_demo.cpp', args=args)
for c in tu.cursor.get_children():
    find_structs(c, all_structs)


def gen_struct_code(struct_name, children):
    _tmpl_begin  = '    nb::class_<{0}>(m, "{0}")\n'
    _tmpl_field  = '        .def_readwrite("{1}", &{0}::{1})\n'
    _tmpl_ctor   = '        .def(nb::init<{}>())\n'
    _tmpl_lambda = '        .def("{1}", []({0} const & self, {2}) {{ {3} }})\n'
    _tmpl_end    = '    ;\n\n'

    code = ''
    code += _tmpl_begin.format(struct_name)

    # fields
    for field in children['fields']:
        # simple fields
        code += _tmpl_field.format(struct_name, field['name'])
    
    # constructors
    for ctor in children['constructors']:
        code += _tmpl_ctor.format(', '.join(x['type'] for x in ctor['args']))
    
    # methods
    for method in children['methods']:
        if method['name'] == 'operator[]':
            fn_txt = ''
            if len(method['args']) == 1:
                fn_txt += f"return self[{method['args'][0]['name']}];"
            args_txt = ', '.join(f"{x['type']} {x['name']}" for x in method['args'])
            code += _tmpl_lambda.format(struct_name, '__getitem__', args_txt, fn_txt)
        else:
            raise NotImplementedError()

    code += _tmpl_end
    print(code, end='')
    return code


for n, v in all_structs.items():
    gen_struct_code(n, v)
