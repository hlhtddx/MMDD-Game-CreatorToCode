%{
%}

%type script

%%

script: statements
;

statements:
            | statements statement
;

statement: output_statement
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
;

assign_statement: postfix_expression ASSIGN expression SEMI
;

output_statement: output_operator statement
        | output_operator SEMI
;

output_operator: ASSIGN
        | LT
        | GT
;

compound_statement: compound_statement_init statements RBRACE
;

compound_statement_init: LBRACE
;

if_statement: if_statement : if_only_statement
        | if_else_statement
;

if_only_statement: IF LPAREN expression RPAREN statement
;

if_else_statement: IF LPAREN expression RPAREN statement ELSE statement
;

for_statement: for ID in expression statements
;

while_statement: WHILE LPAREN expression RPAREN statement
;

do_statement: DO statement WHILE LPAREN expression RPAREN
;

definition_statement: definition
;

expression_statement: expression_list SEMI
;

label_statement: INTERNAL COLON
        | EXTERNAL COLON
;

goto_statement: BREAK SEMI
        | CONTINUE SEMI
;

return_statement: RETURN SEMI
        | RETURN expression SEMI
;

primary_expression: ID
        | THIS
        | SUPER
        | constant
;

postfix_expression: primary_expression
        | postfix_expression LBRACKET expression RBRACKET
        | postfix_expression PERIOD ID
        | postfix_expression LPAREN argument_list RPAREN
        | parentheses_expression
;

parentheses_expression: LPAREN logical_or_expression RPAREN
;

unary_expression: postfix_expression
        | LNOT unary_expression
        | MINUS unary_expression
;

multiplicative_expression: unary_expression
        | multiplicative_expression TIMES unary_expression
        | multiplicative_expression DIVIDE unary_expression
        | multiplicative_expression MOD unary_expression
;

additive_expression: multiplicative_expression
        | additive_expression '+' multiplicative_expression
        | additive_expression '-' multiplicative_expression
;

relational_expression:
        additive_expression
        | relational_expression LT additive_expression
        | relational_expression GT additive_expression
        | relational_expression LE  additive_expression
        | relational_expression GE  additive_expression
;

equality_expression: relational_expression
        | equality_expression EQ relational_expression
        | equality_expression NE relational_expression
;

logical_and_expression:
        equality_expression
        | logical_and_expression LAND equality_expression
        ;

logical_or_expression:
        logical_and_expression
        | logical_or_expression LOR logical_and_expression
        ;

expression: logical_or_expression
;

expression_list: expression
        | expression_list COMMA expression
;

definition: class_definition
        | function
        | variable SEMI
        | type_alias SEMI
;

class_definition: class_definition_init statements RBRACE
;

class_definition_init: class_extends
        | class_no_extends
;

class_no_extends: CLASS id_name LBRACE
;

class_extends: CLASS id_name EXTENDS type LBRACE
;

function: function_init statements RBRACE
;

function_init: type id_name LPAREN argument_declaration RPAREN LBRACE
;

argument_declaration:
        | variable
        | argument_declaration COMMA variable
;

argument_list:
        | expression
        | argument_list COMMA expression
;

variable: variable_no_value
        | variable_with_value
;

variable_no_value: type id_name
;

variable_with_value: type id_name ASSIGN expression
;

type_alias: TYPEDEF type id_name
;

id_name: ID
        | ID COLON string_constant
;

type: INT
        | UBYTE
        | FLOAT
        | STRING
        | VARIANT
        | BOOL
        | VOID
        | ID
        | array
;

array: type AT
;

constant: ICONST
        | FCONST
        | string_constant
        | NULL
        | TRUE
        | FALSE
;

string_constant: SCONST
        | string_constant SCONST
;
