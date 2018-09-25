from cc_script.CcScriptAst import *
from cc_script.CcScriptStmt import CcDefinitionStatement


class CcIdName:
    def __init__(self, identifier, tag=None):
        self.identifier = identifier
        self.tag = tag

    def __repr__(self):
        return f'{self.identifier}:{self.tag}'


class CcType(CcDefinition):
    element_type = 't'

    def __init__(self, line_no, identifier, tag=None, storage_type=StorageType.auto):
        super().__init__(line_no=line_no, identifier=identifier, tag=tag, storage_type=storage_type)

    @property
    def value_type(self):
        return self

    @property
    def declare_cc(self):
        return self.reference_cc

    @property
    def reference_cc(self):
        return self.identifier

    def represent_py(self, presenter: CcScriptPresenter):
        self.represent_cc(presenter)

    def represent_cc(self, presenter: CcScriptPresenter):
        raise CcTypeException(data_type=self, msg=get_func_name(), obj=self)

    @property
    def default_value(self):
        raise CcTypeException(data_type=self, msg=get_func_name(), obj=self)

    def accept_operator(self, operator, operand_type):
        return False


class CcUnboundName(CcEntity):
    element_type = 'un'

    def __init__(self, line_no, identifier, expr=None):
        super().__init__(line_no=line_no, identifier=identifier, tag=None, storage_type=StorageType.auto)
        if identifier in ('@', '#'):
            assert expr
        self.expr = expr

    def resolve_symbol(self, namespace: CcNamespace):
        if self.expr:
            self.expr = self.expr.resolve_symbol(namespace)

        if self.identifier == '#':  # return type of self.expr
            return self.expr.value_type
        if self.identifier == '@':  # return base type of self.expr(array)
            return self.expr.value_type.base_type
        return namespace.get_entity(identifier=self.identifier)

    @property
    def declare_cc(self):
        raise CcTypeException(data_type=self, msg=get_func_name(), obj=self)

    @property
    def reference_cc(self):
        raise CcTypeException(data_type=self, msg=get_func_name(), obj=self)

    @property
    def default_value(self):
        raise CcTypeException(data_type=self, msg=get_func_name(), obj=self)


class CcBuiltinType(CcType):
    element_type = 'bt'

    def __init__(self, identifier, native_type):
        super().__init__(line_no=0, identifier=identifier, storage_type=StorageType.module)
        self.native_type = native_type

    @property
    def default_value(self):
        return self.native_type()

    @property
    def reference_py(self):
        return self.native_type.__name__

    @classmethod
    def accept_operator_numeric(cls, operator, operand_type):
        return False

    @classmethod
    def accept_operator_string(cls, operator, operand_type):
        return False

    @classmethod
    def accept_operator_bool(cls, operator, operand_type):
        return False

    def accept_operator(self, operator, operand_type):
        if self.identifier in ('int', 'float'):
            return self.accept_operator_numeric(operator, operand_type)
        if self.identifier == 'string':
            return self.accept_operator_string(operator, operand_type)
        if self.identifier == 'bool':
            return self.accept_operator_bool(operator, operand_type)
        return False


class CcTypeVariant(CcType):
    def __init__(self):
        super().__init__(line_no=0, identifier='variant')


class CcVariableDefinition(CcDefinition):
    element_type = 'va'

    def __init__(self, line_no, identifier, value_type, tag=None, default_value=None):
        super().__init__(line_no=line_no, identifier=identifier, tag=tag)
        self._value_type = value_type
        self.default_value = default_value

    def __repr__(self):
        param = [self.element_type, ':', repr(self._value_type), self.identifier]
        if self.default_value:
            param += ['=', repr(self.default_value)]
        if self.tag:
            param += [f'// tag={self.tag}']
        return ' '.join(param)

    @property
    def value_type(self):
        return self._value_type

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        _value_type = self._value_type.resolve_symbol(namespace)
        assert _value_type
        self._value_type = _value_type

        if self.default_value:
            self.default_value = self.default_value.resolve_symbol(namespace)

        return self

    @property
    def declare_cc(self):
        str_list = [self.value_type.reference_cc, self.identifier]
        if self.default_value:
            str_list += ['=', self.default_value.reference_cc]
        return ' '.join(str_list)

    def represent_py(self, presenter: CcScriptPresenter):
        str_list = []
        if self.storage_type == StorageType.external:
            str_list.append(f'self.{self.identifier}')
        elif self.storage_type == StorageType.internal:
            str_list.append(f'self.{self.identifier}')
        elif self.storage_type == StorageType.module:
            str_list.append(f'CcObject.{self.identifier}')
        else:
            str_list.append(self.identifier)

        str_list.append('=')

        if self.storage_type == StorageType.external:
            if isinstance(self.value_type, CcBuiltinType):
                str_list.append(f'self.get_object_by_id({self.value_type.reference_py}, \'{self.tag}\')')
            elif isinstance(self.value_type, CcClassDefinition):
                str_list.append(f'self.get_object_by_id({self.value_type.reference_py}, \'{self.tag}\')')
            elif isinstance(self.value_type, CcTypeArray):
                str_list.append(f'self.get_array_by_id({self.value_type.base_type.reference_py}, \'{self.tag}\')')
            elif isinstance(self.value_type, CcTypeVariant):
                str_list.append(f'self.get_array_by_id({"Item"}, \'{self.tag}\')')
            else:
                raise CcTypeException(data_type=self.value_type, msg=get_func_name(), obj=self)

        elif self.default_value:
            str_list.append(self.default_value.reference_py)
        else:
            str_list.append(repr(self._value_type.default_value))
        presenter.write_line(' '.join(str_list))

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(self.declare_cc + ';')


