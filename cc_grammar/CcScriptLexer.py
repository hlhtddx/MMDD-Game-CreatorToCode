import ply.lex as lex

# Reserved words
reserved = (
    'CLASS', 'TYPEDEF', 'EXTENDS', 'INTERNAL', 'EXTERNAL',
    'VOID', 'BOOL', 'UBYTE', 'INT', 'FLOAT', 'STRING', 'VARIANT',
    'NULL', 'TRUE', 'FALSE', 'THIS', 'SUPER',
    'IF', 'ELSE', 'FOR', 'IN', 'WHILE', 'DO', 'BREAK', 'CONTINUE', 'RETURN',
)

tokens = reserved + (
    # Literals (identifier, integer constant, float constant, string constant)
    'ID', 'ICONST', 'FCONST', 'SCONST',

    # Operators (+, -, *, /, %, ||, &&, !, <, <=, >, >=, ==, !=)
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'LOR', 'LAND', 'LNOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',

    # Delimeters ( ) [ ] { } , . ; :
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'PERIOD', 'SEMI', 'COLON', 'DOLLAR',

    # Special Operators @, =
    'AT', 'ASSIGN',
)

# Completely ignored characters
t_ignore = ' \t\x0c'


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


# Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_LOR = r'\|\|'
t_LAND = r'&&'
t_LNOT = r'!'
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='

# Delimeters
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_PERIOD = r'\.'
t_SEMI = r';'
t_DOLLAR = r'\$'
t_COLON = r':'

# Special
t_AT = r'@'
t_ASSIGN = r'='

# Identifiers and reserved words

reserved_map = {}
for r in reserved:
    reserved_map[r.lower()] = r


def t_ID(t):
    r'[A-Za-z_][\w_]*'
    t.type = reserved_map.get(t.value, "ID")
    return t


# Integer literal
t_ICONST = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

# Floating literal
t_FCONST = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

# String literal
t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

t_ignore_line_comment = r'//[^\\\n]*\n'


# Comments
def t_comment(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')


def t_error(t):
    print("Illegal literal %s" % repr(t.value[0]))
    t.lexer.skip(1)


lexer = lex.lex(debug=False)
