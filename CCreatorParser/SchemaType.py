class Type:
    type_none = -1
    type_compound = 0
    type_int = 1
    type_ubyte = 2
    type_float = 3
    type_string = 4
    type_bool = 5
    type_array = 6

    def __init__(self, type, id):
        self.type_code = type
        self.id = id

    def __repr__(self):
        return self.id

class TypeArray(Type):
    def __init__(self, type):
        super().__init__(Type.type_array, None)
        self.base_type = type

    def __repr__(self):
        return repr(self.base_type) + '[]'


class Property:
    def __init__(self, tag, id, type, default_value):
        self.tag = tag
        self.id = id
        self.type = type
        self.default_value = default_value

    def __repr__(self):
        return "{}, {}: {} = {};\n".format(self.tag, self.id, self.type, self.default_value)


class TypeDef(Type):
    def __init__(self, id, properties):
        super().__init__(Type.type_compound, id)
        self.properties = properties

    def __repr__(self):
        s = self.id + ' {\n'
        for prop in self.properties.values():
            s += ' {} '.format(prop)
        s += '}\n'
        # s = '{} [ {} ]'.format(self.id, self.properties)
        return s

class Schema:
    def __init__(self):
        self.type_map = {}
        for type in (
        ('int', Type.type_int), ('ubyte', Type.type_ubyte), ('float', Type.type_float), ('string', Type.type_string), ('bool', Type.type_bool)):
            self.type_map[type[0]] = Type(type[1], type[0])
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