class CcFunction(CcDefinition):
    element_type = 'f'

    def __init__(self, line_no, identifier, return_type, argument_list: tuple = (), fixed_argument_list: tuple = ()):
        super().__init__(line_no=line_no, identifier=identifier)
        self._value_type = return_type
        self.fixed_argument_list = fixed_argument_list[:]
        self.argument_list = argument_list[:]
        for argument in self.fixed_argument_list + self.argument_list:
            self.append_entity(argument, StorageType.argument)

    def __repr__(self):
        arg_str = []
        for argument in self.argument_list:
            arg_str.append(repr(argument))
        ret_type_str = repr(self.value_type)
        return f'{ret_type_str} {self.identifier}({", ".join(arg_str)})'

    def append_argument(self, argument: CcVariableDefinition):
        self.argument_list.append(argument)
        self.append_entity(entity=argument, storage_type=StorageType.argument)

    @property
    def value_type(self):
        return self._value_type

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        self._value_type = self._value_type.resolve_symbol(namespace)
        assert self._value_type

        if self.argument_list:
            new_argument_list = []
            for argument in self.argument_list:
                new_argument_list.append(argument.resolve_symbol(namespace))
            self.argument_list = tuple(new_argument_list)
        CcNamespace.resolve_symbol(self, self)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        arg_str_list = ['self']
        for argument in self.fixed_argument_list + self.argument_list:
            arg_str_list.append(argument.identifier)
        argument_string = ', '.join(arg_str_list)
        presenter.write_line(f'def {self.reference_py}({argument_string}):')

        presenter.shift_indent(True)
        super().represent_py(presenter)
        presenter.shift_indent(False)

    def represent_cc(self, presenter: CcScriptPresenter):
        arg_str_list = []
        for argument in self.fixed_argument_list + self.argument_list:
            arg_str_list.append(argument.declare_cc)
        argument_string = ', '.join(arg_str_list)
        presenter.write_line(f'{self._value_type.reference_cc} {self.reference_cc}({argument_string}) {{')

        presenter.shift_indent(True)
        super().represent_cc(presenter)
        presenter.shift_indent(False)

        presenter.write_line('}')

    def set_entity_storage_type(self, entity: CcDefinition):
        entity.storage_type = StorageType.local


class CcBuiltinFunction(CcFunction):
    element_type = 'bf'

    def __init__(self, applied_to: CcType, identifier, return_type, argument_list, implementation):
        super().__init__(line_no=0, identifier=identifier, return_type=return_type, argument_list=argument_list)
        self.applied_to = applied_to
        self.implementation = implementation

    def represent_py(self, presenter: CcScriptPresenter):
        pass

    def represent_py_output(self, presenter: CcScriptPresenter):
        pass

    def represent_cc(self, presenter: CcScriptPresenter):
        pass


