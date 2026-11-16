from valores_semanticos import convertir_numero


# INICIO APORTE MARLO VALLE: REGLAS SEMANTICAS 6 Y 7

# =====================================================
# REGLA 6: CONVERSION DE CADENA A NUMERO
# =====================================================
# En una operacion aritmetica Lua convierte una cadena a numero
# solo si la cadena representa un numeral de Lua:
#   local a = "10" + 5      -- valido: 15
#   local b = "diez" + 5    -- invalido
# La conversion explicita se hace con tonumber y tostring.

def cadena_invalida(valor):
    # Solo se revisan cadenas con contenido conocido; si la cadena
    # viene de io.read u otra fuente desconocida no se puede saber.
    return (
        valor.tipo == 'string'
        and valor.dato is not None
        and convertir_numero(valor).tipo == 'error'
    )


def revisar_conversion(operandos, linea):
    mensajes = []
    for valor in operandos:
        if cadena_invalida(valor):
            texto = valor.dato.decode('utf-8', errors='replace')
            mensajes.append(
                f"Error semántico [Conversión] en la línea {linea}: "
                f"la cadena \"{texto}\" no puede convertirse a número"
            )
    return mensajes


# =====================================================
# REGLA 7: BREAK SOLO DENTRO DE UN BUCLE
# =====================================================
# break solo puede aparecer dentro de while, for o repeat y
# termina el bucle mas interno:
#   if x > 0 then
#       break             -- invalido: no hay bucle
#   end
# El cuerpo de una funcion empieza fuera de cualquier bucle,
# aunque la funcion se declare dentro de uno.

BUCLES = {
    # tipo de nodo: (posiciones del cuerpo, posiciones de expresiones)
    'while': ((3,), (2,)),
    'repeat': ((2,), (3,)),
    'for': ((6,), (3, 4, 5)),
    'for_generico': ((4,), (3,)),
}


def revisar_break(nodo, dentro_bucle, mensajes):
    if isinstance(nodo, list):
        for elemento in nodo:
            revisar_break(elemento, dentro_bucle, mensajes)
        return
    if not isinstance(nodo, tuple) or not nodo:
        return

    tipo = nodo[0]
    if not isinstance(tipo, str):
        # Pares como (condicion, bloque) de un if o campos de tabla.
        for elemento in nodo:
            revisar_break(elemento, dentro_bucle, mensajes)
        return

    if tipo == 'break':
        if not dentro_bucle:
            mensajes.append((
                nodo[1],
                f"Error semántico [Estructuras de Control] en la línea {nodo[1]}: "
                f"'break' fuera de un bucle"
            ))
    elif tipo in BUCLES:
        cuerpos, expresiones = BUCLES[tipo]
        for posicion in expresiones:
            revisar_break(nodo[posicion], dentro_bucle, mensajes)
        for posicion in cuerpos:
            revisar_break(nodo[posicion], True, mensajes)
    elif tipo == 'funcion':
        revisar_break(nodo[3], False, mensajes)
    elif tipo == 'definir_funcion':
        revisar_break(nodo[4], False, mensajes)
    else:
        for elemento in nodo[1:]:
            revisar_break(elemento, dentro_bucle, mensajes)


# Devuelve pares (linea, mensaje) de cada break fuera de un bucle.
def revisar_breaks(arbol):
    mensajes = []
    revisar_break(arbol or [], False, mensajes)
    return mensajes

# FIN APORTE MARLO VALLE
