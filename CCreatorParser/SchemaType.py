class Type:
    type_none = -1
    type_compound = 0
    type_int = 1
    type_ubyte = 2
    type_float = 3
    type_string = 4
    type_bool = 5
    type_array = 6
    type_variant = 7

    def __init__(self, type, identifier):
        self.type_code = type
        self.identifier = identifier

    def __repr__(self):
        return self.identifier

    def create_instance(self):
        return None


class TypeArray(Type):
    def __init__(self, type):
        super().__init__(Type.type_array, None)
        self.base_type = type

    def __repr__(self):
        return repr(self.base_type) + '[]'


class TypeVariant(Type):
    def __init__(self):
        super().__init__(Type.type_variant, 'variant')


class Property:
    def __init__(self, tag, identifier, type, default_value):
        if tag:
            self.tag = tag
        else:
            self.tag = identifier
        self.identifier = identifier
        self.type = type
        self.default_value = default_value

    def __repr__(self):
        type = self.type if isinstance(self.type, str) else self.type.identifier if self.type else None
        return "{}, {}: {} = {};\n".format(self.tag, self.identifier, type, self.default_value)


class TypeDef(Type):
    def __init__(self, identifier, tag, properties):
        super().__init__(Type.type_compound, identifier)
        self.tag = tag
        self.properties = properties

    def __repr__(self):
        s = self.identifier + ' {\n'
        for prop in self.properties.values():
            s += ' {} '.format(prop)
        s += '}\n'
        # s = '{} [ {} ]'.format(self.identifier, self.properties)
        return s


class Schema:
    def __init__(self):
        self.definition_map = {}
        self.definition_by_tag = {}
        self.unresolved_types = {}
        for definition in (
                ('int', Type.type_int), ('ubyte', Type.type_ubyte), ('float', Type.type_float),
                ('string', Type.type_string), ('bool', Type.type_bool)):
            self.definition_map[definition[0]] = Type(definition[1], definition[0])
            self.definition_map['variant'] = TypeVariant()

    def _resolve_type_name(self, identifier, typedef):
        if identifier in self.unresolved_types:
            for item in self.unresolved_types[identifier]:
                if isinstance(item, Property):
                    item.type = typedef
                elif isinstance(item, TypeArray):
                    item.base_type = typedef
            del self.unresolved_types[identifier]

    def watch_for_typedef(self, identifier, item):
        if not identifier in self.unresolved_types:
            self.unresolved_types[identifier] = []
        self.unresolved_types[identifier] += [item]

    def get_type(self, identifier):
        if identifier not in self.definition_map:
            return None
        return self.definition_map[identifier]

    def append_type(self, typedef):
        identifier = typedef.identifier
        if identifier in self.definition_map:
            raise Exception('name %s is already defined' % identifier)
        self.definition_map[identifier] = typedef

        tag = typedef.tag
        if tag:
            if tag in self.definition_by_tag:
                raise Exception('tag %s is already defined' % tag)
            self.definition_by_tag[tag] = typedef

        self._resolve_type_name(identifier, typedef)
        return typedef

    def __repr__(self):
        return repr(self.definition_map)
