from copy import deepcopy
from contextlib import contextmanager
from dataclasses import dataclass
import math
import operator
import parser as sintactico
from reglas_paula import FUNCIONES_PREDEFINIDAS, revisar_llamada, revisar_operacion
# INICIO APORTE MARLO VALLE: reglas semanticas 6 y 7
from reglas_marlo import cadena_invalida, revisar_breaks, revisar_conversion
# FIN APORTE MARLO VALLE

# INICIO APORTE SHIRLEY ARAGÓN: reglas semanticas 1 y 3
from reglas_shirley import revisar_identificadores_y_constantes
# FIN APORTE SHIRLEY ARAGÓN


from valores_semanticos import (
    Valor, convertir_base, convertir_numero, literal, operacion_numerica,
    texto_numero, unir_valores, verdad,
)


# INICIO APORTE ANTHONY SANTANA
# Mis reglas son 5 (concatenacion) y 8 (for numerico).
# Las comprobaciones 2 y 4 de Paula se mantienen en reglas_paula.py.
SALIDA_BUCLE = object()


class Entorno:
    def __init__(self, padre=None):
        self.padre = padre
        self.valores = {}
        self.varargs = None
        self.desconocidos = False
        self.nivel = 0 if padre is None else padre.nivel + 1

    def propietario(self, nombre):
        entorno = self
        while entorno.padre is not None and nombre not in entorno.valores:
            entorno = entorno.padre
        return entorno

    def leer(self, nombre):
        propietario = self.propietario(nombre)
        faltante = 'desconocido' if propietario.desconocidos else 'nil'
        return propietario.valores.get(nombre, Valor(faltante))


@dataclass
class Funcion:
    parametros: tuple
    cuerpo: list
    entorno: Entorno
    identificador: int


def clave(valor):
    if valor.tipo in ('desconocido', 'error', 'nil') or valor.dato is None:
        return None
    if valor.tipo in ('table', 'function'):
        return (valor.tipo, valor.identidad) if valor.identidad is not None else None
    if valor.tipo == 'number' and isinstance(valor.dato, float) and math.isnan(valor.dato):
        return None
    return (valor.tipo, valor.dato)


def equivalentes(primero, segundo, visitados=None):
    if primero.tipo != segundo.tipo:
        return False
    if primero.tipo in ('table', 'function') and primero.identidad != segundo.identidad:
        return False
    if primero.tipo == 'function':
        if primero.identidad is not None:
            return True
        return primero.dato == segundo.dato
    if primero.tipo != 'table' or primero.dato is None or segundo.dato is None:
        return primero.dato == segundo.dato
    visitados = set() if visitados is None else visitados
    par = (id(primero.dato), id(segundo.dato))
    if par in visitados:
        return True
    visitados.add(par)
    return primero.dato.keys() == segundo.dato.keys() and all(
        equivalentes(valor, segundo.dato[nombre], visitados)
        for nombre, valor in primero.dato.items()
    )


