from parser import analizar as analizar_sintaxis, pasos_for


# INICIO APORTE ANTHONY SANTANA
# Regla 8: controles numericos y paso distinto de cero en el for.
# Por ahora reviso tipos conocidos de valores literales.
def analizar(codigo):
    errores = analizar_sintaxis(codigo)
    if errores:
        return errores

    for linea, inicio, limite, paso in sorted(pasos_for, key=lambda bucle: bucle[0]):
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