class CcConstructor(CcFunction):
    element_type = 'ct'

    function_name = '@ctor'

    def __init__(self, line_no, class_type, argument_list: tuple = ()):
        var_data = CcVariableDefinition(line_no=line_no, identifier='data', value_type=type_variant)
        var_parent = CcVariableDefinition(line_no=line_no, identifier='parent_item', value_type=type_variant)
        super().__init__(line_no=line_no, identifier=self.function_name, return_type=class_type,
                         argument_list=argument_list, fixed_argument_list=(var_data, var_parent))

        assert isinstance(class_type, CcClassDefinition)
        self.class_type = class_type

    @property
    def reference_py(self):
        return '__init__'

    def represent_py(self, presenter: CcScriptPresenter):
        arg_str_list = ['self']
        for argument in self.fixed_argument_list + self.argument_list:
            arg_str_list.append(argument.identifier)
        presenter.write_line(f'def {self.reference_py}({", ".join(arg_str_list)}):')

        presenter.shift_indent(True)
        presenter.write_line(f'super().{self.reference_py}(data, parent_item)')
        # member variables
        for statement in self.class_type._statements:
            if not isinstance(statement, CcDefinitionStatement):
                continue
            if not isinstance(statement.definition, CcVariableDefinition):
                continue
            statement.represent_py(presenter)

        super(CcDefinition, self).represent_py(presenter)
        presenter.shift_indent(False)


class CcPresenterFunction(CcFunction):
    element_type = 'pf'

    def __init__(self, line_no, identifier, argument_list: tuple):
        var_presenter = CcVariableDefinition(line_no=line_no, identifier='presenter', value_type=type_presenter)
        super().__init__(line_no=line_no, identifier=identifier, return_type=type_void, argument_list=argument_list,
                         fixed_argument_list=(var_presenter,))


class CcClassDefinition(CcType):
    element_type = 'c'
    crlf_for_statement = 1

    def __init__(self, line_no, identifier, super_class=None, tag=None):
        CcType.__init__(self, line_no=line_no, identifier=identifier, tag=tag)
        self.super_class = super_class
        self.constructor = None

    def __repr__(self):
        param = ['class', self.identifier, '//', f'tag={self.tag}']
        return ' '.join(param)

    def create_constructor(self):
        if CcConstructor.function_name in self._entities:
            self.constructor = self._entities[CcConstructor.function_name]
        else:
            self.constructor = CcConstructor(line_no=self.line_no, class_type=self,
                                             argument_list=self.super_class.constructor.argument_list[:])
        assert self.constructor

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        if self.super_class:
            self.super_class = self.super_class.resolve_symbol(namespace)
            assert self.super_class
        else:
            self.super_class = type_object
        self.create_constructor()
        this_name = CcVariableDefinition(line_no=self.line_no, identifier='this', value_type=self)
        self.append_entity(this_name, StorageType.internal)
        CcNamespace.resolve_symbol(self, self)
        return self

    def has_entity(self, identifier):
        if identifier in self._entities:
            return True
        elif self.super_class and self.super_class.has_entity(identifier):
            return True
        elif self.parent:
            return self.parent.has_entity(identifier)
        else:
            return False

    def get_entity(self, identifier):
        if identifier in self._entities:
            return self._entities[identifier]
        elif self.super_class and self.super_class.has_entity(identifier):
            return self.super_class.get_entity(identifier)
        elif self.parent:
            return self.parent.get_entity(identifier)
        return None

    @property
    def default_value(self):
        return None

    @staticmethod
    def find_class_namespace(namespace: CcNamespace):
        while namespace.parent:
            if isinstance(namespace, CcClassDefinition):
                return namespace
            namespace = namespace.parent
        return None

    def represent_py(self, presenter: CcScriptPresenter):
        presenter.write_line(f'class {self.identifier}({self.super_class.identifier}):')
        presenter.shift_indent(True)

        if self.tag != self.identifier:
            presenter.write_line(f'"""tag={self.tag}"""')

        self.constructor.represent_py(presenter)
        presenter.write_crlf(self.__class__.__name__, self.crlf_for_statement)

        for statement in self._statements:
            if isinstance(statement, CcDefinitionStatement):
                if isinstance(statement.definition, CcVariableDefinition):
                    continue
                if isinstance(statement.definition, CcConstructor):
                    continue
            statement.represent_py(presenter)
            presenter.write_crlf(self.__class__.__name__, self.crlf_for_statement)

        presenter.shift_indent(False)

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(f'class {self.identifier} extends {self.super_class.identifier} {{')
        presenter.shift_indent(True)

        internal_definitions = []
        # internal member variables
        for statement in self._statements:
            statement.represent_cc(presenter)

        presenter.shift_indent(False)
        presenter.write_line('}')

    def set_entity_storage_type(self, entity: CcDefinition):
        if isinstance(entity, CcVariableDefinition):
            entity.storage_type = self._default_storage_type
        else:
            entity.storage_type = StorageType.internal


