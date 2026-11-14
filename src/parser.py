
import ply.yacc as yacc
from lexer import lexer, tokens


# =====================================================
# PRECEDENCIA DE OPERADORES
# INICIO APORTE PAULA BASTIDAS
# =====================================================

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
    ('right', 'NOT'),
    ('right', 'CONCAT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'FLOORDIV', 'MOD'),
    ('right', 'UMINUS', 'HASH'),
    ('right', 'POW'),
)

# FIN APORTE PAULA BASTIDAS


errores = []
pasos_for = []


# =====================================================
# PROGRAMA PRINCIPAL
# =====================================================

def p_programa(p):
    'programa : sentencias retorno_opcional'


def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | '''


# =====================================================
# ASIGNACIONES
# INICIO APORTE PAULA BASTIDAS
# =====================================================

def p_sentencia(p):
    '''sentencia : lista_variables ASSIGN lista_expresiones
                 | SEMI'''


def p_sentencia_local(p):
    '''sentencia : LOCAL lista_variables
                 | LOCAL lista_variables ASSIGN lista_expresiones'''


# Permite asignar varios valores a varias variables.
def p_lista_variables(p):
    '''lista_variables : variable
                       | lista_variables COMMA variable'''


# FIN APORTE PAULA BASTIDAS


# =====================================================
# ESTRUCTURA FOR
# APORTE ANTHONY SANTANA
# =====================================================

def p_sentencia_for(p):
    'sentencia : FOR ID ASSIGN expresion COMMA expresion paso DO programa END'
    pasos_for.append((p.lineno(1), p[7]))


def p_paso(p):
    '''paso : COMMA expresion
            | '''
    p[0] = p[2] if len(p) == 3 else 1


# =====================================================
# ESTRUCTURA WHILE
# INICIO APORTE PAULA BASTIDAS
# =====================================================

def p_sentencia_while(p):
    'sentencia : WHILE expresion DO programa END'


# FIN APORTE PAULA BASTIDAS


# =====================================================
# FUNCIONES CON VARARGS
# APORTE ANTHONY SANTANA
# =====================================================

def p_sentencia_funcion(p):
    'sentencia : FUNCTION ID LPAREN parametros_variables RPAREN programa END'


def p_parametros_variables(p):
    '''parametros_variables : ELLIPSIS
                            | nombres COMMA ELLIPSIS'''


def p_nombres(p):
    '''nombres : ID
               | nombres COMMA ID'''


# =====================================================
# FUNCIONES ANONIMAS
# INICIO APORTE PAULA BASTIDAS
# =====================================================

# Permite parametros normales, varargs o funciones sin parametros.
def p_parametros(p):
    '''parametros : nombres
                  | nombres COMMA ELLIPSIS
                  | ELLIPSIS
                  | '''


# Reconoce funciones sin nombre propio.
def p_expresion_funcion_anonima(p):
    'expresion : FUNCTION LPAREN parametros RPAREN programa END'


# FIN APORTE PAULA BASTIDAS


# =====================================================
# RETURN
# APORTE ANTHONY SANTANA
# =====================================================

def p_retorno_opcional(p):
    '''retorno_opcional : RETURN
                        | RETURN lista_expresiones
                        | RETURN SEMI
                        | RETURN lista_expresiones SEMI
                        | '''


# =====================================================
# LLAMADAS A FUNCIONES
# APORTE ANTHONY SANTANA
# =====================================================

def p_sentencia_llamada(p):
    'sentencia : llamada'


def p_llamada(p):
    'llamada : variable LPAREN argumentos RPAREN'

def p_expresion_llamada(p):
    'expresion : llamada'
    p[0] = p[1]

def p_argumentos(p):
    '''argumentos : lista_expresiones
                  | '''


# =====================================================
# LISTA DE EXPRESIONES
# =====================================================

def p_lista_expresiones(p):
    '''lista_expresiones : expresion
                         | lista_expresiones COMMA expresion'''


# =====================================================
# EXPRESIONES ARITMETICAS, RELACIONALES Y LOGICAS
# INICIO APORTE PAULA BASTIDAS
# =====================================================

def p_expresion_binaria(p):
    '''expresion : expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion
                 | expresion FLOORDIV expresion
                 | expresion MOD expresion
                 | expresion POW expresion
                 | expresion EQ expresion
                 | expresion NE expresion
                 | expresion LT expresion
                 | expresion LE expresion
                 | expresion GT expresion
                 | expresion GE expresion
                 | expresion AND expresion
                 | expresion OR expresion
                 | expresion CONCAT expresion'''


# Reconoce la negacion logica.
def p_expresion_not(p):
    'expresion : NOT expresion %prec NOT'


# FIN APORTE PAULA BASTIDAS


# =====================================================
# EXPRESIONES UNARIAS
# APORTE ANTHONY SANTANA
# =====================================================

def p_expresion_negativa(p):
    'expresion : MINUS expresion %prec UMINUS'
    if isinstance(p[2], (int, float)):
        p[0] = -p[2]


def p_expresion_longitud(p):
    'expresion : HASH expresion'


def p_expresion_parentesis(p):
    'expresion : LPAREN expresion RPAREN'
    p[0] = p[2]


# =====================================================
# VALORES Y VARIABLES
# =====================================================

def p_expresion_valor(p):
    '''expresion : INTEGER
                 | FLOAT
                 | STRING
                 | TRUE
                 | FALSE
                 | NIL
                 | ELLIPSIS
                 | variable'''
    if p.slice[1].type in ('INTEGER', 'FLOAT'):
        p[0] = p[1]


# =====================================================
# VARIABLES Y ACCESO A TABLAS
# APORTE ANTHONY SANTANA
# =====================================================

def p_variable(p):
    '''variable : ID
                | variable LBRACKET expresion RBRACKET'''


# =====================================================
# TABLAS Y DICCIONARIOS
# INICIO APORTE PAULA BASTIDAS
# =====================================================

# Reconoce tablas vacias y tablas con elementos.
def p_expresion_tabla(p):
    '''expresion : LBRACE RBRACE
                 | LBRACE elementos RBRACE
                 | LBRACE elementos separador RBRACE'''


# Permite campos separados por coma o punto y coma.
def p_elementos(p):
    '''elementos : campo
                 | elementos separador campo'''


# Reconoce claves con nombre, claves entre corchetes
# y elementos normales de una tabla.
def p_campo(p):
    '''campo : ID ASSIGN expresion
             | LBRACKET expresion RBRACKET ASSIGN expresion
             | expresion'''


def p_separador(p):
    '''separador : COMMA
                 | SEMI'''


# FIN APORTE PAULA BASTIDAS


# =====================================================
# ERRORES SINTACTICOS
# =====================================================

def p_error(token):
    if token is None:
        errores.append(
            f"Error sintactico: fin de archivo inesperado, linea {lexer.lineno}"
        )
    else:
        errores.append(
            f"Error sintactico: token {token.value!r} inesperado, "
            f"linea {token.lineno}"
        )


# =====================================================
# CREACION DEL ANALIZADOR
# =====================================================

parser = yacc.yacc(
    start='programa',
    write_tables=False,
    debug=False
)


# =====================================================
# FUNCION PARA ANALIZAR CODIGO
# =====================================================

def analizar(codigo):
    errores.clear()
    pasos_for.clear()

    lexer.lineno = 1
    lexer.errors = []

    parser.parse(codigo, lexer=lexer)

    return lexer.errors + errores