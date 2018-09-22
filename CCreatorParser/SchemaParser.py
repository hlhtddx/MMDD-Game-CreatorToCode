from CCreatorParser import SchemaLexer
from CCreatorParser.SchemaType import Schema, TypeDef, Property, Type, TypeArray

import ply.yacc as yacc
import sys

tokens = SchemaLexer.tokens


def p_schema(p):
    """schema : schema typedef
               | typedef"""
    logtag = 'schema'
    schema = p.parser.schema
    if len(p) == 2:
        typedef = p[1]
    elif len(p) == 3:
        typedef = p[2]
    else:
        raise Exception()
    schema.append_type(typedef)
    p[0] = schema
    if len(schema.unresolved_types) > 0:
        raise Exception('There is still unresolved symbols')
    print(logtag, p[0])


def p_typedef(p):
    """typedef : CLASS ID LBRACE properties RBRACE
                | CLASS ID COLON SCONST LBRACE properties RBRACE"""
    logtag = 'typedef'
    schema = p.parser.schema
    identifier = p[2]
    tag = None
    if len(p) == 6:
        properties = p[4]
    else:
        tag = p[4]
        properties = p[6]
    typedef = TypeDef(identifier, tag, properties)
    p[0] = typedef
    print(logtag, p[0])


def p_properties(p):
    """properties : properties property
                | property"""
    logtag = 'properties'
    schema = p.parser.schema
    if len(p) == 2:
        prop = p[1]
        identifier = prop.identifier
        properties = {}
    elif len(p) == 3:
        prop = p[2]
        identifier = prop.identifier
        properties = p[1]
        if identifier in properties:
            raise Exception('Duplicated property %s' % identifier)
    else:
        raise Exception()
    properties[identifier] = prop
    p[0] = properties
    print(logtag, p[0])


def p_property(p):
    """property : ID COLON type SEMI
                | ID COLON type ASSIGN constant SEMI
                | ID COMMA SCONST COLON type SEMI
                | ID COMMA SCONST COLON type ASSIGN constant SEMI"""
    logtag = 'property'
    schema = p.parser.schema

    tag = None
    identifier = p[1]
    default_value = None
    type = None

    if len(p) == 5:
        type = p[3]
    elif len(p) == 7:
        if p[2] == ':':
            type = p[3]
            default_value = p[5]
        else:
            tag = p[3]
            type = p[5]
    elif len(p) == 9:
        tag = p[3]
        type = p[5]
        default_value = p[7]
    prop = Property(tag, identifier, type, default_value)
    if isinstance(type, str):
        schema.watch_for_typedef(type, prop)
    p[0] = prop
    print(logtag, p[0])


def p_array(p):
    """array : type LBRACKET RBRACKET
                | type LBRACKET ICONST RBRACKET
                | type LBRACKET ID RBRACKET"""
    logtag = 'array'
    schema = p.parser.schema
    base_type = p[1]
    p[0] = TypeArray(base_type)
    if isinstance(base_type, str):
        schema.watch_for_typedef(base_type, p[0])
    print(logtag, p[0])


def p_type(p):
    """type : INT
                | UBYTE
                | FLOAT
                | STRING
                | VARIANT
                | ID
                | array"""

    schema = p.parser.schema
    type = p.slice[1]
    if type.type == 'array':
        p[0] = p[1]
    else:
        p[0] = schema.get_type(type.value)
    print('p_class', p[0])


def p_constant(p):
    """constant : ICONST
                    | FCONST
                    | SCONST
                    | TRUE
                    | FALSE"""

    schema = p.parser.schema
    constant = p.slice[1]
    if constant.type == 'ICONST':
        p[0] = int(constant.value)
    elif constant.type == 'FCONST':
        p[0] = float(constant.value)
    elif constant.type == 'SCONST':
        p[0] = str(constant.value)
    elif constant.type == 'TRUE':
        p[0] = True
    elif constant.type == 'FALSE':
        p[0] = False
    else:
        raise Exception('Invalid constant type:' + str(constant))
    print('p_constant', p[0])


def p_error(p):
    print('Error occurs:', p)


if __name__ == '__main__':
    file = open(sys.argv[1], 'r')
    data = file.read()
    schema = Schema()
    parser = yacc.yacc()
    parser.schema = schema
    parser.parse(input=data, lexer=SchemaLexer.lexer)