class CcTypeArray(CcType):
    element_type = 'a'

    def __init__(self, line_no, base_type):
        identifier = base_type.identifier
        super().__init__(line_no=line_no, identifier=identifier + '[]')
        self.base_type = base_type
        append_arg = CcVariableDefinition(line_no=line_no, identifier='data', value_type=type_variant)
        self.append_entity(CcBuiltinFunction(applied_to=self, implementation='CcObject.append', identifier='append',
                                             return_type=type_void, argument_list=(append_arg,)),
                           storage_type=StorageType.internal)
        self.append_entity(CcBuiltinFunction(applied_to=self, implementation='CcObject.length', identifier='length',
                                             return_type=type_void, argument_list=()),
                           storage_type=StorageType.internal)

    def __repr__(self):
        return repr(self.base_type) + '[]'

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        self.base_type = self.base_type.resolve_symbol(namespace)
        assert self.base_type
        self.storage_type = self.base_type.storage_type
        return self

    @property
    def reference_cc(self):
        return self.base_type.reference_cc + '[]'

    @property
    def default_value(self):
        return []


class CcTypeAlias(CcType):
    element_type = 'ta'

    def __init__(self, line_no, identifier, base_type: CcType, tag=None):
        super().__init__(line_no=line_no, identifier=identifier, tag=tag)
        self.base_type = base_type
        while isinstance(self.base_type, CcTypeAlias):
            self.base_type = self.base_type.base_type

    @property
    def value_type(self):
        return self.base_type.value_type

    def __repr__(self):
        return f'typedef {repr(self.base_type)} {self.identifier}'

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        self.base_type = self.base_type.resolve_symbol(namespace)
        assert self.base_type
        return self.base_type

    @property
    def declare_cc(self):
        return f'typedef {self.base_type.reference_cc} {self.identifier}'

    def represent_py(self, presenter: CcScriptPresenter):
        presenter.write_line(f'{self.identifier} = {repr(self.base_type)}')

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(f'typedef {self.base_type.reference_cc} {self.identifier}')

    def verify_value(self, value):
        if value is None:
            return
        assert self.base_type.verify_value(value)


type_void = CcBuiltinType('void', type(None))
type_null = CcBuiltinType('null', type(None))
type_process = CcBuiltinType('__process', type(None))
type_int = CcBuiltinType('int', int)
type_ubyte = CcBuiltinType('ubyte', int)
type_float = CcBuiltinType('float', float)
type_string = CcBuiltinType('string', str)
type_bool = CcBuiltinType('bool', bool)
type_variant = CcTypeVariant()
type_presenter = CcBuiltinType('CcPresenter', CcScriptPresenter)

type_object = CcClassDefinition(line_no=0, identifier='CcObject')
type_object.append_entity(CcVariableDefinition(line_no=0, identifier='value_data', value_type=type_variant),
                          StorageType.external)
type_object_ctor = CcConstructor(line_no=0, class_type=type_object)
type_object.append_entity(type_object_ctor)
type_object.constructor = type_object_ctor


def __append_builtin_functions():
    _qname_arg = CcVariableDefinition(line_no=0, identifier='name', value_type=type_string)
    type_object.append_entity(
        CcBuiltinFunction(applied_to=type_void, identifier='qualified_name', implementation='CcObject.qualified_name',
                          return_type=type_string, argument_list=(_qname_arg,), ), storage_type=StorageType.module)

    _obj = CcVariableDefinition(line_no=0, identifier='obj', value_type=type_variant)
    type_object.append_entity(
        CcBuiltinFunction(applied_to=type_void, identifier='make_string', implementation='CcObject.make_string',
                          return_type=type_string, argument_list=(_obj,), ), storage_type=StorageType.module)

    _uuid = CcVariableDefinition(line_no=0, identifier='uuid', value_type=type_variant)
    type_object.append_entity(
        CcBuiltinFunction(applied_to=type_void, identifier='find_resource_by_uuid', implementation='CcObject.find_resource_by_uuid',
                          return_type=type_string, argument_list=(_uuid,), ), storage_type=StorageType.module)

    _meta = CcVariableDefinition(line_no=0, identifier='meta', value_type=type_variant)
    type_object.append_entity(
        CcBuiltinFunction(applied_to=type_void, identifier='get_sub_metas', implementation='CcObject.get_sub_metas',
                          return_type=type_variant, argument_list=(_meta,), ), storage_type=StorageType.module)


built_in_types = (
    type_void, type_null, type_process, type_int, type_ubyte, type_float, type_string, type_bool,
    type_variant, type_object, type_presenter)

built_in_types_map = {}

for bt in built_in_types:
    built_in_types_map[bt.identifier] = bt
__append_builtin_functions()
