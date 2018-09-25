from cc_script.CcScriptAst import *
import sys


class CcVariableInstance:
    def __init__(self, identifier, value_type=None, value=None):
        self.identifier = identifier
        if value_type is None:
            raise Exception('Unknown type for value')
        self._value_type = value_type
        if value is None:
            self.value = self._value_type.default_value
        else:
            self.value = value
        self.variables = {}

    def represent(self, file):
        file.write(repr(self.value))

    def add_variable_with_instance(self, instance):
        self.variables[instance.identifier] = instance

    def add_variable_with_value(self, identifier, value_type=None, value=None):
        new_var = CcVariableInstance(identifier=identifier, value_type=value_type, value=value)
        self.variables[identifier] = new_var

    def get_value(self, identifier):
        return self._value_type.get_value(self, identifier=identifier)

    def __repr__(self):
        return f'{{"type": "{self._value_type.identifier}", "value": {self.value}}}'

    @property
    def reference_cc(self):
        return repr(self.value)


class CcScriptEngine(CcVariableInstance):
    def __init__(self, script):
        super().__init__(script=script, identifier='myself', value_type=script.get_entity('__process'), value=self)
        self.stack = []

    def init_engine(self, **args):
        self.stack.clear()
        self.variables.clear()
        self.add_variable_with_instance(instance=self)

        __file_type = self.script.get_entity('__file')
        self.add_variable_with_value(identifier='stdout_1', value_type=__file_type, value=sys.stdout)
        self.add_variable_with_value(identifier='stdout_2', value_type=__file_type, value=sys.stderr)

        for identifier, value in args.items():
            self.add_variable_with_value(identifier=identifier, value=value)

    def execute(self, entry, *args):
        self.init_engine()
        for arg in args:
            self.stack.append(CcInstanceValue(value=arg))
        definition = self.script.get_entity(entry)
        if isinstance(definition, CcFunction):
            definition.execute(self)
        elif isinstance(definition, CcClassDefinition):
            pass

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        return self.stack.pop()
