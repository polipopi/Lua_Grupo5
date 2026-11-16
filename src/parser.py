
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
    ('right', 'CONCAT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'FLOORDIV', 'MOD'),
    # NOT tiene precedencia unaria al revisar concatenaciones (Anthony).
    ('right', 'UMINUS', 'HASH', 'NOT'),
    ('right', 'POW'),
)

# FIN APORTE PAULA BASTIDAS


errores = []
pasos_for = []
concatenaciones = []
arbol = []


# APORTE SEMANTICO ANTHONY SANTANA
# Las acciones p[0] guardan expresiones, asignaciones y bloques para revisar
# mis reglas usando los valores disponibles en cada parte del programa.
def nombre_variable(nombre, linea):
    return ('variable', linea, nombre)


def campo_variable(base, nombre, linea):
    clave = ('literal', linea, 'STRING', repr(nombre), False)
    return ('indice', linea, base, clave)


def ruta_variable(nombres, linea):
    variable = nombre_variable(nombres[0], linea)
    for nombre in nombres[1:]:
        variable = campo_variable(variable, nombre, linea)
    return variable


# =====================================================
# PROGRAMA PRINCIPAL
# =====================================================

def p_programa(p):
    'programa : sentencias retorno_opcional'
    p[0] = p[1]
    if p[2] is not None:
        p[0].append(p[2])


def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | '''
    p[0] = p[1] if len(p) == 3 else []
    if len(p) == 3 and p[2] is not None:
        p[0].append(p[2])


# =====================================================
# ASIGNACIONES
# INICIO APORTE PAULA BASTIDAS
# =====================================================

def p_sentencia(p):
    '''sentencia : lista_variables ASSIGN lista_expresiones
                 | SEMI'''
    if len(p) == 4:
        p[0] = ('asignacion', p.lineno(2), p[1], p[3], False)


def p_sentencia_local(p):
    '''sentencia : LOCAL lista_variables
                 | LOCAL lista_variables ASSIGN lista_expresiones'''
    p[0] = ('asignacion', p.lineno(1), p[2], p[4] if len(p) == 5 else [], True)


# Permite asignar varios valores a varias variables.
def p_lista_variables(p):
    '''lista_variables : variable
                       | lista_variables COMMA variable'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


# FIN APORTE PAULA BASTIDAS


# =====================================================
# ESTRUCTURA FOR
# APORTE ANTHONY SANTANA
# =====================================================

def p_sentencia_for(p):
    'sentencia : FOR ID ASSIGN expresion COMMA expresion paso DO programa END'
    # Inicio, limite y paso para la regla semantica de Anthony.
    pasos_for.append((p.lineno(1), p[4], p[6], p[7]))
    p[0] = ('for', p.lineno(1), p[2], p[4], p[6], p[7], p[9])


def p_paso(p):
    '''paso : COMMA expresion
            | '''
    p[0] = p[2] if len(p) == 3 else ('literal', 0, 'INTEGER', 1, False)


# =====================================================
# ESTRUCTURA WHILE
# INICIO APORTE PAULA BASTIDAS
# =====================================================

def p_sentencia_while(p):
    'sentencia : WHILE expresion DO programa END'
    p[0] = ('while', p.lineno(1), p[2], p[4])


# FIN APORTE PAULA BASTIDAS


# =====================================================
# FUNCIONES CON VARARGS
# APORTE ANTHONY SANTANA
# =====================================================

def p_sentencia_funcion(p):
    'sentencia : FUNCTION ID LPAREN parametros_variables RPAREN programa END'
    p[0] = ('definir_funcion', p.lineno(1), nombre_variable(p[2], p.lineno(2)), p[4], p[6], False)


def p_parametros_variables(p):
    '''parametros_variables : ELLIPSIS
                            | nombres COMMA ELLIPSIS'''
    p[0] = (p[1] if len(p) == 4 else [], True)


