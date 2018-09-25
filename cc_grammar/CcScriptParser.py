import ply.yacc as yacc
import sys
import logging

from cc_script.CcScriptStmt import *
from cc_script.CcScriptDefinition import *
from cc_script.CcScriptExpr import *
from cc_script.CcScriptPresenter import CcScriptPresenter
from cc_grammar.CcScriptLexer import tokens, lexer
script = CcModule()

for identifier, built_in in built_in_types_map.items():
    script._entities[identifier] = built_in


def p_script(p):
    """script : statements"""
    script.resolve_symbol(script)
    p[0] = script


def p_statements(p):
    """statements :
        | statements statement"""
    p[0] = script.current_namespace
    if len(p) == 3:
        if p[2] is not None:
            assert (isinstance(p[2], CcStatement))
            script.create_statement(p[2])


def p_statement(p):
    """statement : output_statement
        | assign_statement
        | compound_statement
        | if_statement
        | for_statement
        | while_statement
        | do_statement
        | expression_statement
        | definition_statement
        | label_statement
        | goto_statement
        | return_statement
        | empty_statement"""
    statement = p[1]
    assert (statement is None or isinstance(statement, CcStatement))
    p[0] = p[1]


def p_output_statement(p):
    """output_statement : output_operator statement
        | output_operator SEMI"""
    statement = None if p[2] == ';' else p[2]
    p[0] = CcOutputStatement(line_no=p.lexer.lineno, operator=p[1], statement=statement)


def p_output_operator(p):
    """output_operator : ASSIGN
        | LT
        | GT
        | DOLLAR"""
    p[0] = p[1]


def p_assign_statement(p):
    """assign_statement : postfix_expression ASSIGN expression SEMI"""
    p[0] = CcAssignStatement(line_no=p.lexer.lineno, l_expr=p[1], r_expr=p[3])


def p_compound_statement(p):
    """compound_statement : compound_statement_init statements RBRACE"""
    p[0] = p[1]
    script.pop_namespace()


def p_compound_statement_init(p):
    """compound_statement_init : LBRACE"""
    p[0] = CcCompoundStatement(line_no=p.lexer.lineno)
    script.push_namespace(p[0])


def p_if_statement(p):
    """if_statement : if_only_statement
        | if_else_statement"""
    p[0] = p[1]


def p_if_only_statement(p):
    """if_only_statement : IF LPAREN expression RPAREN statement"""
    p[0] = CcIfStatement(line_no=p.lexer.lineno, condition=p[3], if_statement=p[5])


def p_if_else_statement(p):
    """if_else_statement : IF LPAREN expression RPAREN statement ELSE statement"""
    p[0] = CcIfStatement(line_no=p.lexer.lineno, condition=p[3], if_statement=p[5], else_statement=p[7])


def p_for_statement(p):
    """for_statement : FOR ID IN expression statement"""
    var = CcVariableDefinition(line_no=p.lexer.lineno, identifier=p[2], value_type=CcUnboundName(line_no=p.lexer.lineno, identifier='@', expr=p[4]))
    body = p[5]

    # Ensure the body is Compound statement, for individual namespace
    if not isinstance(p[5], CcCompoundStatement):
        body = CcCompoundStatement(line_no=p.lexer.lineno)
        body.append_statement(statement=p[5])

    script.push_namespace(body)
    p[0] = CcForStatement(line_no=p.lexer.lineno, var=var, iterable=p[4], statement=body)
    script.create_entity(var)
    script.pop_namespace()


def p_while_statement(p):
    """while_statement : WHILE LPAREN expression RPAREN statement"""
    p[0] = CcWhileStatement(line_no=p.lexer.lineno, condition=p[3], statement=p[5])


def p_do_statement(p):
    """do_statement : DO statement WHILE LPAREN expression RPAREN"""
    p[0] = CcDoStatement(line_no=p.lexer.lineno, condition=p[6], statement=p[2])


def p_definition_statement(p):
    """definition_statement : definition"""
    p[0] = CcDefinitionStatement(line_no=p.lexer.lineno, definition=p[1])


def p_expression_statement(p):
    """expression_statement : expression_list SEMI"""
    p[0] = CcExprStatement(line_no=p.lexer.lineno, expr_list=p[1])


def p_label_statement(p):
    """label_statement : INTERNAL COLON
        | EXTERNAL COLON"""
    access_type = StorageType[p[1]]
    script.set_statement_storage_type(storage_type=access_type)
    # p[0] = CcLabelStatement(line_no=p.lexer.lineno, label=access_type)
    p[0] = None


def p_goto_statement(p):
    """goto_statement : BREAK SEMI
        | CONTINUE SEMI"""
    p[0] = CcGotoStatement(line_no=p.lexer.lineno, goto=p[1])


def p_return_statement(p):
    """return_statement : RETURN SEMI
        | RETURN expression SEMI"""
    if len(p) == 3:
        p[0] = CcReturnStatement(line_no=p.lexer.lineno)
    else:
        p[0] = CcReturnStatement(line_no=p.lexer.lineno, expr=p[2])


