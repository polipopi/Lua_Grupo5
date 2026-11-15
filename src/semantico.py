import math
import operator
from parser import analizar as analizar_sintaxis, pasos_for


# INICIO APORTE ANTHONY SANTANA
# Regla 8: controles numericos y paso distinto de cero en el for.
# Calculo las operaciones que tienen solo numeros como operandos.
OPERACIONES = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '//': operator.floordiv,
    '%': operator.mod,
    '^': math.pow,
}


def calcular_constante(expresion):
    if not isinstance(expresion, tuple):
        return expresion

    izquierdo = calcular_constante(expresion[1])
    if not isinstance(izquierdo, (int, float)):
        return None

    try:
        if expresion[0] == 'negativo':
            resultado = -izquierdo
        else:
            derecho = calcular_constante(expresion[2])
            if not isinstance(derecho, (int, float)):
                return None
            simbolo = expresion[0]
            if simbolo == '/':
                resultado = float(izquierdo) / float(derecho)
            elif simbolo == '//' and (isinstance(izquierdo, float) or isinstance(derecho, float)):
                # En Lua se redondea hacia abajo el resultado de la division.
                resultado = float(math.floor(float(izquierdo) / float(derecho)))
            else:
                resultado = OPERACIONES[simbolo](izquierdo, derecho)
    except (ArithmeticError, ValueError):
        return None

    if isinstance(resultado, int):
        # Los resultados enteros de Lua usan 64 bits con signo.
        resultado = (resultado + 2 ** 63) % (2 ** 64) - 2 ** 63
    return resultado


def analizar(codigo):
    errores = analizar_sintaxis(codigo)
    if errores:
        return errores

    for linea, inicio, limite, paso in sorted(pasos_for, key=lambda bucle: bucle[0]):
        inicio = calcular_constante(inicio)
        limite = calcular_constante(limite)
        paso = calcular_constante(paso)
        for nombre, valor in (('inicio', inicio), ('limite', limite), ('paso', paso)):
            if isinstance(valor, str):
                errores.append(
                    f"Error semantico [Estructuras de Control] en la linea {linea}: "
                    f"el {nombre} del 'for' debe ser numerico, se recibio {valor}."
                )
        if paso == 0:
            errores.append(
                f"Error semantico [Estructuras de Control] en la linea {linea}: "
                "el paso del 'for' no puede ser cero."
            )
    return errores
# FIN APORTE ANTHONY SANTANA
