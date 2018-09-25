from cc_script.CcScriptAst import *
from cc_script.CcScriptPresenter import CcScriptPresenter


def property_set_name(identifier: str):
    return f'set{identifier[0].capitalize()}{identifier[1:]}'


class CcCommonStatement(CcStatement):
    def __init__(self, line_no):
        super().__init__(line_no=line_no)

    def represent_py_output(self, presenter: CcScriptPresenter):
        self.represent_py(presenter)


class CcOutputStatement(CcCommonStatement):
    element_type = 'os'

    def __init__(self, line_no, operator, statement: CcStatement):
        super().__init__(line_no=line_no)
        self.operator = operator
        self.statement = statement

    def __repr__(self):
        return ''

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        if self.statement:
            self.statement = self.statement.resolve_symbol(namespace)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        self.represent_py_output(presenter)

    def represent_py_output(self, presenter: CcScriptPresenter):
        if self.operator == '>':
            presenter.write_line('presenter.shift_indent(True)')
        elif self.operator == '<':
            presenter.write_line('presenter.shift_indent(False)')

        if self.operator == '$':
            if self.statement:
                self.statement.represent_py(presenter)
        else:
            if self.statement:
                self.statement.represent_py_output(presenter)
            else:
                presenter.write_line('presenter.write_line()')

        if self.operator == '>':
            presenter.write_line('presenter.shift_indent(False)')
        elif self.operator == '<':
            presenter.write_line('presenter.shift_indent(True)')

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(f'{self.operator} {{')
        if self.operator == '>':
            presenter.shift_indent(True)
        elif self.operator == '<':
            presenter.shift_indent(False)

        if self.statement:
            self.statement.represent_cc(presenter)

        if self.operator == '>':
            presenter.shift_indent(False)
        elif self.operator == '<':
            presenter.shift_indent(True)
        presenter.write_line(f'}}')


class CcDefinitionStatement(CcCommonStatement):
    element_type = 'ds'

    def __init__(self, line_no, definition):
        super().__init__(line_no=line_no)
        self.definition = definition

    def __repr__(self):
        return ''

    def resolve_symbol(self, namespace: CcNamespace):
        self.definition.resolve_symbol(namespace)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        self.definition.represent_py(presenter)

    def represent_cc(self, presenter: CcScriptPresenter):
        self.definition.represent_cc(presenter)


class CcExprStatement(CcStatement):
    element_type = 'es'

    def __init__(self, line_no, expr_list: list):
        super().__init__(line_no=line_no)
        self.expr_list = expr_list

    def __repr__(self):
        return ''

    def resolve_symbol(self, namespace: CcNamespace):
        for index, expr in enumerate(self.expr_list):
            self.expr_list[index] = expr.resolve_symbol(namespace)
        return self

    def execute(self, engine):
        for expr in self.expr_list:
            expr.execute(engine)

    def represent_py(self, presenter: CcScriptPresenter):
        for expr in self.expr_list:
            presenter.write_line(expr.reference_py)

    def represent_py_output(self, presenter: CcScriptPresenter):
        if len(self.expr_list) == 1 and self.expr_list[0].element_type == 'fc':
            if self.expr_list[0].expr.l_expr.value_type.identifier == 'string':
                presenter.write_line(f'presenter.write_line({self.expr_list[0].reference_py})')
                return

        expr_repr_list = []
        for expr in self.expr_list:
            expr_repr_list.append(f'CcObject.value_of({expr.reference_py})')
        presenter.write_line(f'presenter.write_line({", ".join(expr_repr_list)})')

    def represent_cc(self, presenter: CcScriptPresenter):
        expr_repr_list = []
        for expr in self.expr_list:
            expr_repr_list.append(expr.reference_py)
        presenter.write_line(f'{", ".join(expr_repr_list)};')