def p_empty_statement(p):
    """empty_statement : SEMI"""
    p[0] = CcEmptyStatement(line_no=p.lexer.lineno)


def p_primary_expression(p):
    """primary_expression : ID
        | THIS
        | SUPER
        | constant"""
    expr = p.slice[1]
    if expr.type == 'ID':
        p[0] = CcNameReference(priority=1, l_expr=CcNopExpression(priority=1), indicator=p[1])
    elif expr.type == 'THIS':
        p[0] = CcThisReference(priority=1)
    elif expr.type == 'SUPER':
        p[0] = CcSuperReference(priority=1)
    else:
        p[0] = p[1]


def p_postfix_expression(p):
    """postfix_expression : primary_expression
        | postfix_expression LBRACKET expression RBRACKET
        | postfix_expression PERIOD ID
        | postfix_expression LPAREN argument_list RPAREN
        | parentheses_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        operator = p.slice[2]
        if operator.type == 'LBRACKET':
            p[0] = CcArrayExpression(priority=2, l_expr=p[1], r_expr=p[3])
        elif operator.type == 'PERIOD':
            p[0] = CcNameReference(priority=2, l_expr=p[1], indicator=p[3])
        elif operator.type == 'LPAREN':
            p[0] = CcFunctionCall(priority=2, expr=p[1], argument_list=p[3])
        else:
            raise Exception('invalid postfix expression')


def p_parentheses_expression(p):
    """parentheses_expression : LPAREN logical_or_expression RPAREN"""
    p[0] = p[2]


def p_unary_expression(p):
    """unary_expression : postfix_expression
        | LNOT unary_expression
        | MINUS unary_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CcUnaryExpression(priority=3, operator=p[1], expr=p[2])


def p_multiplicative_expression(p):
    """multiplicative_expression : unary_expression
        | multiplicative_expression TIMES unary_expression
        | multiplicative_expression DIVIDE unary_expression
        | multiplicative_expression MOD unary_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CcBinaryExpression(priority=4, operator=p[2], l_expr=p[1], r_expr=p[3])


def p_additive_expression(p):
    """additive_expression : multiplicative_expression
        | additive_expression PLUS multiplicative_expression
        | additive_expression MINUS multiplicative_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CcBinaryExpression(priority=5, operator=p[2], l_expr=p[1], r_expr=p[3])


def p_relational_expression(p):
    """relational_expression : additive_expression
        | relational_expression LT additive_expression
        | relational_expression GT additive_expression
        | relational_expression LE  additive_expression
        | relational_expression GE  additive_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CcBinaryExpression(priority=6, operator=p[2], l_expr=p[1], r_expr=p[3])


def p_equality_expression(p):
    """equality_expression : relational_expression
        | equality_expression EQ relational_expression
        | equality_expression NE relational_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CcBinaryExpression(priority=7, operator=p[2], l_expr=p[1], r_expr=p[3])


def p_logical_and_expression(p):
    """logical_and_expression : equality_expression
        | logical_and_expression LAND equality_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CcBinaryExpression(priority=8, operator=p[2], l_expr=p[1], r_expr=p[3])


def p_logical_or_expression(p):
    """logical_or_expression : logical_and_expression
        | logical_or_expression LOR logical_and_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CcBinaryExpression(priority=9, operator=p[2], l_expr=p[1], r_expr=p[3])


def p_expression(p):
    """expression : logical_or_expression"""
    p[0] = p[1]


def p_expression_list(p):
    """expression_list : expression
        | expression_list COMMA expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])


def p_definition(p):
    """definition : class_definition
        | function
        | variable SEMI
        | type_alias SEMI"""
    p[0] = p[1]
    if isinstance(p[1], CcClassDefinition) or isinstance(p[1], CcFunction):
        return
    script.create_entity(p[0])


def p_class_definition(p):
    """class_definition : class_definition_init statements RBRACE"""
    script.pop_namespace()
    p[0] = p[1]


def p_class_definition_init(p):
    """class_definition_init : class_extends
        | class_no_extends"""
    p[0] = p[1]
    script.create_entity(p[0])
    script.push_namespace(p[0])


def p_class_extends(p):
    """class_extends : CLASS id_name EXTENDS type LBRACE"""
    id_name = p[2]
    super_class = p[4]
    if super_class is None:
        raise CcNamedException(identifier=id_name.identifier, obj=p[2])
    p[0] = CcClassDefinition(line_no=p.lexer.lineno, identifier=id_name.identifier, tag=id_name.tag, super_class=super_class)


def p_class_no_extends(p):
    """class_no_extends : CLASS id_name LBRACE"""
    id_name = p[2]
    p[0] = CcClassDefinition(line_no=p.lexer.lineno, identifier=id_name.identifier, tag=id_name.tag)


def p_function(p):
    """function : function_init statements RBRACE"""
    script.pop_namespace()
    p[0] = p[1]


def p_function_init(p):
    """function_init : type id_name LPAREN argument_declaration RPAREN LBRACE"""
    id_name = p[2]
    if id_name.identifier == '__ctor__':
        assert isinstance(script.current_namespace, CcClassDefinition)
        p[0] = CcConstructor(line_no=p.lexer.lineno, class_type=script.current_namespace, argument_list=tuple(p[4]))
    elif id_name.identifier.startswith('write_'):
        p[0] = CcPresenterFunction(line_no=p.lexer.lineno, identifier=id_name.identifier, argument_list=tuple(p[4]))
    else:
        p[0] = CcFunction(line_no=p.lexer.lineno, identifier=id_name.identifier, return_type=p[1], argument_list=tuple(p[4]))
    script.create_entity(p[0])
    script.push_namespace(p[0])


def p_argument_declaration(p):
    """argument_declaration :
        | variable
        | argument_declaration COMMA variable"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1], ]
    elif len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        raise Exception('Invalid argument_declaration')


