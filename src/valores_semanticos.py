from dataclasses import dataclass
import math
import operator
import re


# INICIO APORTE ANTHONY SANTANA
# Valores que uso al revisar la concatenacion y los controles del for.
@dataclass
class Valor:
    tipo: str
    dato: object = None
    identidad: int = None


def entero_64(numero):
    return (numero + 2 ** 63) % (2 ** 64) - 2 ** 63


def cadena_lua(lexema):
    if lexema.startswith('['):
        ancho = lexema.index('[', 1) + 1
        contenido = lexema[ancho:-ancho]
        contenido = contenido.replace('\r\n', '\n').replace('\n\r', '\n').replace('\r', '\n')
        return contenido.removeprefix('\n').encode('utf-8')

    texto = lexema[1:-1]
    salida = bytearray()
    simples = {'a': 7, 'b': 8, 'f': 12, 'n': 10, 'r': 13, 't': 9, 'v': 11,
               '\\': 92, '"': 34, "'": 39, '\n': 10}
    posicion = 0
    while posicion < len(texto):
        caracter = texto[posicion]
        posicion += 1
        if caracter != '\\':
            salida.extend(caracter.encode('utf-8'))
            continue
        escape = texto[posicion]
        posicion += 1
        if escape in simples:
            salida.append(simples[escape])
        elif escape == 'z':
            while posicion < len(texto) and texto[posicion] in ' \t\r\n\f\v':
                posicion += 1
        elif escape == 'x':
            salida.append(int(texto[posicion:posicion + 2], 16))
            posicion += 2
        elif escape == 'u':
            fin = texto.index('}', posicion)
            salida.extend(chr(int(texto[posicion + 1:fin], 16)).encode('utf-8'))
            posicion = fin + 1
        else:
            fin = posicion
            while fin < min(posicion + 2, len(texto)) and texto[fin].isascii() and texto[fin].isdigit():
                fin += 1
            salida.append(int(escape + texto[posicion:fin]))
            posicion = fin
    return bytes(salida)


DECIMAL = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z')
HEXADECIMAL = re.compile(r'[+-]?0[xX](?:[0-9a-fA-F]+(?:\.[0-9a-fA-F]*)?|\.[0-9a-fA-F]+)(?:[pP][+-]?[0-9]+)?\Z')


def convertir_numero(valor):
    if valor.tipo in ('number', 'error', 'desconocido'):
        return valor
    if valor.tipo != 'string':
        return Valor('error', f'se recibio {valor.tipo}')
    if valor.dato is None:
        return Valor('number')
    try:
        texto = valor.dato.strip(b' \t\r\n\f\v').decode('ascii')
    except UnicodeDecodeError:
        return Valor('error', 'la cadena no representa un numero')
    hexadecimal = HEXADECIMAL.fullmatch(texto)
    if not hexadecimal and not DECIMAL.fullmatch(texto):
        return Valor('error', 'la cadena no representa un numero')
    try:
        if hexadecimal:
            if '.' in texto or 'p' in texto.lower():
                numero = float.fromhex(texto)
            else:
                signo = -1 if texto.startswith('-') else 1
                digitos = texto.lstrip('+-')[2:]
                numero = entero_64(signo * int(digitos[-16:], 16))
        elif '.' not in texto and 'e' not in texto.lower():
            numero = int(texto) if len(texto.lstrip('+-')) <= 19 else float(texto)
            if not -(2 ** 63) <= numero < 2 ** 63:
                numero = float(texto)
        else:
            numero = float(texto)
    except OverflowError:
        numero = -math.inf if texto.startswith('-') else math.inf
    return Valor('number', numero)