class CcAssignStatement(CcStatement):
    element_type = 'as'

    def __init__(self, line_no, l_expr, r_expr):
        super().__init__(line_no=line_no)
        self.l_expr = l_expr
        self.r_expr = r_expr

    def __repr__(self):
        return ''

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True

        self.l_expr = self.l_expr.resolve_symbol(namespace)
        self.r_expr = self.r_expr.resolve_symbol(namespace)

        return self

    def represent_py(self, presenter: CcScriptPresenter):
        presenter.write_line(f'{self.l_expr.reference_py} = {self.r_expr.reference_py}')

    def represent_py_output(self, presenter: CcScriptPresenter):
        if self.l_expr.l_expr.value_type.identifier == 'string':
            var_name = self.l_expr.l_expr.reference_py
            func_name = property_set_name(self.l_expr.indicator)
            argument = f'{{CcObject.value_of({self.r_expr.reference_py})}}'
            presenter.write_line(f'if {self.r_expr.reference_py}:')
            presenter.shift_indent(True)
            presenter.write_line(f'presenter.write_line({var_name}, f\'->{func_name}({argument});\')')
            presenter.shift_indent(False)
        else:
            presenter.write_line(f'{self.l_expr.reference_py} = {self.r_expr.reference_py}')

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(f'{self.l_expr.reference_cc} = {self.r_expr.reference_cc}')


class CcCompoundStatement(CcNamespace, CcStatement):
    element_type = 'cs'

    crlf_for_statement = 0

    def __init__(self, line_no):
        super().__init__(line_no=line_no, identifier='noname')

    def __repr__(self):
        return ''

    def represent_py_output(self, presenter: CcScriptPresenter):
        super().represent_py_output(presenter)

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.shift_indent(False)
        presenter.write_line('{')
        presenter.shift_indent(True)
        super().represent_cc(presenter)
        presenter.shift_indent(False)
        presenter.write_line('}')
        presenter.shift_indent(True)

    def set_entity_storage_type(self, entity: CcDefinition):
        entity.storage_type = StorageType.local


class CcIfStatement(CcStatement):
    element_type = 'is'

    def __init__(self, line_no, condition, if_statement, else_statement=None):
        super().__init__(line_no=line_no)
        self.condition = condition
        self.if_statement = if_statement
        self.else_statement = else_statement

    def __repr__(self):
        return ''

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        self.condition = self.condition.resolve_symbol(namespace)
        self.if_statement.resolve_symbol(namespace)
        if self.else_statement:
            self.else_statement.resolve_symbol(namespace)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        if presenter.follow_if:
            presenter.write_line(f'elif {self.condition.reference_py}:')
        else:
            presenter.write_line(f'if {self.condition.reference_py}:')

        presenter.shift_indent(True)
        self.if_statement.represent_py(presenter)
        presenter.shift_indent(False)

        if self.else_statement:
            if isinstance(self.else_statement, CcIfStatement):
                presenter.follow_if = True
                self.else_statement.represent_py(presenter)
            else:
                presenter.follow_if = False
                presenter.write_line('else:')
                presenter.shift_indent(True)
                self.else_statement.represent_py(presenter)
                presenter.shift_indent(False)

    def represent_py_output(self, presenter: CcScriptPresenter):
        if presenter.follow_if:
            presenter.write_line(f'elif {self.condition.reference_py}:')
        else:
            presenter.write_line(f'if {self.condition.reference_py}:')

        presenter.shift_indent(True)
        self.if_statement.represent_py_output(presenter)
        presenter.shift_indent(False)

        if self.else_statement:
            if isinstance(self.else_statement, CcIfStatement):
                presenter.follow_if = True
                self.else_statement.represent_py_output(presenter)
            else:
                presenter.follow_if = False
                presenter.write_line('else:')
                presenter.shift_indent(True)
                self.else_statement.represent_py_output(presenter)
                presenter.shift_indent(False)

    def represent_cc(self, presenter: CcScriptPresenter):
        if presenter.follow_if:
            presenter.write_line(f'else if ({self.condition.reference_cc})')
        else:
            presenter.write_line(f'if ({self.condition.reference_cc})')

        presenter.shift_indent(True)
        self.if_statement.represent_cc(presenter)
        presenter.shift_indent(False)

        if self.else_statement:
            if isinstance(self.else_statement, CcIfStatement):
                presenter.follow_if = True
                self.else_statement.represent_cc(presenter)
            else:
                presenter.follow_if = False
                presenter.write_line('else')
                presenter.shift_indent(True)
                self.else_statement.represent_cc(presenter)
                presenter.shift_indent(False)


