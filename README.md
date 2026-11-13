# Lua_Grupo5

## Avance 2 de Anthony Santana

Usuario de GitHub `antivsan796`.

Las reglas de Anthony estan en `src/parser.py`, entre los comentarios de inicio
y fin de su aporte. Usan `ply.yacc` y los tokens del lexer del grupo.

Se reconocen asignaciones globales y expresiones con `+`, `-`, `*`, `/`, `//`,
`%` y `^`. Los parentesis cambian la agrupacion. La potencia se agrupa por la
derecha y tiene mayor precedencia que el signo negativo.

Las matrices se escriben como tablas de tablas, por ejemplo `{{1, 2}, {3, 4}}`.
Se puede leer o cambiar un elemento con `matriz[fila][columna]`. Las filas usan
coma o punto y coma como separador y pueden dejar un separador al final.

## Ejecutar las pruebas

Desde la carpeta del repositorio, instalar PLY y ejecutar una prueba.

```sh
python -m pip install -r requirements.txt
python src/main_sintactico.py --archivo prueba_anthony_matrices.lua
python src/main_sintactico.py --archivo prueba_anthony_matrices_error.lua
```

El usuario predeterminado del sintactico es `antivsan796`. Cada ejecucion guarda
un archivo `sintactico-usuario-fecha-hora.txt` en `src/pruebas/resultados/`, con
el archivo analizado y los errores encontrados. Si no hay errores, lo indica.
Cuando se repite una prueba en el mismo minuto, el nombre incluye segundos
y microsegundos para conservar ambos resultados.
