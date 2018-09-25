from cc_script.CcScriptDefinition import *
from cc_script.CcScriptAst import CcNamespace
from cc_script import *


class CcExpression:
    element_type = 'ex'

    def __init__(self, priority):
        self.priority = priority
        self.is_resolved = False

    def __repr__(self):
        if self.is_resolved:
            return self.reference_cc
        else:
            return 'not resolved'

    def resolve_symbol(self, namespace: CcNamespace):
        return self

    @property
    def value_type(self):
        raise CcTypeException(data_type=None, msg=get_func_name(), obj=self)

    @property
    def reference_cc(self):
        raise CcValueException(data_type=None, msg=get_func_name(), obj=self)

    @property
    def reference_py(self):
        raise CcValueException(data_type=None, msg=get_func_name(), obj=self)

    @property
    def value_string_py(self):
        return self.reference_py

    @staticmethod
    def calculated_type(value_type1, value_type2):
        assert value_type1 in (int, float)
        assert value_type2 in (int, float)
        if value_type1 == float or value_type2 == float:
            return float
        return int

    @property
    def is_constant(self):
        return False

    @property
    def is_numeric_constant(self):
        return False

    @property
    def is_bool_constant(self):
        return False

    @property
    def is_string_constant(self):
        return False

    def evaluate(self):
        return self


class CcInstanceValue(CcExpression):
    element_type = 'i'

    def __init__(self, priority, value_type=None, value=None):
        super().__init__(priority=priority)
        if value_type is None:
            if value is None:
                raise CcValueException(data_type=None, msg=get_func_name(), obj=self)
            if isinstance(value, int):
                value_type = built_in_types_map['int']
            elif isinstance(value, float):
                value_type = built_in_types_map['float']
            elif isinstance(value, str):
                value_type = built_in_types_map['string']
            elif isinstance(value, bool):
                value_type = built_in_types_map['bool']
            else:
                raise CcTypeException(data_type=None, msg=get_func_name(), obj=self)
        self._value_type = value_type
        if value is None:
            value = value_type.default_value
        self.value = value

    def __repr__(self):
        return f'{{"type": "{self._value_type.identifier}", "value": {self.value}}}'

    def __str__(self):
        return str(self.value)

    @property
    def value_type(self):
        return self._value_type

    @property
    def reference_cc(self):
        return str(self.value)

    @property
    def reference_py(self):
        if self.value_type == type_string:
            return f'\"{str(self.value)}\"'
        return str(self.value)

    @property
    def value_string_py(self):
        if self.value_type == type_bool:
            return 'true' if self.value else 'false'
        return self.reference_py

    @property
    def is_constant(self):
        return True

    @property
    def is_numeric_constant(self):
        return self._value_type in (type_int, type_float)

    @property
    def is_bool_constant(self):
        return self._value_type in (type_bool,)

    @property
    def is_string_constant(self):
        return self._value_type in (type_string,)


class CcNopExpression(CcExpression):
    element_type = 'ne'

    def __init__(self, priority):
        super().__init__(priority=priority)

    def __bool__(self):
        return False

    @property
    def value_type(self):
        return type_void

    @property
    def reference_cc(self):
        return ''

    @property
    def reference_py(self):
        return ''

    @property
    def is_constant(self):
        return True


class CcBaseExpression(CcExpression):
    element_type = 'be'

    def __init__(self, priority, operator, l_expr: CcExpression, r_expr: CcExpression):
        super().__init__(priority=priority)
        self.operator = operator
        self.l_expr = l_expr
        self.r_expr = r_expr

    def resolve_symbol(self, namespace: CcNamespace):
        self.l_expr = self.l_expr.resolve_symbol(namespace)
        self.r_expr = self.r_expr.resolve_symbol(namespace)
        if self.l_expr.is_constant and self.r_expr.is_constant:
            return self.evaluate()
        return self

    @property
    def operator_for_python(self):
        return self.operator

    @property
    def reference_py(self):
        ret_value = []

        if self.l_expr:
            if self.l_expr.priority > self.priority:
                ret_value += ['(', self.l_expr.reference_py, ')']
            else:
                ret_value.append(self.l_expr.reference_py)

        ret_value += [' ', self.operator_for_python, ' ']

        if self.r_expr.priority >= self.priority:
            ret_value += ['(', self.r_expr.reference_py, ')']
        else:
            ret_value.append(self.r_expr.reference_py)

        return ''.join(ret_value)

    @property
    def reference_cc(self):
        ret_value = []

        if self.l_expr:
            if self.l_expr.priority > self.priority:
                ret_value += ['(', self.l_expr.reference_cc, ')']
            else:
                ret_value.append(self.l_expr.reference_cc)

        ret_value += [' ', self.operator, ' ']

        if self.r_expr.priority >= self.priority:
            ret_value += ['(', self.r_expr.reference_cc, ')']
        else:
            ret_value.append(self.r_expr.reference_cc)

        return ''.join(ret_value)


