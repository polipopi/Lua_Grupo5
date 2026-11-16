from lexer import lexer as lexer_base
from reglas_paula import FUNCIONES_PREDEFINIDAS


# INICIO APORTE SHIRLEY ARAGÓN: REGLAS SEMANTICAS 1 Y 3
# Regla 1: una variable tiene que estar declarada antes de usarla.
# Regla 3: una variable <const> no se puede volver a asignar.
# Se recorre el arbol llevando una pila de ambitos, cada bloque abre uno nuevo.

LIBRERIA_ESTANDAR = {
    'io', 'table', 'string', 'math', 'os', 'utf8', 'coroutine', 'debug',
    '_G', '_ENV', '_VERSION', 'select', 'next', 'rawget', 'rawset',
    'rawequal', 'rawlen', 'getmetatable', 'collectgarbage', 'load',
    'dofile', 'loadfile', 'unpack',
}
PREDEFINIDOS = set(FUNCIONES_PREDEFINIDAS) | LIBRERIA_ESTANDAR


# El arbol no guarda si una local es <const>, asi que se busca en los tokens
# el patron: local nombre < const >
def constantes_declaradas(codigo):
    analizador = lexer_base.clone()
    analizador.lineno = 1
    analizador.errors = []
    analizador.input(codigo)
    constantes = set()
    ventana = []
    for token in analizador:
        ventana = (ventana + [token])[-5:]
        tipos = [t.type for t in ventana]
        if tipos == ['LOCAL', 'ID', 'LT', 'ID', 'GT'] and ventana[3].value == 'const':
            constantes.add((ventana[1].lineno, ventana[1].value))
    return constantes


# Variables globales que se asignan en cualquier parte del programa.
# Se usa dentro de las funciones, que se pueden llamar mas tarde.
def globales_asignados(nodo, nombres=None):
    nombres = set() if nombres is None else nombres
    if isinstance(nodo, tuple) and nodo and isinstance(nodo[0], str):
        if nodo[0] == 'asignacion' and not nodo[4]:
            nombres.update(v[2] for v in nodo[2] if v[0] == 'variable')
        elif nodo[0] == 'definir_funcion' and not nodo[5] and nodo[2][0] == 'variable':
            nombres.add(nodo[2][2])
    if isinstance(nodo, (tuple, list)):
        for elemento in nodo:
            if isinstance(elemento, (tuple, list)):
                globales_asignados(elemento, nombres)
    return nombres


class Revisor:
    def __init__(self, constantes, globales_totales):
        self.constantes = constantes
        self.globales_totales = globales_totales
        self.globales_vistos = set()
        self.ambitos = [{}]       
        self.profundidad = 0      
        self.mensajes = []

    def buscar(self, nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None

    # Regla 1
    def leer(self, nodo):
        nombre, linea = nodo[2], nodo[1]
        if self.buscar(nombre) is not None or nombre in PREDEFINIDOS:
            return
        if nombre in self.globales_vistos:
            return
        # dentro de una funcion basta con que la global se asigne en algun lado
        if self.profundidad > 0 and nombre in self.globales_totales:
            return
        self.mensajes.append((
            linea,
            f"Error semántico [Identificadores] en la línea {linea}: "
            f"la variable '{nombre}' no está declarada en este ámbito"
        ))

    # Regla 3
    def asignar(self, nodo):
        nombre, linea = nodo[2], nodo[1]
        es_constante = self.buscar(nombre)
        if es_constante is None:
            self.globales_vistos.add(nombre)
        elif es_constante:
            self.mensajes.append((
                linea,
                f"Error semántico [Asignación] en la línea {linea}: "
                f"no se puede modificar la constante '{nombre}'"
            ))

    def expresion(self, nodo):
        tipo = nodo[0]
        if tipo == 'variable':
            self.leer(nodo)
        elif tipo == 'indice':
            self.expresion(nodo[2])
            self.expresion(nodo[3])
        elif tipo == 'grupo':
            self.expresion(nodo[2])
        elif tipo == 'unaria':
            self.expresion(nodo[3])
        elif tipo == 'binaria':
            self.expresion(nodo[3])
            self.expresion(nodo[4])
        elif tipo == 'llamada':
            self.expresion(nodo[2])
            self.todas(nodo[3])
        elif tipo == 'metodo':
            self.expresion(nodo[2])
            self.todas(nodo[4])
        elif tipo == 'tabla':
            for clave, valor in nodo[2]:
                if clave is not None:
                    self.expresion(clave)
                self.expresion(valor)
        elif tipo == 'funcion':
            self.funcion(nodo[2], nodo[3])

    def todas(self, expresiones):
        for expresion in expresiones:
            self.expresion(expresion)

    def funcion(self, parametros, cuerpo):
        self.profundidad += 1
        self.ambitos.append({nombre: False for nombre in parametros[0]})
        self.sentencias(cuerpo)
        self.ambitos.pop()
        self.profundidad -= 1

    def bloque(self, sentencias, locales=None):
        self.ambitos.append(dict(locales or {}))
        self.sentencias(sentencias)
        self.ambitos.pop()

    def sentencias(self, sentencias):
        for nodo in sentencias:
            self.sentencia(nodo)

    def sentencia(self, nodo):
        tipo = nodo[0]
        if tipo == 'asignacion':
            variables, expresiones, local = nodo[2], nodo[3], nodo[4]
            self.todas(expresiones)    # primero el lado derecho
            for variable in variables:
                if local:
                    es_constante = (variable[1], variable[2]) in self.constantes
                    self.ambitos[-1][variable[2]] = es_constante
                elif variable[0] == 'variable':
                    self.asignar(variable)
                else:
                    self.expresion(variable)
        elif tipo == 'definir_funcion':
            destino, local = nodo[2], nodo[5]
            if local:
                self.ambitos[-1][destino[2]] = False
            elif destino[0] == 'variable':
                self.asignar(destino)
            else:
                self.expresion(destino)
            self.funcion(nodo[3], nodo[4])
        elif tipo == 'expresion':
            self.expresion(nodo[2])
        elif tipo == 'retorno':
            self.todas(nodo[2])
        elif tipo == 'if':
            for condicion, cuerpo in nodo[2]:
                self.expresion(condicion)
                self.bloque(cuerpo)
            self.bloque(nodo[3])
        elif tipo == 'while':
            self.expresion(nodo[2])
            self.bloque(nodo[3])
        elif tipo == 'repeat':
            # el until puede usar las locales del cuerpo
            self.ambitos.append({})
            self.sentencias(nodo[2])
            self.expresion(nodo[3])
            self.ambitos.pop()
        elif tipo == 'for':
            self.todas(nodo[3:6])
            self.bloque(nodo[6], {nodo[2]: False})
        elif tipo == 'for_generico':
            self.todas(nodo[3])
            self.bloque(nodo[4], {nombre: False for nombre in nodo[2]})


# Devuelve una lista de (linea, mensaje) con los errores de las reglas 1 y 3
def revisar_identificadores_y_constantes(arbol, codigo):
    arbol = arbol or []
    revisor = Revisor(constantes_declaradas(codigo), globales_asignados(arbol))
    revisor.sentencias(arbol)
    return revisor.mensajes
# FIN APORTE SHIRLEY ARAGÓN