class Analizador:
    def __init__(self):
        self.errores = {}
        self.profundidad = 0
        self.funciones_revisadas = set()
        self.retornos = [[]]
        self.secuencia = 0
        self.iteraciones = 256
        self.bucles = []
        # INICIO APORTE MARLO VALLE: metatablas de las clases
        self.metatablas = {}
        # FIN APORTE MARLO VALLE

    @contextmanager
    def contexto_bucle(self, entorno):
        salidas = []
        self.bucles.append((entorno.nivel, salidas))
        try:
            yield salidas
        finally:
            self.bucles.pop()

    def interrumpir_bucle(self, entorno):
        if not self.bucles:
            return None
        nivel, salidas = self.bucles[-1]
        while entorno.nivel > nivel:
            entorno = entorno.padre
        salidas.append(deepcopy(entorno))
        return SALIDA_BUCLE

    def objeto(self, tipo, dato):
        self.secuencia += 1
        return Valor(tipo, dato, self.secuencia)

    def error(self, linea, categoria, mensaje):
        self.errores[(linea, categoria, mensaje)] = (
            f'Error semantico [{categoria}] en la linea {linea}: {mensaje}'
        )

    def error_paula(self, linea, mensaje):
        if mensaje is not None:
            self.errores[(linea, 'Paula', mensaje)] = mensaje

    # INICIO APORTE MARLO VALLE
    def error_marlo(self, linea, mensajes):
        for mensaje in mensajes:
            self.errores[(linea, 'Marlo', mensaje)] = mensaje
    # FIN APORTE MARLO VALLE

    def nombre_llamada(self, nodo):
        if nodo[0] == 'variable':
            return nodo[2]
        if nodo[0] == 'indice' and nodo[3][0] == 'literal':
            indice = literal(nodo[3])
            if indice.tipo == 'string' and indice.dato is not None:
                return self.nombre_llamada(nodo[2]) + '.' + indice.dato.decode('utf-8', errors='replace')
        return 'valor'

    def lista(self, expresiones, entorno):
        valores = []
        for indice, expresion in enumerate(expresiones):
            if indice == len(expresiones) - 1 and expresion[0] in ('llamada', 'metodo', 'varargs'):
                valores.extend(self.resultados(expresion, entorno))
            else:
                valores.append(self.expresion(expresion, entorno))
        return valores

    def resultados(self, nodo, entorno):
        if nodo[0] == 'varargs':
            actual = entorno
            while actual.varargs is None and actual.padre is not None:
                actual = actual.padre
            return actual.varargs if actual.varargs is not None else [Valor('desconocido')]
        if nodo[0] == 'metodo':
            receptor = self.expresion(nodo[2], entorno)
            funcion = self.elemento(receptor, Valor('string', nodo[3].encode('utf-8')))
            argumentos = [receptor] + self.lista(nodo[4], entorno)
        else:
            funcion = self.expresion(nodo[2], entorno)
            argumentos = self.lista(nodo[3], entorno)
        nombre = nodo[3] if nodo[0] == 'metodo' else self.nombre_llamada(nodo[2])
        self.error_paula(nodo[1], revisar_llamada(nombre, funcion, nodo[1]))
        if funcion.tipo != 'function' or funcion.dato is None:
            return [Valor('desconocido')]
        if isinstance(funcion.dato, str):
            return self.incorporada(funcion.dato, argumentos)
        if self.profundidad >= 12:
            return [Valor('desconocido')]
        return self.llamar(funcion.dato, argumentos)

    def elemento(self, tabla, indice):
        llave = clave(indice)
        if tabla.tipo != 'table' or tabla.dato is None or llave is None:
            return Valor('desconocido')
        # INICIO APORTE MARLO VALLE: busqueda en la clase con __index
        if llave not in tabla.dato and tabla.identidad in self.metatablas:
            return self.heredado(tabla, llave, set())
        # FIN APORTE MARLO VALLE
        return tabla.dato.get(llave, Valor('nil'))

    # INICIO APORTE MARLO VALLE: CLASES CON METATABLAS
    # obj = setmetatable({}, Clase) con Clase.__index = Clase hace que
    # obj:metodo() busque el metodo en Clase. Si la busqueda no se puede
    # completar se devuelve desconocido para no reportar errores falsos.
    def heredado(self, tabla, llave, visitados):
        meta = self.metatablas.get(tabla.identidad)
        if meta is None or meta.tipo != 'table' or meta.dato is None:
            return Valor('desconocido')
        clase = meta.dato.get(('string', b'__index'))
        if clase is None or clase.tipo != 'table' or clase.dato is None:
            return Valor('desconocido')
        if llave in clase.dato:
            return clase.dato[llave]
        if clase.identidad in visitados or clase.identidad not in self.metatablas:
            return Valor('desconocido')
        visitados.add(clase.identidad)
        return self.heredado(clase, llave, visitados)
    # FIN APORTE MARLO VALLE

    def tabla(self, campos, entorno):
        contenido = {}
        posicion = 1
        for indice, (nombre, expresion) in enumerate(campos):
            if nombre is not None:
                llave = clave(self.expresion(nombre, entorno))
                valor = self.expresion(expresion, entorno)
                if llave is None:
                    contenido = None
                elif contenido is not None:
                    if valor.tipo == 'nil':
                        contenido.pop(llave, None)
                    else:
                        contenido[llave] = valor
                continue
            valores = self.lista([expresion], entorno) if indice == len(campos) - 1 else [self.expresion(expresion, entorno)]
            if expresion[0] in ('varargs', 'llamada', 'metodo') and valores and valores[-1].tipo == 'desconocido':
                contenido = None
            for valor in valores:
                if contenido is not None and valor.tipo != 'nil':
                    contenido[('number', posicion)] = valor
                posicion += 1
        return self.objeto('table', contenido)

    def longitud(self, valor):
        if valor.tipo == 'desconocido':
            return Valor('number')
        if valor.tipo == 'error':
            return valor
        if valor.tipo == 'string':
            return Valor('number', len(valor.dato) if valor.dato is not None else None)
        if valor.tipo != 'table':
            return Valor('error', f'no se puede obtener la longitud de {valor.tipo}')
        if valor.dato is None:
            return Valor('number')
        posicion = 1
        while ('number', posicion) in valor.dato:
            if valor.dato[('number', posicion)].tipo == 'desconocido':
                return Valor('number')
            posicion += 1
        if any(tipo == 'number' and numero >= posicion for tipo, numero in valor.dato):
            return Valor('number')
        return Valor('number', posicion - 1)

    def concatenar(self, nodo, izquierdo, derecho):
        invalido = False
        for lado, valor in (('izquierdo', izquierdo), ('derecho', derecho)):
            if valor.tipo == 'error':
                self.error(nodo[1], 'Operaciones', f'no se pudo calcular el operando {lado} de la concatenacion: {valor.dato}.')
                invalido = True
            elif valor.tipo not in ('number', 'string', 'desconocido'):
                self.error(nodo[1], 'Operaciones', f'no se puede concatenar un valor {valor.tipo} (operando {lado}).')
                invalido = True
        if invalido:
            return Valor('desconocido')
        if izquierdo.dato is None or derecho.dato is None:
            return Valor('string')
        primero = texto_numero(izquierdo.dato) if izquierdo.tipo == 'number' else izquierdo.dato
        segundo = texto_numero(derecho.dato) if derecho.tipo == 'number' else derecho.dato
        return Valor('string', primero + segundo)

    def expresion(self, nodo, entorno):
        tipo = nodo[0]
        if tipo == 'literal':
            return literal(nodo)
        if tipo == 'variable':
            return entorno.leer(nodo[2])
        if tipo == 'indice':
            return self.elemento(self.expresion(nodo[2], entorno), self.expresion(nodo[3], entorno))
        if tipo == 'grupo':
            return self.expresion(nodo[2], entorno)
        if tipo in ('llamada', 'metodo', 'varargs'):
            valores = self.resultados(nodo, entorno)
            return valores[0] if valores else Valor('nil')
        if tipo == 'tabla':
            return self.tabla(nodo[2], entorno)
        if tipo == 'funcion':
            funcion = Funcion(nodo[2], nodo[3], entorno, id(nodo))
            self.revisar_funcion(funcion)
            return self.objeto('function', funcion)
        if tipo == 'unaria':
            valor = self.expresion(nodo[3], entorno)
            if valor.tipo == 'error':
                return valor
            if nodo[2] == '-':
                # INICIO APORTE MARLO VALLE: regla 6 en el menos unario ("diez" negado)
                self.error_marlo(nodo[1], revisar_conversion((valor,), nodo[1]))
                # FIN APORTE MARLO VALLE
                return operacion_numerica('-', valor)
            if nodo[2] == '#':
                return self.longitud(valor)
            condicion = verdad(valor)
            return Valor('boolean', None if condicion is None else not condicion)
        simbolo = nodo[2]
        izquierdo = self.expresion(nodo[3], entorno)
        if simbolo in ('and', 'or') and izquierdo.tipo == 'error':
            return izquierdo
        condicion = verdad(izquierdo)
        if (simbolo == 'and' and condicion is False) or (simbolo == 'or' and condicion is True):
            return izquierdo
        if simbolo in ('and', 'or') and condicion is None:
            antes = deepcopy(entorno)
            rama = deepcopy(entorno)
            derecho = self.expresion(nodo[4], rama)
            self.unir_entornos(entorno, [antes, rama])
            return unir_valores(izquierdo, derecho)
        derecho = self.expresion(nodo[4], entorno)
        if simbolo in ('and', 'or'):
            return derecho
        if simbolo == '..':
            return self.concatenar(nodo, izquierdo, derecho)
        if simbolo in ('+', '-', '*', '/', '//', '%', '^'):
            # INICIO APORTE MARLO VALLE: regla 6
            # Las cadenas que no son numerales se reportan como error de
            # conversion; la regla 4 queda para nil, boolean y table.
            conversiones = revisar_conversion((izquierdo, derecho), nodo[1])
            self.error_marlo(nodo[1], conversiones)
            otro_invalido = any(
                not cadena_invalida(valor)
                and valor.tipo not in ('desconocido', 'error')
                and convertir_numero(valor).tipo == 'error'
                for valor in (izquierdo, derecho)
            )
            if not conversiones or otro_invalido:
                self.error_paula(nodo[1], revisar_operacion(simbolo, izquierdo, derecho, nodo[1]))
            # FIN APORTE MARLO VALLE
            return operacion_numerica(simbolo, izquierdo, derecho)
        if izquierdo.tipo == 'error':
            return izquierdo
        if derecho.tipo == 'error':
            return derecho
        if 'desconocido' in (izquierdo.tipo, derecho.tipo):
            return Valor('boolean')
        if simbolo in ('==', '~=') and izquierdo.tipo != derecho.tipo:
            return Valor('boolean', simbolo == '~=')
        if izquierdo.dato is None or derecho.dato is None:
            if izquierdo.tipo == derecho.tipo == 'nil':
                return Valor('boolean', simbolo == '==')
            return Valor('boolean')
        if simbolo in ('==', '~=') and izquierdo.tipo in ('table', 'function'):
            if izquierdo.identidad is None or derecho.identidad is None:
                return Valor('boolean')
            iguales = izquierdo.identidad == derecho.identidad
            return Valor('boolean', iguales if simbolo == '==' else not iguales)
        operaciones = {'==': operator.eq, '~=': operator.ne, '<': operator.lt,
                       '<=': operator.le, '>': operator.gt, '>=': operator.ge}
        try:
            return Valor('boolean', operaciones[simbolo](izquierdo.dato, derecho.dato))
        except TypeError:
            return Valor('error', 'comparacion entre tipos incompatibles')

    def destino(self, variable, entorno):
        if variable[0] == 'variable':
            return (entorno.propietario(variable[2]).valores, variable[2])
        tabla = self.expresion(variable[2], entorno)
        indice = clave(self.expresion(variable[3], entorno))
        if tabla.tipo != 'table' or tabla.dato is None:
            return (None, None)
        if indice is None:
            tabla.dato = None
            return (None, None)
        return (tabla.dato, indice)

    def asignar(self, nodo, entorno):
        variables, expresiones, local = nodo[2:]
        destinos = [(entorno.valores, variable[2]) for variable in variables] if local else [
            self.destino(variable, entorno) for variable in variables
        ]
        valores = self.lista(expresiones, entorno.padre if local else entorno)
        varios = bool(expresiones and expresiones[-1][0] in ('llamada', 'metodo', 'varargs')
                      and valores and valores[-1].tipo == 'desconocido')
        for indice, (contenedor, nombre) in enumerate(destinos):
            if contenedor is not None:
                valor = valores[indice] if indice < len(valores) else Valor('desconocido' if varios else 'nil')
                if isinstance(nombre, tuple) and valor.tipo == 'nil':
                    contenedor.pop(nombre, None)
                else:
                    contenedor[nombre] = valor

    def unir_entornos(self, destino, fuentes):
        actual = destino
        copias = list(fuentes)
        while actual is not None:
            nombres = set(actual.valores)
            for copia in copias:
                nombres.update(copia.valores)
            for nombre in nombres:
                valores = [copia.valores.get(nombre, Valor('nil')) for copia in copias]
                valor = valores[0]
                for otro in valores[1:]:
                    if not equivalentes(valor, otro):
                        valor = unir_valores(valor, otro)
                anterior = actual.valores.get(nombre, Valor('nil'))
                actual.valores[nombre] = anterior if equivalentes(anterior, valor) else valor
            actual = actual.padre
            copias = [copia.padre for copia in copias]

    def condicion(self, nodo, entorno):
        restantes = deepcopy(entorno)
        salidas = []
        retornos = []
        interrumpido = False
        for condicion, cuerpo in nodo[2]:
            valor = verdad(self.expresion(condicion, restantes))
            if valor is not False:
                rama = deepcopy(restantes)
                retorno = self.bloque(cuerpo, Entorno(rama))
                if retorno is None:
                    salidas.append(rama)
                elif retorno is SALIDA_BUCLE:
                    interrumpido = True
                else:
                    retornos.append(retorno)
            if valor is True:
                break
        else:
            retorno = self.bloque(nodo[3], Entorno(restantes))
            if retorno is None:
                salidas.append(restantes)
            elif retorno is SALIDA_BUCLE:
                interrumpido = True
            else:
                retornos.append(retorno)
        if salidas:
            self.unir_entornos(entorno, salidas)
            return None
        return SALIDA_BUCLE if interrumpido else self.unir_retornos(retornos)

    def bucle(self, cuerpo, entorno, variables, puede_omitirse):
        with self.contexto_bucle(entorno) as salidas:
            antes = deepcopy(entorno)
            primera = deepcopy(entorno)
            ambito = Entorno(primera)
            ambito.valores.update(variables)
            retorno = self.bloque(cuerpo, ambito)
            if retorno is not None:
                if retorno is not SALIDA_BUCLE and not puede_omitirse and not salidas:
                    return retorno
                if puede_omitirse:
                    salidas.append(antes)
                self.unir_entornos(entorno, salidas)
                return None
            entrada = deepcopy(antes)
            self.unir_entornos(entrada, [antes, primera])
            repeticion = Entorno(entrada)
            repeticion.valores.update(variables)
            retorno = self.bloque(cuerpo, repeticion)
            fuentes = salidas + [primera]
            if retorno is None:
                fuentes.append(entrada)
            if puede_omitirse:
                fuentes.append(antes)
            self.unir_entornos(entorno, fuentes)
            return None

    def repetir(self, nodo, entorno):
        with self.contexto_bucle(entorno) as salidas:
            ambito = Entorno(entorno)
            retorno = self.bloque(nodo[2], ambito)
            if retorno is None:
                if verdad(self.expresion(nodo[3], ambito)) is not True:
                    self.bucle(nodo[2], entorno, {}, True)
                salidas.append(deepcopy(entorno))
            if salidas:
                self.unir_entornos(entorno, salidas)
                return None
            return retorno

    def for_numerico(self, nodo, entorno):
        controles = [self.expresion(expresion, entorno) for expresion in nodo[3:6]]
        numeros = []
        for nombre, valor in zip(('inicio', 'limite', 'paso'), controles):
            numero = convertir_numero(valor)
            numeros.append(numero)
            if numero.tipo == 'error':
                self.error(nodo[1], 'Estructuras de Control', f"el {nombre} del 'for' debe ser numerico: {numero.dato}.")
        inicio, limite, paso = numeros
        if paso.tipo == 'number' and paso.dato == 0:
            self.error(nodo[1], 'Estructuras de Control', "el paso del 'for' no puede ser cero.")
        conocidos = all(valor.tipo == 'number' and valor.dato is not None for valor in numeros)
        puede_omitirse = True
        if conocidos and paso.dato != 0:
            entra = inicio.dato <= limite.dato if paso.dato > 0 else inicio.dato >= limite.dato
            if not entra:
                return None
            puede_omitirse = False
            enteros = (controles[0].tipo == controles[2].tipo == 'number'
                       and isinstance(controles[0].dato, int) and isinstance(controles[2].dato, int))
            valores = self.valores_for(inicio.dato, limite.dato, paso.dato, enteros)
            if valores is not None:
                self.iteraciones -= len(valores)
                with self.contexto_bucle(entorno) as salidas:
                    retorno = None
                    for valor in valores:
                        ambito = Entorno(entorno)
                        ambito.valores[nodo[2]] = Valor('number', valor)
                        retorno = self.bloque(nodo[6], ambito)
                        if retorno is not None:
                            break
                    if retorno is None:
                        salidas.append(deepcopy(entorno))
                    if salidas:
                        self.unir_entornos(entorno, salidas)
                        return None
                    return retorno
        return self.bucle(nodo[6], entorno, {nodo[2]: Valor('number')}, puede_omitirse)

    def valores_for(self, inicio, limite, paso, enteros):
        valores = []
        actual = inicio if enteros else float(inicio)
        while (actual <= limite if paso > 0 else actual >= limite):
            if len(valores) >= self.iteraciones:
                return None
            valores.append(actual)
            siguiente = actual + paso
            if enteros and not -(2 ** 63) <= siguiente < 2 ** 63:
                break
            if siguiente == actual:
                return None
            actual = siguiente
        return valores

    def unir_retornos(self, retornos):
        if not retornos:
            return []
        salida = []
        for indice in range(max(map(len, retornos))):
            valores = [retorno[indice] if indice < len(retorno) else Valor('nil') for retorno in retornos]
            valor = valores[0]
            for otro in valores[1:]:
                valor = valor if equivalentes(valor, otro) else unir_valores(valor, otro)
            salida.append(valor)
        return salida

    def llamar(self, funcion, argumentos):
        self.profundidad += 1
        nombres, variable = funcion.parametros
        entorno = Entorno(funcion.entorno)
        for indice, nombre in enumerate(nombres):
            faltante = 'desconocido' if argumentos and argumentos[-1].tipo == 'desconocido' else 'nil'
            entorno.valores[nombre] = argumentos[indice] if indice < len(argumentos) else Valor(faltante)
        entorno.varargs = argumentos[len(nombres):] if variable else []
        self.retornos.append([])
        bucles_exteriores = self.bucles
        self.bucles = []
        try:
            if self.bloque(funcion.cuerpo, entorno) is None:
                self.retornos[-1].append([])
            return self.unir_retornos(self.retornos[-1])
        finally:
            self.bucles = bucles_exteriores
            self.retornos.pop()
            self.profundidad -= 1

    def revisar_funcion(self, funcion):
        if funcion.identificador in self.funciones_revisadas:
            return
        self.funciones_revisadas.add(funcion.identificador)
        exterior = deepcopy(funcion.entorno)
        actual = exterior
        while actual is not None:
            actual.desconocidos = True
            for nombre, valor in actual.valores.items():
                if not (valor.tipo == 'function' and isinstance(valor.dato, str)):
                    actual.valores[nombre] = Valor('desconocido')
            actual = actual.padre
        parametros = [Valor('desconocido')] * len(funcion.parametros[0])
        if funcion.parametros[1]:
            parametros.append(Valor('desconocido'))
        copia = Funcion(funcion.parametros, funcion.cuerpo, exterior, funcion.identificador)
        presupuesto = self.iteraciones
        try:
            self.llamar(copia, parametros)
        finally:
            self.iteraciones = presupuesto

    def bloque(self, sentencias, entorno):
        for nodo in sentencias:
            tipo = nodo[0]
            retorno = None
            if (tipo == 'asignacion' and nodo[4]) or (tipo == 'definir_funcion' and nodo[5]):
                # Una nueva declaracion local no reemplaza el valor capturado por una funcion anterior.
                entorno = Entorno(entorno)
            if tipo == 'asignacion':
                self.asignar(nodo, entorno)
            elif tipo == 'expresion':
                self.expresion(nodo[2], entorno)
            elif tipo == 'retorno':
                retorno = self.lista(nodo[2], entorno)
                self.retornos[-1].append(retorno)
            elif tipo == 'break':
                return self.interrumpir_bucle(entorno)
            elif tipo == 'definir_funcion':
                funcion = Funcion(nodo[3], nodo[4], entorno, id(nodo))
                valor = self.objeto('function', funcion)
                if nodo[5]:
                    entorno.valores[nodo[2][2]] = valor
                else:
                    contenedor, nombre = self.destino(nodo[2], entorno)
                    if contenedor is not None:
                        contenedor[nombre] = valor
                self.revisar_funcion(funcion)
            elif tipo == 'if':
                retorno = self.condicion(nodo, entorno)
            elif tipo == 'for':
                retorno = self.for_numerico(nodo, entorno)
            elif tipo == 'for_generico':
                self.lista(nodo[3], entorno)
                retorno = self.bucle(nodo[4], entorno, {nombre: Valor('desconocido') for nombre in nodo[2]}, True)
            elif tipo == 'while':
                condicion = verdad(self.expresion(nodo[2], entorno))
                if condicion is not False:
                    retorno = self.bucle(nodo[3], entorno, {}, condicion is None)
            elif tipo == 'repeat':
                retorno = self.repetir(nodo, entorno)
            if retorno is not None:
                return retorno
        return None

    def incorporada(self, nombre, argumentos):
        primero = argumentos[0] if argumentos else Valor('nil')
        if nombre == 'tonumber':
            if len(argumentos) > 1 and argumentos[1].tipo != 'nil':
                return [convertir_base(primero, argumentos[1])]
            numero = convertir_numero(primero)
            return [Valor('nil') if numero.tipo == 'error' else numero]
        if nombre == 'tostring':
            if primero.tipo == 'string':
                return [primero]
            if primero.tipo == 'number' and primero.dato is not None:
                return [Valor('string', texto_numero(primero.dato))]
            if primero.tipo == 'nil':
                return [Valor('string', b'nil')]
            if primero.tipo == 'boolean' and primero.dato is not None:
                return [Valor('string', b'true' if primero.dato else b'false')]
            return [Valor('string')]
        if nombre == 'type':
            dato = primero.tipo.encode('ascii') if primero.tipo != 'desconocido' else None
            return [Valor('string', dato)]
        if nombre == 'setmetatable':
            # INICIO APORTE MARLO VALLE: se guarda la clase del objeto
            if primero.tipo == 'table' and primero.identidad is not None and len(argumentos) > 1:
                self.metatablas[primero.identidad] = argumentos[1]
            # FIN APORTE MARLO VALLE
            return [primero]
        if nombre in ('print', 'io.write'):
            return []
        if nombre == 'io.read':
            return [Valor('desconocido') for _ in range(max(1, len(argumentos)))]
        if nombre == 'table.pack':
            campos = {('number', indice): valor for indice, valor in enumerate(argumentos, 1) if valor.tipo != 'nil'}
            campos[('string', b'n')] = Valor('number', len(argumentos))
            return [self.objeto('table', campos)]
        if nombre == 'table.unpack' and primero.tipo == 'table' and primero.dato is not None:
            longitud = self.longitud(primero).dato
            if longitud is not None:
                return [primero.dato[('number', indice)] for indice in range(1, longitud + 1)]
        return [Valor('desconocido')]

    def entorno_inicial(self):
        entorno = Entorno()
        for nombre in FUNCIONES_PREDEFINIDAS:
            entorno.valores[nombre] = Valor('function', nombre)
        for modulo, funciones in {'io': ('read', 'write'), 'table': ('pack', 'unpack')}.items():
            entorno.valores[modulo] = self.objeto('table', {
                ('string', funcion.encode('ascii')): Valor('function', f'{modulo}.{funcion}')
                for funcion in funciones
            })
        return entorno


