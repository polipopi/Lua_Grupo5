
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
concatenaciones = []

# INICIO APORTE PAULA BASTIDAS: REGLAS SEMANTICAS
errores_semanticos = []
tabla_simbolos = {}

funciones_predefinidas = {
    'print', 'pairs', 'ipairs', 'type', 'tostring',
    'tonumber', 'setmetatable', 'assert', 'error',
    'pcall', 'xpcall', 'require'
}
# FIN APORTE PAULA BASTIDAS


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

    # INICIO APORTE PAULA BASTIDAS: REGISTRO DE IDENTIFICADORES
    if len(p) == 3:
        for nombre in p[2]:
            tabla_simbolos[nombre] = 'variable'
    else:
        nombres = p[2]
        valores = p[4]

        for i, nombre in enumerate(nombres):
            if i < len(valores):
                tabla_simbolos[nombre] = valores[i]
                
            else:
                tabla_simbolos[nombre] = 'variable'
    # FIN APORTE PAULA BASTIDAS

# Permite asignar varios valores a varias variables.
def p_lista_variables(p):
    '''lista_variables : variable
                       | lista_variables COMMA variable'''

    # INICIO APORTE PAULA BASTIDAS
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
    # FIN APORTE PAULA BASTIDAS

# FIN APORTE PAULA BASTIDAS


# =====================================================
# ESTRUCTURA FOR
# APORTE ANTHONY SANTANA
# =====================================================

def p_sentencia_for(p):
    'sentencia : FOR ID ASSIGN expresion COMMA expresion paso DO programa END'
    # Inicio, limite y paso para la regla semantica de Anthony.
    pasos_for.append((p.lineno(1), p[4], p[6], p[7]))


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

    # INICIO APORTE PAULA BASTIDAS: REGISTRO DE FUNCIONES
    tabla_simbolos[p[2]] = 'function'
    # FIN APORTE PAULA BASTIDAS

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
    # Tipo para revisar los controles del for (Anthony Santana).
    p[0] = 'function'


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

    # INICIO APORTE PAULA BASTIDAS: REGLA SEMANTICA 2
    nombre = p[1]

    if nombre not in funciones_predefinidas and tabla_simbolos.get(nombre) != 'function':
        errores_semanticos.append(
            f"Error semántico [Identificadores] en la línea {p.lineno(2)}: "
            f"'{nombre}' no es una función"
        )

    p[0] = 'unknown'
    # FIN APORTE PAULA BASTIDAS

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

    # INICIO APORTE PAULA BASTIDAS
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
    # FIN APORTE PAULA BASTIDAS

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
        # INICIO APORTE PAULA BASTIDAS: REGLA SEMANTICA 4
    operadores_aritmeticos = ('+', '-', '*', '/', '//', '%', '^')

    if p[2] in operadores_aritmeticos:
        tipo1 = p[1]
        tipo2 = p[3]

        def obtener_tipo(valor):
            if isinstance(valor, (int, float)):
                return 'number'

            if isinstance(valor, str):
                return valor if valor in (
                    'boolean', 'nil', 'table', 'function', 'string'
                ) else 'unknown'

            if isinstance(valor, tuple):
                if len(valor) == 3 and valor[0] in operadores_aritmeticos:
                    tipo1 = obtener_tipo(valor[1])
                    tipo2 = obtener_tipo(valor[2])

                    if tipo1 == 'number' and tipo2 == 'number':
                        return 'number'

            return 'unknown'

        tipo_izquierdo = obtener_tipo(tipo1)
        tipo_derecho = obtener_tipo(tipo2)

        if tipo_izquierdo not in ('number', 'unknown') or tipo_derecho not in ('number', 'unknown'):
            errores_semanticos.append(
                f"Error semántico [Operaciones] en la línea {p.lineno(2)}: "
                f"no se puede aplicar '{p[2]}' entre {tipo_izquierdo} y {tipo_derecho}"
            )

        p[0] = (p[2], p[1], p[3])

    # FIN APORTE PAULA BASTIDAS

    # Datos para la regla semantica de concatenacion de Anthony.
    elif p[2] == '..':
        concatenaciones.append((p.lineno(2), p[1], p[3]))
        p[0] = 'string'


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
    p[0] = ('negativo', p[2])


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

    # INICIO APORTE PAULA BASTIDAS: TIPOS DE IDENTIFICADORES
    if p.slice[1].type in ('INTEGER', 'FLOAT'):
        p[0] = p[1]

    elif p.slice[1].type in ('TRUE', 'FALSE'):
        p[0] = 'boolean'

    elif p.slice[1].type == 'NIL':
        p[0] = 'nil'

    elif p.slice[1].type == 'STRING':
        contenido = str(p[1]).strip('"\'')
        try:
            float(contenido)
            p[0] = 'number'
        except ValueError:
            p[0] = 'string'

    elif p.slice[1].type == 'variable':
        p[0] = tabla_simbolos.get(p[1], 'unknown')
    # FIN APORTE PAULA BASTIDAS

