import clang.cindex
from clang.cindex import CursorKind


WHITE_LIST = ["ImGuiStyle", "ImDrawChannel"]


def find_structs(node, results):
    if node.kind == CursorKind.STRUCT_DECL and node.spelling.startswith("Im"):
        if WHITE_LIST is not None and node.spelling not in WHITE_LIST:
            return
        if len(list(node.get_children())) == 0:
            return
        print(node.spelling, node.kind, node.brief_comment)

        for x in node.get_tokens():
            # print(x.kind)
            # print("  " + str(x.extent))
            print("  " + str(x.spelling) + "")
        for child in node.get_children():
            print(f"  {child.spelling:30}", "\t\t", child.kind, child.is_default_constructor())
            # for t in child.get_tokens():
            #     print("   ", t.kind, t.spelling)
        # quit(1)


all_structs = dict()
# imgui.h, imgui_internal.h
index = clang.cindex.Index.create()
tu = index.parse('../third-party/imgui/imgui_internal.h')  # imgui.h is included
for c in tu.cursor.get_children():
    find_structs(c, all_structs)