class CcUnaryExpression(CcBaseExpression):
    element_type = 'ue'

    def __init__(self, priority, operator, expr: CcExpression):
        super().__init__(priority=priority, operator=operator, l_expr=CcNopExpression(priority=priority), r_expr=expr)

    def __repr__(self):
        return self.reference_cc

    @property
    def value_type(self):
        if self.operator == '!':
            return bool
        if self.operator == '-':
            return self.r_expr.value_type

    def evaluate(self):
        assert self.r_expr.is_constant
        if self.operator == '-':
            if self.r_expr.is_numeric_constant:
                self.r_expr.value = -self.r_expr.value
                return self.r_expr
            else:
                raise CcValueException(data_type=None, msg=get_func_name(), obj=self)
        elif self.operator == '!':
            if self.r_expr.value_type == bool:
                self.r_expr.value = not self.r_expr.value
                return self.r_expr
            else:
                raise CcValueException(data_type=None, msg=get_func_name(), obj=self)
        raise CcValueException(data_type=None, msg=get_func_name(), obj=self)

    @property
    def operator_for_python(self):
        if self.operator == '!':
            return 'not'
        return self.operator

    @property
    def reference_cc(self):
        ret_value = [self.operator, ' ']
        if self.r_expr.priority > self.priority:
            ret_value += ['(', self.r_expr.reference_cc, ')']
        else:
            ret_value.append(self.r_expr.reference_cc)
        return ''.join(ret_value)

    @property
    def reference_py(self):
        ret_value = [self.operator_for_python, ' ']
        if self.r_expr.priority > self.priority:
            ret_value += ['(', self.r_expr.reference_py, ')']
        else:
            ret_value.append(self.r_expr.reference_py)
        return ''.join(ret_value)


class CcArrayExpression(CcBaseExpression):
    element_type = 'ae'

    def __init__(self, priority, l_expr: CcExpression, r_expr: CcExpression):
        super().__init__(priority=priority, operator='@', l_expr=l_expr, r_expr=r_expr)

    def __repr__(self):
        return ''

    @property
    def value_type(self):
        assert isinstance(self.l_expr, CcNameReference)
        return self.l_expr.value_type.base_type

    def evaluate(self):
        param2 = self.l_expr.evaluate()
        param1 = self.r_expr.evaluate()
        result = param1.get_item(param2)
        return result

    @property
    def reference_cc(self):
        return self.l_expr.reference_cc + '[' + self.r_expr.reference_cc + ']'

    @property
    def reference_py(self):
        assert isinstance(self.l_expr, CcNameReference)
        assert isinstance(self.l_expr.target_var.value_type, CcTypeArray)
        return self.l_expr.reference_py + '[' + self.r_expr.reference_py + ']'


class CcNameReference(CcExpression):
    element_type = 'nr'

    def __init__(self, priority, l_expr: CcExpression, indicator: str):
        super().__init__(priority=priority)
        self.l_expr = l_expr
        self.indicator = indicator
        self.target_var = None

    def __repr__(self):
        return self.indicator

    @property
    def value_type(self):
        return self.target_var.value_type

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True

        if self.l_expr:
            self.l_expr = self.l_expr.resolve_symbol(namespace)
            self.l_expr.value_type.resolve_symbol(namespace)
            if self.l_expr.value_type == type_string:
                target_var = namespace.get_entity(self.indicator)
            else:
                target_var = self.l_expr.value_type.get_entity(self.indicator)
        else:
            target_var = namespace.get_entity(self.indicator)
        if target_var is None:
            raise CcNamedException(identifier=self.indicator, obj=(namespace, self.l_expr))
        # TODO target_var is var, function, class, variant

        self.target_var = target_var.resolve_symbol(namespace)
        return self

    def evaluate(self):
        param1 = self.l_expr.evaluate()
        result = param1.get_fields(self.r_expr)
        return result

    @property
    def reference_cc(self):
        if self.is_resolved:
            storage_string = f'/* {self.target_var.storage_type.name} */'
            prefix = f'{self.l_expr.reference_cc}.' if self.l_expr else ''
            return f'{storage_string} {prefix}{self.indicator}'
        else:
            return f'{self.l_expr}.{self.indicator}'

    @property
    def reference_py(self):
        prefix = (self.l_expr.reference_py + '.') if self.l_expr else 'self.'
        storage_type = self.target_var.storage_type
        if isinstance(self.target_var, CcBuiltinFunction):
            return f'{self.indicator}'

        if storage_type == StorageType.internal:
            return f'{prefix}{self.indicator}'

        if storage_type == StorageType.external:
            return f'{prefix}{self.indicator}'

        if storage_type == StorageType.module:
            if isinstance(self.target_var, CcClassDefinition):
                return f'{self.indicator}'
            else:
                return f'CcObject.{self.indicator}'

        return f'{self.indicator}'