# =====================================================
# VARIABLES Y ACCESO A TABLAS
# APORTE ANTHONY SANTANA
# =====================================================
def p_variable(p):
    '''variable : ID
                | variable LBRACKET expresion RBRACKET'''

    # INICIO APORTE PAULA BASTIDAS: IDENTIFICADORES
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1]
    # FIN APORTE PAULA BASTIDAS

# =====================================================
# TABLAS Y DICCIONARIOS
# INICIO APORTE PAULA BASTIDAS
# =====================================================

# Reconoce tablas vacias y tablas con elementos.
def p_expresion_tabla(p):
    '''expresion : LBRACE RBRACE
                 | LBRACE elementos RBRACE
                 | LBRACE elementos separador RBRACE'''
    # Tipo para revisar los controles del for (Anthony Santana).
    p[0] = 'table'


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
# IF / ELSEIF / ELSE
# INICIO APORTE SHIRLEY ARAGON
# =====================================================

def p_sentencia_if(p):
    'sentencia : IF expresion THEN programa lista_elseif parte_else END'


# puede haber varios elseif seguidos o ninguno
def p_lista_elseif(p):
    '''lista_elseif : lista_elseif ELSEIF expresion THEN programa
                    | '''


def p_parte_else(p):
    '''parte_else : ELSE programa
                  | '''

# FIN APORTE SHIRLEY ARAGON


# =====================================================
# FUNCION CON RETORNO
# INICIO APORTE SHIRLEY ARAGON
# =====================================================

# el return lo toma programa con retorno_opcional
def p_sentencia_funcion_retorno(p):
    '''sentencia : FUNCTION ID LPAREN nombres RPAREN programa END
                 | FUNCTION ID LPAREN RPAREN programa END'''

    # INICIO APORTE PAULA BASTIDAS: REGISTRO DE FUNCIONES
    tabla_simbolos[p[2]] = 'function'
    # FIN APORTE PAULA BASTIDAS
# FIN APORTE SHIRLEY ARAGON


# =====================================================
# ACCESO CON PUNTO (persona.nombre, io.read)
# INICIO APORTE SHIRLEY ARAGON
# =====================================================

def p_variable_campo(p):
    'variable : variable DOT ID'

    # INICIO APORTE PAULA BASTIDAS: IDENTIFICADORES
    p[0] = str(p[1]) + '.' + str(p[3])
    # FIN APORTE PAULA BASTIDAS
    
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

    # INICIO APORTE PAULA BASTIDAS: REGISTRO DE FUNCIONES LOCALES
    tabla_simbolos[p[3]] = 'function'
    # FIN APORTE PAULA BASTIDAS
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


# Nombre de la tabla que contiene la funcion: Clase o modulo.Clase
def p_ruta_funcion(p):
    '''ruta_funcion : ID
                    | ruta_funcion DOT ID'''


# Llamada a un metodo con dos puntos: objeto:metodo(argumentos)
def p_llamada_metodo(p):
    '''llamada : variable COLON ID LPAREN argumentos RPAREN
               | variable COLON ID STRING'''

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
    errores.clear()
    pasos_for.clear()
    concatenaciones.clear()
    errores_semanticos.clear()
    tabla_simbolos.clear()

    lexer.lineno = 1
    lexer.errors = []

    parser.parse(codigo, lexer=lexer)

    return lexer.errors + errores