def p_argument_list(p):
    """argument_list :
        | expression
        | argument_list COMMA expression"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1], ]
    elif len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        raise Exception('Invalid argument_list')


def p_variable(p):
    """variable : variable_no_value
        | variable_with_value"""
    p[0] = p[1]


def p_variable_no_value(p):
    """variable_no_value : type id_name"""
    id_name = p[2]
    p[0] = CcVariableDefinition(line_no=p.lexer.lineno, identifier=id_name.identifier, value_type=p[1], tag=id_name.tag)


def p_variable_with_value(p):
    """variable_with_value : type id_name ASSIGN expression"""
    id_name = p[2]
    p[0] = CcVariableDefinition(line_no=p.lexer.lineno, identifier=id_name.identifier, value_type=p[1], tag=id_name.tag,
                                default_value=p[4])


def p_type_alias(p):
    """type_alias : TYPEDEF type id_name"""
    id_name = p[3]
    p[0] = CcTypeAlias(line_no=p.lexer.lineno, identifier=id_name.identifier, base_type=p[2], tag=id_name.tag)


def p_id_name(p):
    """id_name : ID
        | ID COLON string_constant"""
    if len(p) == 2:
        p[0] = CcIdName(identifier=p[1])
    else:
        p[0] = CcIdName(identifier=p[1], tag=p[3])


def p_type(p):
    """type : INT
        | UBYTE
        | FLOAT
        | STRING
        | VARIANT
        | BOOL
        | VOID
        | ID
        | array"""

    value = p.slice[1]
    if value.type == 'array':
        p[0] = p[1]
    else:
        p[0] = CcUnboundName(line_no=p.lexer.lineno, identifier=value.value)


def p_array(p):
    """array : type AT"""
    base_type = p[1]
    p[0] = CcTypeArray(line_no=p.lexer.lineno, base_type=base_type)


def p_constant(p):
    """constant : ICONST
        | FCONST
        | string_constant
        | NULL
        | TRUE
        | FALSE"""
    constant = p.slice[1]
    if constant.type == 'ICONST':
        p[0] = CcInstanceValue(priority=1, value_type=type_int, value=int(constant.value))
    elif constant.type == 'FCONST':
        p[0] = CcInstanceValue(priority=1, value_type=type_float, value=float(constant.value))
    elif constant.type == 'string_constant':
        p[0] = CcInstanceValue(priority=1, value_type=type_string, value=constant.value)
    elif constant.type == 'NULL':
        p[0] = CcInstanceValue(priority=1, value_type=type_null, value=None)
    elif constant.type == 'TRUE':
        p[0] = CcInstanceValue(priority=1, value_type=type_bool, value=True)
    elif constant.type == 'FALSE':
        p[0] = CcInstanceValue(priority=1, value_type=type_bool, value=False)
    else:
        raise Exception('Invalid constant type:' + str(constant))


def p_string_constant(p):
    """string_constant : SCONST
        | string_constant SCONST"""
    if len(p) == 2:
        p[0] = parse_string_constants(p[1])
    else:
        p[0] = p[1] + parse_string_constants(p[2])


def p_error(p):
    print('Error occurs:', p)


def generate_model_python(model_script):
    # model_file = sys.stdout
    model_file = open('cc_model/CcModel.py', 'w')
    model_presenter = CcScriptPresenter(model_file, '    ')
    model_script.represent_py(presenter=model_presenter)
    model_file.close()


def parse(script_path, debug=False, tracking=False):
    script_file = open(script_path, 'r')
    data = script_file.read()
    global script
    parser = yacc.yacc()
    parser.script = script
    p = parser.parse(input=data, lexer=lexer, debug=debug, tracking=tracking)
    if p:
        generate_model_python(script)
        return parser.script
    return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if parse(script_path=sys.argv[1], debug=True, tracking=False):
        file = open('Data/CcScript.cpp', 'w')
        presenter = CcScriptPresenter(file)
        script.represent_cc(presenter=presenter)
        file.close()
        del file
        del presenter
