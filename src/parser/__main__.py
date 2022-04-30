import os
from . import utils
from .enums import find_all_enums, generate_code_enums


def dump_enums():
    # It's easy to handle enums
    dict_enum = find_all_enums()
    code_enum = generate_code_enums(dict_enum)
    with open(os.path.join(utils.DIR_EXPORT, "enums_auto.cpp"), "w") as fp:
        print(code_enum, file=fp)


def dump_structs():
    # Some essential structs, like 'ImVec2', are manually written
    # We automatically handle some other commonly used strcuts.
    pass


if __name__ == "__main__":
    dump_enums()
