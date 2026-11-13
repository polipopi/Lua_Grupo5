import ply.yacc as yacc
from lexer import lexer, tokens


# INICIO APORTE ANTHONY SANTANA
# Asignacion global, expresiones aritmeticas y matrices.
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'FLOORDIV', 'MOD'),
    ('right', 'UMINUS'),
    ('right', 'POW'),
)

errores = []


def p_programa(p):
    '''programa : programa sentencia
                | '''


def p_sentencia(p):
    '''sentencia : variable ASSIGN expresion
                 | SEMI'''


def p_expresion_binaria(p):
    '''expresion : expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion
                 | expresion FLOORDIV expresion
                 | expresion MOD expresion
                 | expresion POW expresion'''


def p_expresion_negativa(p):
    'expresion : MINUS expresion %prec UMINUS'


def p_expresion_parentesis(p):
    'expresion : LPAREN expresion RPAREN'


def p_expresion_valor(p):
    '''expresion : INTEGER
                 | FLOAT
                 | variable'''


# Una matriz es una tabla con otras tablas como filas.
def p_variable(p):
    '''variable : ID
                | variable LBRACKET expresion RBRACKET'''


def p_expresion_tabla(p):
    '''expresion : LBRACE RBRACE
                 | LBRACE elementos RBRACE
                 | LBRACE elementos separador RBRACE'''


def p_elementos(p):
    '''elementos : expresion
                 | elementos separador expresion'''


def p_separador(p):
    '''separador : COMMA
                 | SEMI'''


def p_error(token):
    if token is None:
        errores.append(f"Error sintactico: fin de archivo inesperado, linea {lexer.lineno}")
    else:
        errores.append(
            f"Error sintactico: token {token.value!r} inesperado, linea {token.lineno}"
        )


parser = yacc.yacc(start='programa', write_tables=False, debug=False)


def analizar(codigo):
    errores.clear()
    lexer.lineno = 1
    lexer.errors = []
    parser.parse(codigo, lexer=lexer)
    return lexer.errors + errores

# FIN APORTE ANTHONY SANTANA
