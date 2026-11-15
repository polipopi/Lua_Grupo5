from valores_semanticos import convertir_numero


# INICIO APORTE PAULA BASTIDAS: REGLAS SEMANTICAS 2 Y 4
# Integracion de Anthony: estas comprobaciones reciben los valores resueltos
# del programa, en lugar de depender de la reduccion de las reglas de yacc.
FUNCIONES_PREDEFINIDAS = {
    'print', 'pairs', 'ipairs', 'type', 'tostring',
    'tonumber', 'setmetatable', 'assert', 'error',
    'pcall', 'xpcall', 'require',
}


def revisar_llamada(nombre, valor, linea):
    if valor.tipo not in ('function', 'desconocido', 'error'):
        return (
            f"Error semántico [Identificadores] en la línea {linea}: "
            f"'{nombre}' no es una función"
        )
    return None


def revisar_operacion(simbolo, izquierdo, derecho, linea):
    invalidos = [
        valor.tipo not in ('desconocido', 'error')
        and convertir_numero(valor).tipo == 'error'
        for valor in (izquierdo, derecho)
    ]
    if any(invalidos):
        return (
            f"Error semántico [Operaciones] en la línea {linea}: "
            f"no se puede aplicar '{simbolo}' entre {izquierdo.tipo} y {derecho.tipo}"
        )
    return None
# FIN APORTE PAULA BASTIDAS
