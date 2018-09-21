class Type:
    type_none = -1
    type_compound = 0
    type_int = 1
    type_float = 2
    type_string = 3
    type_bool = 4
    type_array = 5

    def __init__(self, type, name):
        self.type_code = type
        self.name = name

    def __repr__(self):
        return self.name

class TypeArray(Type):
    def __init__(self, type):
        super().__init__(Type.type_array, None)
        self.base_type = type

    def __repr__(self):
        return self.base_type + '[]'


class TypeCompound(Type):
    def __init__(self, name, properties):
        super().__init__(Type.type_compound, name)
        self.properties = properties


class Property:
    def __init__(self, tag, id, type, default_value):
        self.tag = tag
        self.id = id
        self.type = type
        self.default_value = default_value


class TypeDef:
    def __init__(self, id, properties):
        self.id = id
        self.properties = properties


class Schema:
    def __init__(self):
        self.type_map = {}
        for type in (
        ('int', Type.type_int), ('float', Type.type_float), ('string', Type.type_string), ('bool', Type.type_bool)):
            self.type_map[type[0]] = Type(type[0], type[1])
        self.unresolved_types = {}

    def _resolve_type_name(self, id, typedef):
        if id in self.unresolved_types:
            for item in self.unresolved_types[id]:
                if item is Property:
                    item.type = typedef
                elif item is TypeArray:
                    item.base_type = typedef
            del self.unresolved_types[id]

    def watch_for_typedef(self, id, item):
        if not id in self.unresolved_types:
            self.unresolved_types[id] = []
        self.unresolved_types[id] += [item]

    def get_type(self, id):
        if not id in self.type_map:
            return None
        return self.type_map[id]

    def append_type(self, typedef):
        """
        :type typedef: TypeDef
        """
        id = typedef.id
        if id in self.type_map:
            raise Exception('name %s is already defined' % typedef.id)
        self.type_map[id] = typedef
        self._resolve_type_name(id, typedef)
        return typedef

    def __repr__(self):
        return repr(self.type_map)