def analizar(codigo):
    errores = sintactico.analizar(codigo)
    if errores:
        return errores
    analizador = Analizador()
    analizador.bloque(sintactico.arbol, analizador.entorno_inicial())
    # INICIO APORTE MARLO VALLE: regla 7, se revisa la estructura del arbol
    for linea, mensaje in revisar_breaks(sintactico.arbol):
        analizador.error_marlo(linea, [mensaje])
    # FIN APORTE MARLO VALLE
    
    # INICIO APORTE SHIRLEY ARAGÓN: reglas 1 (identificadores) y 3 (constantes)
    for linea, mensaje in revisar_identificadores_y_constantes(sintactico.arbol, codigo):
        analizador.errores[(linea, 'Shirley', mensaje)] = mensaje
    # FIN APORTE SHIRLEY ARAGÓN
    return [mensaje for _, mensaje in sorted(analizador.errores.items())]

def calcular_constante(expresion):
    # Entrada usada por las pruebas de operaciones de los avances anteriores.
    if not isinstance(expresion, tuple):
        return expresion
    if expresion[0] in ('+', '-', '*', '/', '//', '%', '^', 'negativo'):
        izquierdo = calcular_constante(expresion[1])
        primero = Valor('number', izquierdo) if isinstance(izquierdo, (int, float)) else Valor('desconocido')
        if expresion[0] == 'negativo':
            resultado = operacion_numerica('-', primero)
        else:
            derecho = calcular_constante(expresion[2])
            segundo = Valor('number', derecho) if isinstance(derecho, (int, float)) else Valor('desconocido')
            resultado = operacion_numerica(expresion[0], primero, segundo)
    else:
        analizador = Analizador()
        resultado = analizador.expresion(expresion, analizador.entorno_inicial())
    return resultado.dato if resultado.tipo == 'number' else None
# FIN APORTE ANTHONY SANTANA
