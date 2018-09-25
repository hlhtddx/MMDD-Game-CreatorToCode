from cc_script import *
from cc_script.CcScriptPresenter import CcScriptPresenter


class CcException(Exception):
    def __init__(self, tag, msg, obj=None):
        super().__init__(msg, obj)
        self.tag = tag


class CcNamedException(CcException):
    def __init__(self, identifier, obj=None):
        super().__init__(tag=ErrorTag.name, msg=identifier + ' is not defined', obj=obj)


class CcTypeException(CcException):
    def __init__(self, data_type, msg, obj=None):
        super().__init__(tag=ErrorTag.type, msg=f'type {data_type}: {msg}', obj=obj)


class CcValueException(CcException):
    def __init__(self, data_type, msg, obj=None):
        super().__init__(tag=ErrorTag.type, msg=f'type {data_type}: {msg}', obj=obj)


class CcElement:
    element_type = 'el'

    def __init__(self, line_no):
        self.is_resolved = False
        self.line_no = line_no

    def __repr__(self):
        return f'({self.line_no}) {self.element_type}'

    def resolve_symbol(self, namespace):
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        raise Exception('Unsupported behaviour')

    def represent_py_output(self, presenter: CcScriptPresenter):
        raise Exception('Unsupported behaviour')

    def represent_cc(self, presenter: CcScriptPresenter):
        raise Exception('Unsupported behaviour')


class CcEntity(CcElement):
    element_type = 'en'

    def __init__(self, line_no, identifier, tag, storage_type):
        super().__init__(line_no)
        self.storage_type = storage_type
        self.identifier = identifier
        self.tag = tag if tag else self.identifier

    def __repr__(self):
        return f'({self.line_no}) {self.element_type}: {self.identifier}'

    def represent_py(self, presenter: CcScriptPresenter):
        return self.identifier

    def represent_py_output(self, presenter: CcScriptPresenter):
        return self.identifier

    def represent_cc(self, presenter: CcScriptPresenter):
        return f'{self.element_type} {self.identifier}'

    @property
    def value_type(self):
        raise Exception('Undefined value type!')

    @property
    def reference_py(self):
        return self.identifier

    @property
    def declare_py(self):
        return self.identifier

    @property
    def reference_cc(self):
        return self.identifier

    @property
    def declare_cc(self):
        return f'{self.element_type} {self.identifier}'


class CcStatement(CcElement):
    element_type = 'st'

    def __init__(self, line_no):
        super().__init__(line_no)

    def __repr__(self):
        return f'({self.line_no}) {self.element_type}'

    @property
    def reference_cc(self):
        return None

    @property
    def declare_cc(self):
        return None

    def resolve_symbol(self, namespace):
        return self

    def execute(self, engine):
        pass

    def represent_py(self, presenter: CcScriptPresenter):
        pass

    def represent_py_output(self, presenter: CcScriptPresenter):
        pass

    def represent_cc(self, presenter: CcScriptPresenter):
        pass


class CcNamespace(CcEntity):
    element_type = 'ns'
    crlf_for_statement = 1

    def __init__(self, line_no, identifier, tag=None, storage_type=StorageType.auto):
        super().__init__(line_no=line_no, identifier=identifier, tag=tag, storage_type=storage_type)
        self.parent = None
        self._entities = {}
        self._entities_by_tag = {}
        self._statements = []
        self._default_storage_type = StorageType.external
        self._all_children_resolved = False

    def __repr__(self):
        entity_count = len(self._entities)
        stmt_count = len(self._statements)
        return f'({self.line_no}) {self.element_type}: {self.identifier} with {entity_count} entities, {stmt_count} statements'

    def resolve_symbol(self, namespace):
        if self._all_children_resolved:
            return self
        self._all_children_resolved = True
        for statement in self._statements:
            assert (isinstance(statement, CcStatement))
            statement.resolve_symbol(self)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        for statement in self._statements:
            assert (isinstance(statement, CcStatement))
            statement.represent_py(presenter)
            presenter.write_crlf(self.__class__.__name__, self.crlf_for_statement)

    def represent_py_output(self, presenter: CcScriptPresenter):
        for statement in self._statements:
            assert (isinstance(statement, CcStatement))
            statement.represent_py_output(presenter)
            presenter.write_crlf(self.__class__.__name__, self.crlf_for_statement)

    def represent_cc(self, presenter):
        for statement in self._statements:
            assert (isinstance(statement, CcStatement))
            statement.represent_cc(presenter)

    def execute(self, engine):
        for statement in self._statements:
            assert (isinstance(statement, CcStatement))
            statement.execute(engine)

    def set_entity_storage_type(self, entity: CcEntity):
        entity.storage_type = StorageType.module

    def has_entity(self, identifier):
        if identifier in self._entities:
            return True
        elif self.parent:
            return self.parent.has_entity(identifier)
        else:
            return False

    def get_entity(self, identifier):
        if identifier in self._entities:
            return self._entities[identifier]
        elif self.parent:
            return self.parent.get_entity(identifier)
        else:
            return None

    def get_entity_by_tag(self, tag):
        if tag not in self._entities_by_tag:
            return None
        return self._entities_by_tag[tag]

    def append_tag(self, entity):
        if entity is None:
            return
        assert (isinstance(entity, CcEntity))

        tag = entity.tag
        if tag is None:
            return
        if tag in self._entities_by_tag:
            raise Exception(f'tag \"{tag}\" is already defined')
        self._entities_by_tag[tag] = entity

    def append_entity(self, entity, storage_type=StorageType.auto):
        if entity is None:
            return
        assert (isinstance(entity, CcEntity))
        identifier = entity.identifier
        if identifier in self._entities:
            raise Exception(f'name \"{identifier}\" is already defined')

        self._entities[identifier] = entity
        self.append_tag(entity)

        if storage_type == StorageType.auto:
            self.set_entity_storage_type(entity)
        else:
            entity.storage_type = storage_type

    def append_statement(self, statement):
        if statement is None:
            return
        assert (isinstance(statement, CcStatement))
        self._statements.append(statement)


class CcDefinition(CcNamespace):
    element_type = 'd'
    crlf_for_statement = 0

    def __init__(self, line_no, identifier, tag=None, storage_type=StorageType.external):
        super().__init__(line_no=line_no, identifier=identifier, tag=tag, storage_type=storage_type)


class CcModule(CcDefinition):
    element_type = 'mo'
    crlf_for_statement = 1

    def __init__(self, name='script'):
        super().__init__(line_no=0, identifier=name)
        self.current_namespace = self

    def represent_py(self, presenter: CcScriptPresenter):
        presenter.write_line('from cc_model.CcModelBase import CcObject')
        presenter.write_crlf(self.__class__.__name__, self.crlf_for_statement * 2)
        super().represent_py(presenter)
        presenter.write_line('CcObject.generate_tag_map(globals())')

    def set_statement_storage_type(self, storage_type):
        self.current_namespace._default_storage_type = storage_type

    def create_entity(self, definition, storage_type=StorageType.auto):
        assert (isinstance(definition, CcEntity))
        self.current_namespace.append_entity(definition, storage_type)

    def create_statement(self, statement):
        assert (isinstance(statement, CcStatement))
        self.current_namespace.append_statement(statement)

    def push_namespace(self, namespace: CcNamespace):
        namespace.parent = self.current_namespace
        self.current_namespace = namespace

    def pop_namespace(self):
        self.current_namespace = self.current_namespace.parent
