
import re
import ply.lex as lex

# =====================================================
# PALABRAS RESERVADAS
# =====================================================
# INICIO APORTE SHIRLEY ARAGÓN: PALABRAS RESERVADAS
# Las 19 palabras reservadas de Lua 5.4 que no son
# valores; true, false y nil estan en el bloque de Marlo.
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
# FIN APORTE SHIRLEY ARAGÓN

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

# INICIO APORTE SHIRLEY ARAGÓN: IDENTIFICADORES
# Un nombre empieza con letra o guion bajo; si coincide
# con una palabra reservada se devuelve su token propio,
# si no, se devuelve ID.

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# FIN APORTE SHIRLEY ARAGÓN

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

# INICIO APORTE MARLO VALLE: CADENAS CORTAS
# El contenido no puede incluir la comilla de apertura sin
# escapar; asi "a" .. "b" produce dos cadenas y no una sola.
# Una barra invertida seguida de salto de linea es valida.
def t_STRING(t):
    r'"([^"\\\n]|\\(.|\n))*"|\'([^\'\\\n]|\\(.|\n))*\''
    linea_inicial = t.lexer.lineno
    t.lexer.lineno += t.value.count('\n')
    if not validar_escapes(t, linea_inicial):
        return None
    return t


# Secuencias de escape permitidas en Lua:
# \a \b \f \n \r \t \v \\ \" \' \<salto> \z \xXX \ddd \u{XXX}
ESCAPE_VALIDO = re.compile(
    r'\\([abfnrtv\\"\'\n]|z|x[0-9a-fA-F]{2}|\d{1,3}|u\{[0-9a-fA-F]+\})'
)


def validar_escapes(t, linea_inicial):
    valor = t.value
    i = 0
    while i < len(valor):
        if valor[i] != '\\':
            i += 1
            continue
        escape = ESCAPE_VALIDO.match(valor, i)
        if escape is None or (escape.group(1).isdigit()
                              and int(escape.group(1)) > 255):
            secuencia = valor[i:i + 2] if escape is None else escape.group()
            registrar_error(
                t.lexer,
                f"secuencia de escape inválida '{secuencia}'",
                linea_inicial + valor.count('\n', 0, i),
                t.lexpos + i
            )
            return False
        i = escape.end()
    return True


# Una comilla que llega al fin de linea sin cerrarse es un error.
# Se define despues de t_STRING para que solo actue si esta falla.
def t_STRING_SIN_CERRAR(t):
    r'"([^"\\\n]|\\(.|\n))*|\'([^\'\\\n]|\\(.|\n))*'
    registrar_error(
        t.lexer,
        f"cadena sin cerrar {t.value.splitlines()[0]}",
        t.lineno,
        t.lexpos
    )
    t.lexer.lineno += t.value.count('\n')


# Cadenas largas: [[ ... ]], [=[ ... ]=], [==[ ... ]==], etc.
# Pueden ocupar varias lineas y no procesan escapes. Se busca
# manualmente el cierre con el mismo numero de signos '='.
# Al ser funcion, se evalua antes que el delimitador LBRACKET.
def t_STRING_LARGA(t):
    r'\[=*\['
    datos = t.lexer.lexdata
    niveles = len(t.value) - 2
    cierre = ']' + '=' * niveles + ']'
    fin = datos.find(cierre, t.lexer.lexpos)

    if fin == -1:
        registrar_error(
            t.lexer,
            f"cadena larga sin cerrar (falta '{cierre}')",
            t.lineno,
            t.lexpos
        )
        t.lexer.lineno += datos.count('\n', t.lexpos)
        t.lexer.lexpos = len(datos)
        return None

    t.lexer.lexpos = fin + len(cierre)
    t.value = datos[t.lexpos:t.lexer.lexpos]
    t.lexer.lineno += t.value.count('\n')
    t.type = 'STRING'
    return t
# FIN APORTE MARLO VALLE


# =====================================================
# COMENTARIOS
# INICIO APORTE MARLO VALLE-SHIRLEY ARAGÓN: ORDEN DE COMENTARIOS
# PLY prueba las funciones en el orden en que se definen;
# si los comentarios van despues de t_MINUS, '--' se lee
# como dos restas. Por eso se definen antes de operadores.
# =====================================================

# Comentarios largos: --[[ ... ]], --[==[ ... ]==], etc.
def t_COMMENT_LARGO(t):
    r'--\[=*\['
    datos = t.lexer.lexdata
    cierre = ']' + '=' * (len(t.value) - 4) + ']'
    fin = datos.find(cierre, t.lexer.lexpos)

    if fin == -1:
        registrar_error(
            t.lexer,
            f"comentario largo sin cerrar (falta '{cierre}')",
            t.lineno,
            t.lexpos
        )
        t.lexer.lineno += datos.count('\n', t.lexpos)
        t.lexer.lexpos = len(datos)
        return None

    fin += len(cierre)
    t.lexer.lineno += datos.count('\n', t.lexpos, fin)
    t.lexer.lexpos = fin


def t_COMMENT(t):
    r'--[^\n]*'
    pass
# FIN APORTE MARLO VALLE -SHIRLEY ARAGÓN


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
# ESPACIOS Y SALTOS DE LINEA
# =====================================================

t_ignore = ' \t\r'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# =====================================================
# ERRORES LEXICOS
# =====================================================

# INICIO APORTE MARLO VALLE: MANEJO DE TOKENS DE ERROR
# Todos los errores se registran con linea y posicion (columna)
# con el formato definido en el documento del proyecto, para
# ubicar con precision el token invalido en el codigo fuente.

def encontrar_columna(lexer, posicion):
    inicio_linea = lexer.lexdata.rfind('\n', 0, posicion) + 1
    return posicion - inicio_linea + 1


def registrar_error(lexer, mensaje, linea, posicion):
    columna = encontrar_columna(lexer, posicion)
    lexer.errors.append(
        f"Error léxico: {mensaje} en la línea {linea}, posición {columna}"
    )


def t_error(t):
    registrar_error(
        t.lexer,
        f"carácter {t.value[0]!r} no reconocido",
        t.lineno,
        t.lexpos
    )
    t.lexer.skip(1)
# FIN APORTE MARLO VALLE


# =====================================================
# CREACION DEL ANALIZADOR
# =====================================================

lexer = lex.lex()
