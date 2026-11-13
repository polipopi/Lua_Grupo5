# Lua_Grupo5

## Avance 2 de Anthony Santana

Usuario de GitHub `antivsan796`.

Las reglas de Anthony están en `src/parser.py`, entre los comentarios de inicio
y fin de su aporte. Usan `ply.yacc` y los tokens del lexer del grupo.

Se reconocen asignaciones globales y expresiones con `+`, `-`, `*`, `/`, `//`,
`%` y `^`. Los paréntesis cambian la agrupación. La potencia se agrupa por la
derecha y tiene mayor precedencia que el signo negativo.

Las matrices se escriben como tablas de tablas, por ejemplo `{{1, 2}, {3, 4}}`.
Se puede leer o cambiar un elemento con `matriz[fila][columna]`. Las filas usan
coma o punto y coma como separador y pueden dejar un separador al final.

El `for` numérico acepta `for i = inicio, limite do ... end` y la variante
con paso, `for i = inicio, limite, paso do ... end`. Se pueden anidar bucles.
El operador `#` permite usar la cantidad de filas o columnas como límite.

Las funciones de Anthony reciben una cantidad variable de argumentos con `...`.
Se acepta `function promedio(...) ... end` o una lista de parámetros fijos
seguida de los puntos, como `function sumar(factor, ...) ... end`.
Los valores se pueden guardar en una tabla con `{...}`. Las llamadas aceptan
cero o más argumentos y se pueden usar dentro de una expresión.

Se agregaron `return` y la sintaxis de llamada como apoyo para probar estas
funciones. El retorno va al final del bloque. Las asignaciones también aceptan
los literales de cadenas, booleanos y `nil` que ya reconoce el lexer, tablas
y referencias a funciones.

Este aporte corresponde a las reglas sintácticas asignadas a Anthony en la
página 17 de la propuesta del proyecto. La validación revisa la escritura del
programa. Las comprobaciones de tipos, valores y alcance pertenecen al avance 3.

## Ejecutar las pruebas

Desde la carpeta del repositorio, instalar PLY y ejecutar una prueba.

```sh
python -m pip install -r requirements.txt
python src/main_sintactico.py
```

Sin argumentos se analiza `prueba_anthony_completo.lua`, que suma una matriz
con bucles anidados y calcula el promedio con una función de n argumentos.
El analizador muestra los errores y guarda el log. Para elegir otro archivo,
usar `--archivo`.

```sh
python src/main_sintactico.py --archivo prueba_anthony_matrices.lua
python src/main_sintactico.py --archivo prueba_anthony_matrices_error.lua
python src/main_sintactico.py --archivo prueba_anthony_for.lua
python src/main_sintactico.py --archivo prueba_anthony_for_error.lua
python src/main_sintactico.py --archivo prueba_anthony_funciones.lua
python src/main_sintactico.py --archivo prueba_anthony_funciones_error.lua
```

El usuario predeterminado del sintáctico es `antivsan796`. Cada ejecución guarda
un archivo `sintactico-usuario-fecha-hora.txt` en `src/pruebas/resultados/`, con
el archivo analizado y los errores encontrados. Si no hay errores, lo indica.
Cuando se repite una prueba en el mismo minuto, el nombre incluye segundos
y microsegundos para conservar ambos resultados.

Las pruebas con sufijo `_error` tienen un error puesto a propósito. La de
matrices deja un indice sin cerrar, la del `for` omite `do` y la de funciones
coloca un parámetro después de `...`. La prueba aritmética inicial también
conserva su version con una suma incompleta.

PLY puede mostrar avisos de tokens que todavía no tienen reglas en este
parser. La lista de tokens se comparte con los demás integrantes.

El análisis léxico se puede ejecutar por separado con `python src/main.py`.
Para la prueba léxica de Anthony, usar
`python src/main.py --usuario antivsan796 --archivo prueba_anthony.lua`.

Las reglas siguen el [manual de Lua 5.4](https://www.lua.org/manual/5.4/manual.html#9)
y la [documentación de PLY](https://ply.readthedocs.io/en/latest/ply.html#yacc).
