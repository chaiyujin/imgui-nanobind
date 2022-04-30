from typing import List

import os
import humps
import clang.cindex
from clang.cindex import Cursor, CursorKind, Type, TypeKind, AccessSpecifier, TranslationUnit

_DIR_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR_3RD = os.path.abspath(os.path.join(_DIR_SRC, "../third-party"))
DIR_EXPORT = os.path.join(_DIR_SRC, "bind-imgui")


def parse_imgui_cpp_sources(source_file: str = 'imgui_demo.cpp') -> TranslationUnit:
    args = [
        f"-I{_DIR_SRC}",
        f"-I{os.path.join(_DIR_3RD, 'imgui')}",
        # f"-I{os.path.join(_DIR_3RD, 'fmt/include')}",
        # f"-I{os.path.join(_DIR_3RD, 'nanobind/include')}",
        # "-DIMGUI_USER_CONFIG=<imconfig_user.h>",
    ]

    print("Parsing '{}' with args:".format(source_file))
    for arg in args:
        print(" ", arg)

    index = clang.cindex.Index.create()
    tu = index.parse(os.path.join(_DIR_3RD, 'imgui', source_file), args=args)
    return tu


def type_names_without_decorations(name):
    type_name = name.replace("const", "").replace("*", "").replace("&", "").strip()
    if type_name.find("[") >= 0:
        t0 = type_name.split("[")[0].strip()
        return (t0, )
    if type_name.find("<") >= 0:
        t0, t1 = type_name.split("<")
        t1 = t1.replace(">", "")
        t0 = t0.strip()
        t1 = t1.strip()
        return t0, t1
    return (type_name, )


def snake_style(name: str):
    return humps.decamelize(name).lower()


class Argument(object):
    __decor__ = set(['*', '&'])

    def __init__(self, node: Cursor):
        self.name = node.spelling
        self.cursor = node

        # get type_name
        type_name, default_value = '', None
        for x in node.get_tokens():
            if x.spelling == node.spelling:
                continue
            if len(x.spelling.strip()) ==  0:
                continue
            if x.spelling.strip() == '=':
                default_value = ''
                continue
            if default_value is None:
                if (len(type_name) > 0) and (
                    (x.spelling in self.__decor__ and x.spelling == type_name[-1]) or
                    (x.spelling in ['[', ']']) or
                    (type_name[-1] == '[')
                ):
                    type_name += x.spelling
                else:
                    type_name += ' ' + x.spelling
            else:
                default_value += x.spelling
        self.type = type_name.strip()
        self.default_value = default_value.strip() if default_value is not None else None


class Method(object):
    def __init__(self, node: Cursor):
        assert node.kind in [
            CursorKind.FUNCTION_DECL,
            CursorKind.CONSTRUCTOR,
            CursorKind.CXX_METHOD,
        ]
        self.name = node.spelling
        self.return_type = node.type.get_result().spelling
        self.args: List[Argument] = []
        # get args
        for t in node.get_arguments():
            self.args.append(Argument(t))