class CcThisReference(CcNameReference):
    element_type = 'tr'

    def __init__(self, priority):
        super().__init__(priority=priority, l_expr=CcNopExpression(priority=priority), indicator='this')

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True

        class_type = CcClassDefinition.find_class_namespace(namespace)
        if class_type is None:
            raise CcNamedException(identifier='this', obj=self)

        self.target_var = class_type
        return self

    @property
    def reference_cc(self):
        return 'this'

    @property
    def reference_py(self):
        return 'self'


class CcSuperReference(CcNameReference):
    element_type = 'sr'

    def __init__(self, priority):
        super().__init__(priority=priority, l_expr=CcNopExpression(priority=priority), indicator='super')

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True

        class_type = CcClassDefinition.find_class_namespace(namespace)
        if class_type is None:
            raise CcNamedException(identifier='super', obj=self)
        if class_type.super_class is None:
            raise CcTypeException(data_type=class_type, msg=get_func_name(), obj=self)

        self.target_var = class_type.super_class
        return self

    @property
    def reference_cc(self):
        return 'super'

    @property
    def reference_py(self):
        return 'super()'


class CcBinaryExpression(CcBaseExpression):
    element_type = 'be'

    arith_operators = ('+', '-', '*', '/', '%')
    relation_operators = ('>', '>=', '<', '<=', '==', '!=')
    logical_operators = ('&&', '||')

    def __init__(self, priority, operator, l_expr: CcExpression, r_expr: CcExpression, left_precedence=False):
        super().__init__(priority=priority, operator=operator, l_expr=l_expr, r_expr=r_expr)
        self.operator = operator
        self.left_precedence = left_precedence
        self.l_expr = l_expr
        self.r_expr = r_expr

    def __repr__(self):
        return ''

    @property
    def value_type(self):
        if self.operator in self.arith_operators:
            return self.calculated_type(self.l_expr.value_type, self.r_expr.value_type)
        if self.operator in self.relation_operators or self.operator in self.logical_operators:
            return bool
        raise Exception('Invalid binary operator')

    def _arithmetic_op(self):
        assert (self.l_expr.is_numeric_constant and self.r_expr.is_numeric_constant) or (self.l_expr.is_string_constant and self.r_expr.is_string_constant)
        l_value = self.l_expr.value
        r_value = self.r_expr.value
        result_value = None

        if self.operator == '+':
            result_value = l_value + r_value
        elif self.operator == '-':
            result_value = l_value - r_value
        elif self.operator == '*':
            result_value = l_value * r_value
        elif self.operator == '/':
            result_value = l_value / r_value
        elif self.operator == '%':
            result_value = l_value % r_value
        return CcInstanceValue(priority=self.l_expr.priority, value=result_value)

    def _relation_op(self):
        assert self.l_expr.is_constant and self.r_expr.is_constant
        l_value = self.l_expr.value
        r_value = self.r_expr.value
        result_value = None

        if self.operator == '>':
            result_value = l_value > r_value
        elif self.operator == '>=':
            result_value = l_value >= r_value
        elif self.operator == '<':
            result_value = l_value < r_value
        elif self.operator == '<=':
            result_value = l_value <= r_value
        elif self.operator == '==':
            result_value = l_value == r_value
        elif self.operator == '!=':
            result_value = l_value != r_value
        return CcInstanceValue(priority=self.l_expr.priority, value=result_value)

    def _logical_op(self):
        assert self.l_expr.is_bool_constant and self.r_expr.is_bool_constant
        l_value = self.l_expr.value
        r_value = self.r_expr.value
        result_value = None

        if self.operator == '&&':
            result_value = l_value and r_value
        elif self.operator == '||':
            result_value = l_value or r_value
        return CcInstanceValue(priority=self.l_expr.priority, value=result_value)

    def evaluate(self):
        assert self.l_expr.is_constant and self.r_expr.is_constant
        if self.operator in self.arith_operators:
            return self._arithmetic_op()
        elif self.operator in self.relation_operators:
            return self._relation_op()
        elif self.operator in self.logical_operators:
            return self._logical_op()
        else:
            raise CcValueException(data_type=self.l_expr.value_type, msg='Invalid binary operator', obj=self)

    def execute(self, engine):
        if self.left_precedence:
            param1 = self.r_expr.execute(engine)
            param2 = self.l_expr.execute(engine)
        else:
            param2 = self.l_expr.execute(engine)
            param1 = self.r_expr.execute(engine)

        assert (param1.type == param2.type)
        value1 = param1.value
        value2 = param2.value
        result_value = None
        if self.operator == '+':
            result_value = value1 + value2
        elif self.operator == '-':
            result_value = value1 - value2
        elif self.operator == '*':
            result_value = value1 * value2
        elif self.operator == '/':
            result_value = value1 / value2
        elif self.operator == '%':
            result_value = value1 % value2
        elif self.operator == '>':
            result_value = value1 > value2
        elif self.operator == '>=':
            result_value = value1 >= value2
        elif self.operator == '<':
            result_value = value1 % value2
        elif self.operator == '<=':
            result_value = value1 > value2
        elif self.operator == '==':
            result_value = value1 >= value2
        elif self.operator == '!=':
            result_value = value1 % value2
        elif self.operator == '||':
            result_value = value1 > value2
        elif self.operator == '&&':
            result_value = value1 >= value2
        else:
            raise Exception('Invalid binary operator')
        result = CcInstanceValue(priority=0, value_type=param1.type, value=result_value)
        engine.push(result)

    @property
    def operator_for_python(self):
        if self.operator == '||':
            return 'or'
        elif self.operator == '&&':
            return 'and'
        return self.operator