def p_nombres(p):
    '''nombres : ID
               | nombres COMMA ID'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


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
    if len(p) == 1:
        p[0] = ([], False)
    elif len(p) == 4:
        p[0] = (p[1], True)
    elif p.slice[1].type == 'ELLIPSIS':
        p[0] = ([], True)
    else:
        p[0] = (p[1], False)


# Reconoce funciones sin nombre propio.
def p_expresion_funcion_anonima(p):
    'expresion : FUNCTION LPAREN parametros RPAREN programa END'
    p[0] = ('funcion', p.lineno(1), p[3], p[5])


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
    if len(p) > 1:
        valores = p[2] if len(p) > 2 and isinstance(p[2], list) else []
        p[0] = ('retorno', p.lineno(1), valores)


# =====================================================
# LLAMADAS A FUNCIONES
# APORTE ANTHONY SANTANA
# =====================================================

def p_sentencia_llamada(p):
    'sentencia : llamada'
    p[0] = ('expresion', p[1][1], p[1])


def p_llamada(p):
    'llamada : variable LPAREN argumentos RPAREN'
    p[0] = ('llamada', p.lineno(2), p[1], p[3])

def p_expresion_llamada(p):
    'expresion : llamada'
    p[0] = p[1]

def p_argumentos(p):
    '''argumentos : lista_expresiones
                  | '''
    p[0] = p[1] if len(p) == 2 else []


# =====================================================
# LISTA DE EXPRESIONES
# =====================================================

def p_lista_expresiones(p):
    '''lista_expresiones : expresion
                         | lista_expresiones COMMA expresion'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


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
    p[0] = ('binaria', p.lineno(2), p[2], p[1], p[3])
    if p[2] == '..':
        concatenaciones.append((p.lineno(2), p[1], p[3]))


# Reconoce la negacion logica.
def p_expresion_not(p):
    'expresion : NOT expresion %prec NOT'
    p[0] = ('unaria', p.lineno(1), 'not', p[2])


# FIN APORTE PAULA BASTIDAS


# =====================================================
# EXPRESIONES UNARIAS
# APORTE ANTHONY SANTANA
# =====================================================

def p_expresion_negativa(p):
    'expresion : MINUS expresion %prec UMINUS'
    p[0] = ('unaria', p.lineno(1), '-', p[2])


def p_expresion_longitud(p):
    'expresion : HASH expresion'
    p[0] = ('unaria', p.lineno(1), '#', p[2])


def p_expresion_parentesis(p):
    'expresion : LPAREN expresion RPAREN'
    p[0] = ('grupo', p.lineno(1), p[2])


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
    tipo = p.slice[1].type
    if tipo == 'variable':
        p[0] = p[1]
    elif tipo == 'ELLIPSIS':
        p[0] = ('varargs', p.lineno(1))
    else:
        hexadecimal = tipo == 'INTEGER' and lexer.lexdata[p.lexpos(1):p.lexpos(1) + 2].lower() == '0x'
        p[0] = ('literal', p.lineno(1), tipo, p[1], hexadecimal)


# =====================================================
# VARIABLES Y ACCESO A TABLAS
# APORTE ANTHONY SANTANA
# =====================================================

def p_variable(p):
    '''variable : ID
                | variable LBRACKET expresion RBRACKET'''
    p[0] = nombre_variable(p[1], p.lineno(1)) if len(p) == 2 else ('indice', p.lineno(2), p[1], p[3])


# =====================================================
# TABLAS Y DICCIONARIOS
# INICIO APORTE PAULA BASTIDAS
# =====================================================

# Reconoce tablas vacias y tablas con elementos.
def p_expresion_tabla(p):
    '''expresion : LBRACE RBRACE
                 | LBRACE elementos RBRACE
                 | LBRACE elementos separador RBRACE'''
    p[0] = ('tabla', p.lineno(1), p[2] if len(p) > 3 else [])


