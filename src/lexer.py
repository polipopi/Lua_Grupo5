
import ply.lex as lex

# =====================================================
# PALABRAS RESERVADAS
# =====================================================

reserved = {
    'and': 'AND',
    'break': 'BREAK',
    'do': 'DO',
    'else': 'ELSE',
    'elseif': 'ELSEIF',
    'end': 'END',
    'for': 'FOR',
    'function': 'FUNCTION',
    'goto': 'GOTO',
    'if': 'IF',
    'in': 'IN',
    'local': 'LOCAL',
    'not': 'NOT',
    'or': 'OR',
    'repeat': 'REPEAT',
    'return': 'RETURN',
    'then': 'THEN',
    'until': 'UNTIL',
    'while': 'WHILE'
}


# =====================================================
# INICIO APORTE MARLO VALLE: LITERALES BOOLEANOS Y NIL
# true, false y nil son palabras reservadas que ademas
# representan valores; se agrupan aqui y se agregan a
# las palabras reservadas para que t_ID las reconozca.
# =====================================================

literales = {
    'true': 'TRUE',
    'false': 'FALSE',
    'nil': 'NIL'
}

reserved.update(literales)

# FIN APORTE MARLO VALLE


# =====================================================
# LISTA GENERAL DE TOKENS
# =====================================================

tokens = [
    'ID',
    'INTEGER',
    'FLOAT',
    'STRING',

    # INICIO APORTE PAULA BASTIDAS
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'FLOORDIV', 'MOD', 'POW',
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
    'CONCAT',
    # FIN APORTE PAULA BASTIDAS

    'ASSIGN',
    'BAND', 'BOR', 'TILDE', 'SHL', 'SHR',
    'HASH',

    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'COMMA', 'SEMI', 'COLON', 'DOT',
    # INICIO APORTE ANTHONY SANTANA: NUEVOS DELIMITADORES
    'DBCOLON', 'ELLIPSIS',
    # FIN APORTE ANTHONY SANTANA
] + list(reserved.values())


# =====================================================
# IDENTIFICADORES Y PALABRAS RESERVADAS
# =====================================================

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


# =====================================================
# NUMEROS
# =====================================================

# INICIO APORTE ANTHONY SANTANA: AJUSTE A LA REGLA FLOAT EXISTENTE
def t_FLOAT(t):
    # Deja .. y ... completos para sus propias reglas.
    r'((\d+\.(?!\.)\d*|\.\d+)([eE][+-]?\d+)?|\d+[eE][+-]?\d+)'
    t.value = float(t.value)
    return t
# FIN APORTE ANTHONY SANTANA


def t_INTEGER(t):
    r'0[xX][0-9a-fA-F]+|\d+'
    if t.value.lower().startswith('0x'):
        t.value = int(t.value, 16)
    else:
        t.value = int(t.value)
    return t


# =====================================================
# INICIO APORTE ANTHONY SANTANA: DELIMITADOR DE VARARGS
# Va antes de CONCAT para reconocer los tres puntos juntos.
def t_ELLIPSIS(t):
    r'\.\.\.'
    return t
# FIN APORTE ANTHONY SANTANA


# =====================================================
# CADENAS
# =====================================================

def t_STRING(t):
    r'"([^\\\n]|\\.)*"|\'([^\\\n]|\\.)*\''
    return t


# =====================================================
# INICIO APORTE PAULA BASTIDAS
# OPERADORES ARITMETICOS, RELACIONALES
# Y DE CONCATENACION
# =====================================================

def t_FLOORDIV(t):
    r'//'
    return t


def t_CONCAT(t):
    r'\.\.'
    return t


def t_EQ(t):
    r'=='
    return t


def t_NE(t):
    r'~='
    return t


def t_LE(t):
    r'<='
    return t


def t_GE(t):
    r'>='
    return t


def t_PLUS(t):
    r'\+'
    return t


def t_MINUS(t):
    r'-'
    return t


def t_TIMES(t):
    r'\*'
    return t


def t_DIVIDE(t):
    r'/'
    return t


def t_MOD(t):
    r'%'
    return t


def t_POW(t):
    r'\^'
    return t


def t_LT(t):
    r'<'
    return t


def t_GT(t):
    r'>'
    return t

# =====================================================
# FIN APORTE PAULA BASTIDAS
# =====================================================


# =====================================================
# OTROS OPERADORES DE LUA
# =====================================================

def t_SHL(t):
    r'<<'
    return t


def t_SHR(t):
    r'>>'
    return t


def t_BAND(t):
    r'&'
    return t


def t_BOR(t):
    r'\|'
    return t


def t_TILDE(t):
    r'~'
    return t


def t_HASH(t):
    r'\#'
    return t


def t_ASSIGN(t):
    r'='
    return t


# =====================================================
# DELIMITADORES
# =====================================================

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_SEMI = r';'
# INICIO APORTE ANTHONY SANTANA: DELIMITADOR DE ETIQUETAS
t_DBCOLON = r'::'
# FIN APORTE ANTHONY SANTANA
t_COLON = r':'
t_DOT = r'\.'


# =====================================================
# COMENTARIOS
# =====================================================

def t_COMMENT(t):
    r'--[^\n]*'
    pass


# =====================================================
# ESPACIOS Y SALTOS DE LINEA
# =====================================================

t_ignore = ' \t\r'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# =====================================================
# ERRORES LEXICOS
# =====================================================

def t_error(t):
    mensaje = (
        f"Caracter no reconocido: {t.value[0]!r}, "
        f"linea {t.lineno}"
    )
    t.lexer.errors.append(mensaje)
    t.lexer.skip(1)


# =====================================================
# CREACION DEL ANALIZADOR
# =====================================================

lexer = lex.lex()