class CcForStatement(CcStatement):
    element_type = 'fs'

    def __init__(self, line_no, var, iterable, statement):
        super().__init__(line_no=line_no)
        self.var = var
        self.iterable = iterable
        self.statement = statement

    def __repr__(self):
        return ''

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        self.iterable = self.iterable.resolve_symbol(namespace)
        self.var.resolve_symbol(namespace)
        self.statement.resolve_symbol(namespace)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        presenter.write_line(f'for {self.var.reference_py} in {self.iterable.reference_py}:')

        presenter.shift_indent(True)
        self.statement.represent_py(presenter)
        presenter.shift_indent(False)

    def represent_py_output(self, presenter: CcScriptPresenter):
        presenter.write_line(f'for {self.var.reference_py} in {self.iterable.reference_py}:')

        presenter.shift_indent(True)
        self.statement.represent_py_output(presenter)
        presenter.shift_indent(False)

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(f'for {self.var.reference_cc} in {self.iterable.reference_cc}')

        presenter.shift_indent(True)
        self.statement.represent_cc(presenter)
        presenter.shift_indent(False)


class CcWhileStatement(CcStatement):
    element_type = 'ws'

    def __init__(self, line_no, condition, statement):
        super().__init__(line_no=line_no)
        self.condition = condition
        self.statement = statement

    def __repr__(self):
        return ''

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        self.condition = self.condition.resolve_symbol(namespace)
        self.statement.resolve_symbol(namespace)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        presenter.write_line(f'while {self.condition.reference_py}:')
        self.condition.represent_py(presenter)

        presenter.shift_indent(True)
        self.statement.represent_py(presenter)
        presenter.shift_indent(False)

    def represent_py_output(self, presenter: CcScriptPresenter):
        presenter.write_line(f'while {self.condition.reference_py}:')
        self.condition.represent_py_output(presenter)

        presenter.shift_indent(True)
        self.statement.represent_py_output(presenter)
        presenter.shift_indent(False)

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(f'while ({self.condition.reference_cc})')
        self.condition.represent_cc(presenter)

        presenter.shift_indent(True)
        self.statement.represent_cc(presenter)
        presenter.shift_indent(False)


class CcDoStatement(CcCommonStatement):
    element_type = 'ds'

    def __init__(self, line_no, condition, statement):
        super().__init__(line_no=line_no)
        self.condition = condition
        self.statement = statement

    def __repr__(self):
        return ''

    def resolve_symbol(self, namespace: CcNamespace):
        if self.is_resolved:
            return self
        self.is_resolved = True
        self.condition = self.condition.resolve_symbol(namespace)
        self.statement.resolve_symbol(namespace)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        raise Exception('do while is not supported yet!')

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line('do ')
        presenter.shift_indent(True)
        self.statement.represent_cc(presenter)
        presenter.shift_indent(False)
        presenter.write_line(f'while ({self.condition.reference_cc});')


class CcLabelStatement(CcCommonStatement):
    element_type = 'ls'

    def __init__(self, line_no, label):
        super().__init__(line_no=line_no)
        self.label = label

    def execute(self, engine):
        pass

    def represent_py(self, presenter: CcScriptPresenter):
        pass

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write(f'{self.get_access_label()}:\n')

    @staticmethod
    def get_access_type(label):
        return StorageType[label]

    def get_access_label(self):
        return self.label.name


class CcGotoStatement(CcCommonStatement):
    element_type = 'gs'

    def __init__(self, line_no, goto):
        super().__init__(line_no=line_no)
        self.goto = goto

    def represent_py(self, presenter: CcScriptPresenter):
        presenter.write_line(self.goto)

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(self.goto + ';')


class CcReturnStatement(CcCommonStatement):
    element_type = 'rs'

    def __init__(self, line_no, expr=None):
        super().__init__(line_no=line_no)
        self.expr = expr

    def resolve_symbol(self, namespace: CcNamespace):
        self.expr = self.expr.resolve_symbol(namespace)
        return self

    def represent_py(self, presenter: CcScriptPresenter):
        if self.expr:
            presenter.write_line(f'return {self.expr.reference_py}')
        else:
            presenter.write_line('return')

    def represent_cc(self, presenter: CcScriptPresenter):
        if self.expr:
            presenter.write_line(f'return {self.expr.reference_cc};')
        else:
            presenter.write_line('return;')


class CcEmptyStatement(CcStatement):
    element_type = 'ep'

    def __init__(self, line_no, expr=None):
        super().__init__(line_no=line_no)

    def represent_py(self, presenter: CcScriptPresenter):
        presenter.write_line('pass')

    def represent_py_output(self, presenter: CcScriptPresenter):
        presenter.write_line('presenter.write_line()')

    def represent_cc(self, presenter: CcScriptPresenter):
        presenter.write_line(';')