# Permite campos separados por coma o punto y coma.
def p_elementos(p):
    '''elementos : campo
                 | elementos separador campo'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


# Reconoce claves con nombre, claves entre corchetes
# y elementos normales de una tabla.
def p_campo(p):
    '''campo : ID ASSIGN expresion
             | LBRACKET expresion RBRACKET ASSIGN expresion
             | expresion'''
    if len(p) == 2:
        p[0] = (None, p[1])
    elif len(p) == 4:
        clave = ('literal', p.lineno(1), 'STRING', repr(p[1]), False)
        p[0] = (clave, p[3])
    else:
        p[0] = (p[2], p[5])


def p_separador(p):
    '''separador : COMMA
                 | SEMI'''


# FIN APORTE PAULA BASTIDAS
# =====================================================
# IF / ELSEIF / ELSE
# INICIO APORTE SHIRLEY ARAGON
# =====================================================

def p_sentencia_if(p):
    'sentencia : IF expresion THEN programa lista_elseif parte_else END'
    p[0] = ('if', p.lineno(1), [(p[2], p[4])] + p[5], p[6])


# puede haber varios elseif seguidos o ninguno
def p_lista_elseif(p):
    '''lista_elseif : lista_elseif ELSEIF expresion THEN programa
                    | '''
    p[0] = p[1] + [(p[3], p[5])] if len(p) == 6 else []


def p_parte_else(p):
    '''parte_else : ELSE programa
                  | '''
    p[0] = p[2] if len(p) == 3 else []

# FIN APORTE SHIRLEY ARAGON


# =====================================================
# FUNCION CON RETORNO
# INICIO APORTE SHIRLEY ARAGON
# =====================================================

# el return lo toma programa con retorno_opcional
def p_sentencia_funcion_retorno(p):
    '''sentencia : FUNCTION ID LPAREN nombres RPAREN programa END
                 | FUNCTION ID LPAREN RPAREN programa END'''
    parametros = (p[4], False) if len(p) == 8 else ([], False)
    cuerpo = p[6] if len(p) == 8 else p[5]
    p[0] = ('definir_funcion', p.lineno(1), nombre_variable(p[2], p.lineno(2)), parametros, cuerpo, False)

# FIN APORTE SHIRLEY ARAGON


# =====================================================
# ACCESO CON PUNTO (persona.nombre, io.read)
# INICIO APORTE SHIRLEY ARAGON
# =====================================================

def p_variable_campo(p):
    'variable : variable DOT ID'
    p[0] = campo_variable(p[1], p[3], p.lineno(2))

# FIN APORTE SHIRLEY ARAGON


# =====================================================
# CONSTANTES (Lua 5.4)
# INICIO APORTE MARLO VALLE
# =====================================================

# local PI <const> = 3.1416
# local archivo <close> = recurso
# La constante puede declararse con o sin valor inicial.
def p_sentencia_constante(p):
    '''sentencia : LOCAL ID atributo ASSIGN lista_expresiones
                 | LOCAL ID atributo'''
    p[0] = ('asignacion', p.lineno(1), [nombre_variable(p[2], p.lineno(2))],
            p[5] if len(p) == 6 else [], True)


# Lua 5.4 solo acepta los atributos const y close.
def p_atributo(p):
    'atributo : LT ID GT'
    if p[2] not in ('const', 'close'):
        errores.append(
            f"Error sintactico: atributo {p[2]!r} desconocido, "
            f"se esperaba 'const' o 'close', linea {p.lineno(2)}"
        )

# FIN APORTE MARLO VALLE


# =====================================================
# ESTRUCTURA REPEAT ... UNTIL
# INICIO APORTE MARLO VALLE
# =====================================================

# El cuerpo se ejecuta al menos una vez y se repite
# hasta que la condicion sea verdadera:
# repeat n = n + 1 until n >= 3
def p_sentencia_repeat(p):
    'sentencia : REPEAT programa UNTIL expresion'
    p[0] = ('repeat', p.lineno(1), p[2], p[4])

# FIN APORTE MARLO VALLE


# =====================================================
# SENTENCIA BREAK
# INICIO APORTE MARLO VALLE
# =====================================================

# break termina el bucle mas interno (while, for o repeat).
# Sintacticamente puede ir en cualquier bloque; que este dentro
# de un bucle lo revisa la regla semantica 7.
def p_sentencia_break(p):
    'sentencia : BREAK'
    p[0] = ('break', p.lineno(1))

# FIN APORTE MARLO VALLE


# =====================================================
# FUNCION LOCAL CON PARAMETRO OPCIONAL
# INICIO APORTE MARLO VALLE
# =====================================================

# local function saludar(nombre, saludo)
#     saludo = saludo or "Hola"
# end
# En Lua todo parametro es opcional: si no se envia vale nil,
# y el valor por defecto se asigna con el operador or.
def p_sentencia_funcion_local(p):
    'sentencia : LOCAL FUNCTION ID LPAREN parametros RPAREN programa END'
    p[0] = ('definir_funcion', p.lineno(1), nombre_variable(p[3], p.lineno(3)), p[5], p[7], True)

# FIN APORTE MARLO VALLE


# =====================================================
# CONJUNTOS
# INICIO APORTE MARLO VALLE
# =====================================================

# Un conjunto es una tabla cuyas claves son los elementos:
#   local colores = {rojo = true, ["azul"] = true}   (crear)
#   colores["verde"] = true                          (agregar)
#   colores.rojo = nil                               (eliminar)
#   if colores["azul"] then ... end                  (pertenencia)
# Crear, agregar, eliminar y consultar ya se reconocen con
# las reglas de tablas y variables. Para recorrer sus
# elementos se agrega el for generico:
#   for elemento in pairs(colores) do ... end
def p_sentencia_for_generico(p):
    'sentencia : FOR nombres IN lista_expresiones DO programa END'
    p[0] = ('for_generico', p.lineno(1), p[2], p[4], p[6])

# FIN APORTE MARLO VALLE


# =====================================================
# IMPRESION Y LECTURA DE DATOS
# INICIO APORTE MARLO VALLE
# =====================================================

# Las formas con parentesis se reconocen como llamadas:
#   print("Total:", total)        io.write("Nombre: ")
#   local nombre = io.read("l")   local edad = io.read("n")
# Lua tambien permite llamar sin parentesis cuando el unico
# argumento es una cadena:
#   print "Hola Mundo"            local linea = io.read "l"
def p_llamada_cadena(p):
    'llamada : variable STRING'
    argumento = ('literal', p.lineno(2), 'STRING', p[2], False)
    p[0] = ('llamada', p.lineno(2), p[1], [argumento])

# FIN APORTE MARLO VALLE


# =====================================================
# CLASES, PROPIEDADES Y METODOS
# INICIO APORTE MARLO VALLE
# =====================================================

# En Lua una clase es una tabla con metatabla:
#   local Persona = {}
#   Persona.__index = Persona
#   function Persona.nuevo(nombre)            (constructor)
#       local obj = setmetatable({}, Persona)
#       obj.nombre = nombre                   (propiedad)
#       return obj
#   end
#   function Persona:saludar()                (metodo, usa self)
#       print("Hola, soy " .. self.nombre)
#   end
#   local p = Persona.nuevo("Ana")
#   p:saludar()                               (llamada a metodo)
# Las propiedades se manejan con el acceso con punto.

def p_sentencia_metodo(p):
    '''sentencia : FUNCTION ruta_funcion COLON ID LPAREN parametros RPAREN programa END
                 | FUNCTION ruta_funcion DOT ID LPAREN parametros RPAREN programa END'''
    destino = campo_variable(ruta_variable(p[2], p.lineno(1)), p[4], p.lineno(3))
    nombres, variable = p[6]
    if p.slice[3].type == 'COLON':
        nombres = ['self'] + nombres
    p[0] = ('definir_funcion', p.lineno(1), destino, (nombres, variable), p[8], False)


# Nombre de la tabla que contiene la funcion: Clase o modulo.Clase
def p_ruta_funcion(p):
    '''ruta_funcion : ID
                    | ruta_funcion DOT ID'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


# Llamada a un metodo con dos puntos: objeto:metodo(argumentos)
def p_llamada_metodo(p):
    '''llamada : variable COLON ID LPAREN argumentos RPAREN
               | variable COLON ID STRING'''
    argumentos = p[5] if len(p) == 7 else [('literal', p.lineno(4), 'STRING', p[4], False)]
    p[0] = ('metodo', p.lineno(2), p[1], p[3], argumentos)

# FIN APORTE MARLO VALLE

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
    global arbol
    arbol = []
    errores.clear()
    pasos_for.clear()
    concatenaciones.clear()

    lexer.lineno = 1
    lexer.errors = []

    arbol = parser.parse(codigo, lexer=lexer)

    return lexer.errors + errores