def convertir_base(valor, base):
    if valor.tipo == 'desconocido' or base.tipo == 'desconocido':
        return Valor('desconocido')
    if valor.tipo != 'string':
        return Valor('error', 'tonumber con base requiere una cadena')
    base = convertir_numero(base)
    if base.tipo == 'error':
        return base
    if base.dato is None or valor.dato is None:
        return Valor('desconocido')
    if not math.isfinite(base.dato) or int(base.dato) != base.dato or not 2 <= base.dato <= 36:
        return Valor('error', 'la base de tonumber debe estar entre 2 y 36')
    texto = valor.dato.strip(b' \t\r\n\f\v').lower()
    signo = -1 if texto.startswith(b'-') else 1
    digitos = texto[1:] if texto.startswith((b'+', b'-')) else texto
    if not digitos:
        return Valor('nil')
    numero = 0
    alfabeto = b'0123456789abcdefghijklmnopqrstuvwxyz'
    for caracter in digitos:
        digito = alfabeto.find(bytes([caracter]))
        if not 0 <= digito < base.dato:
            return Valor('nil')
        numero = entero_64(numero * int(base.dato) + digito)
    return Valor('number', entero_64(signo * numero))


def literal(nodo):
    _, _, tipo, dato, hexadecimal = nodo
    if tipo == 'STRING':
        try:
            return Valor('string', cadena_lua(dato))
        except (ValueError, UnicodeError):
            return Valor('error', 'cadena con un escape Unicode invalido')
    if tipo in ('TRUE', 'FALSE'):
        return Valor('boolean', tipo == 'TRUE')
    if tipo == 'NIL':
        return Valor('nil')
    if tipo == 'INTEGER':
        if hexadecimal:
            dato = entero_64(dato)
        elif dato >= 2 ** 63:
            try:
                dato = float(dato)
            except OverflowError:
                dato = math.inf
    return Valor('number', dato)


def verdad(valor):
    if valor.tipo in ('desconocido', 'error'):
        return None
    if valor.tipo == 'nil':
        return False
    if valor.tipo == 'boolean':
        return valor.dato
    return True


def unir_valores(primero, segundo):
    if primero.tipo != segundo.tipo:
        return Valor('desconocido')
    if primero.tipo in ('number', 'string', 'boolean', 'nil') and primero.dato == segundo.dato:
        return primero
    return Valor(primero.tipo)


def texto_numero(numero):
    if isinstance(numero, int):
        return str(numero).encode('ascii')
    texto = format(numero, '.14g')
    if math.isfinite(numero) and '.' not in texto and 'e' not in texto:
        texto += '.0'
    return texto.encode('ascii')


OPERACIONES = {'+': operator.add, '-': operator.sub, '*': operator.mul,
               '%': operator.mod, '^': math.pow}


def operacion_numerica(simbolo, izquierdo, derecho=None):
    izquierdo = convertir_numero(izquierdo)
    if izquierdo.tipo in ('error', 'desconocido'):
        return izquierdo
    if derecho is None:
        if izquierdo.dato is None:
            return Valor('number')
        resultado = -izquierdo.dato
    else:
        derecho = convertir_numero(derecho)
        if derecho.tipo in ('error', 'desconocido'):
            return derecho
        if izquierdo.dato is None or derecho.dato is None:
            return Valor('number')
        a, b = izquierdo.dato, derecho.dato
        ambos_enteros = isinstance(a, int) and isinstance(b, int)
        try:
            if simbolo == '/':
                if math.isnan(a) or math.isnan(b):
                    resultado = math.nan
                elif b == 0:
                    resultado = math.nan if a == 0 else math.copysign(math.inf, a * math.copysign(1, b))
                else:
                    resultado = float(a) / float(b)
            elif simbolo == '//':
                if ambos_enteros:
                    if b == 0:
                        return Valor('error', 'division entera por cero')
                    resultado = a // b
                else:
                    division = operacion_numerica('/', izquierdo, derecho).dato
                    resultado = float(math.floor(division)) if math.isfinite(division) else division
            elif simbolo == '%' and b == 0:
                if ambos_enteros:
                    return Valor('error', 'modulo entero por cero')
                resultado = math.nan
            else:
                resultado = OPERACIONES[simbolo](a, b)
        except OverflowError:
            resultado = math.inf
            if a < 0 and simbolo == '^' and math.isfinite(b) and b % 2 == 1:
                resultado = -math.inf
        except ValueError:
            resultado = math.inf if simbolo == '^' and a == 0 and b < 0 else math.nan
            if simbolo == '^' and a == 0 and b < 0 and b % 2 == 1:
                resultado = math.copysign(resultado, a)
    if isinstance(resultado, int):
        resultado = entero_64(resultado)
    return Valor('number', resultado)
# FIN APORTE ANTHONY SANTANA