class CcFunctionCall(CcExpression):
    element_type = 'fc'

    def __init__(self, priority, expr: CcExpression, argument_list: list):
        super().__init__(priority=priority)
        self.expr = expr
        self.argument_list = argument_list

    @property
    def value_type(self):
        return self.expr.value_type

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        self.expr = self.expr.resolve_symbol(namespace)
        if isinstance(self.expr.target_var, CcPresenterFunction):
            self.argument_list.insert(0, CcNameReference(priority=0, l_expr=CcNopExpression(priority=0), indicator='presenter'))
        for index, argument in enumerate(self.argument_list):
            self.argument_list[index] = argument.resolve_symbol(namespace)
        return self

    def evaluate(self, engine):
        instance, entry = engine.find_symbol(None, self.expr)
        for argument in self.argument_list:
            arg_value = argument.evaluate(engine)
            engine.push(arg_value)
        engine.push(instance)
        entry.execute(engine)

    @property
    def reference_cc(self):
        arg_str = []
        for argument in self.argument_list:
            arg_str.append(argument.reference_cc)
        return f'{self.expr.reference_cc}({", ".join(arg_str)})'

    @property
    def reference_py(self):
        assert isinstance(self.expr, CcNameReference)
        arg_str_list = []
        for argument in self.argument_list:
            arg_str_list.append(argument.reference_py)
        if isinstance(self.expr.target_var, CcBuiltinFunction):
            if self.expr.target_var.storage_type == StorageType.internal:
                arg_str_list.insert(0, self.expr.l_expr.reference_py)
            return f'{self.expr.target_var.implementation}({", ".join(arg_str_list)})'
        if self.expr.l_expr.value_type == type_string:
            function_ref = self.expr.l_expr
            assert isinstance(function_ref, CcNameReference)
            assert len(arg_str_list) == 1
            var_name = function_ref.reference_py
            func_name = self.expr.indicator
            argument = f'{{CcObject.value_of({arg_str_list[0]})}}'
            return f'{var_name}, f\'->{func_name}({argument});\''
        return f'{self.expr.reference_py}({", ".join(arg_str_list)})'
