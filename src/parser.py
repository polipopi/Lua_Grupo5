import ply.yacc as yacc
from lexer import lexer, tokens


# INICIO APORTE ANTHONY SANTANA
# Variable global, expresiones aritmeticas, matrices, for y funciones varargs.
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'FLOORDIV', 'MOD'),
    ('right', 'UMINUS', 'HASH'),
    ('right', 'POW'),
)

errores = []


def p_programa(p):
    'programa : sentencias retorno_opcional'


def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | '''


def p_sentencia(p):
    '''sentencia : variable ASSIGN expresion
                 | SEMI'''


# El paso del for es opcional. Su cuerpo usa las mismas sentencias.
def p_sentencia_for(p):
    'sentencia : FOR ID ASSIGN expresion COMMA expresion paso DO programa END'


def p_paso(p):
    '''paso : COMMA expresion
            | '''


# Funciones con n argumentos. Los parametros con nombre van antes de ...
def p_sentencia_funcion(p):
    'sentencia : FUNCTION ID LPAREN parametros_variables RPAREN programa END'


def p_parametros_variables(p):
    '''parametros_variables : ELLIPSIS
                            | nombres COMMA ELLIPSIS'''


def p_nombres(p):
    '''nombres : ID
               | nombres COMMA ID'''


# Return cierra el bloque. Las llamadas permiten probar la funcion definida.
def p_retorno_opcional(p):
    '''retorno_opcional : RETURN
                        | RETURN lista_expresiones
                        | RETURN SEMI
                        | RETURN lista_expresiones SEMI
                        | '''


def p_sentencia_llamada(p):
    'sentencia : llamada'


def p_llamada(p):
    'llamada : variable LPAREN argumentos RPAREN'


def p_argumentos(p):
    '''argumentos : lista_expresiones
                  | '''


def p_lista_expresiones(p):
    '''lista_expresiones : expresion
                         | lista_expresiones COMMA expresion'''


def p_expresion_llamada(p):
    'expresion : llamada'


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


def p_expresion_longitud(p):
    'expresion : HASH expresion'


def p_expresion_parentesis(p):
    'expresion : LPAREN expresion RPAREN'


def p_expresion_valor(p):
    '''expresion : INTEGER
                 | FLOAT
                 | STRING
                 | TRUE
                 | FALSE
                 | NIL
                 | ELLIPSIS
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
