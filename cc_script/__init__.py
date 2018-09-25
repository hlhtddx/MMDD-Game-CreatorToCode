from enum import IntEnum
import sys

class StorageType(IntEnum):
    auto = 0
    external = 1
    internal = 2
    module = 3
    local = 4
    argument = 5


class ErrorTag(IntEnum):
    generic = 0
    name = 1
    type = 2
    module = 3
    local = 4
    argument = 5


def parse_string_constants(s):
    return s[1:-1]


def get_func_name():
    return sys._getframe(1).f_code.co_name
