from parser import analizar as analizar_sintaxis, pasos_for


# INICIO APORTE ANTHONY SANTANA
# Regla 8: el paso del for numerico no puede ser cero.
# Por ahora reviso pasos literales, con signo y parentesis.
def analizar(codigo):
    errores = analizar_sintaxis(codigo)
    if errores:
        return errores

    for linea, paso in sorted(pasos_for, key=lambda bucle: bucle[0]):
        if paso == 0:
            errores.append(
                f"Error semantico [Estructuras de Control] en la linea {linea}: "
                "el paso del 'for' no puede ser cero."
            )
    return errores
# FIN APORTE ANTHONY SANTANA
