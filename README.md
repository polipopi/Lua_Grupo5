# Lua_Grupo5

Mi usuario de GitHub es `antivsan796`.

Para instalar PLY uso este comando desde la carpeta del repositorio.

```sh
python -m pip install -r requirements.txt
```

## Avance 1, léxico

Mi parte fue revisar los números enteros, flotantes y delimitadores en
`src/lexer.py`. Probé las reglas que ya estaban para enteros decimales y
hexadecimales, como `42` y `0xFF`. Ajusté los flotantes para distinguir
el punto decimal de `..` y `...`, y agregué los delimitadores `::` y `...`.

Hice un programa con una matriz para probar los números y símbolos. También
preparé una prueba con `@` para comprobar el error léxico y otra con distintas
formas de escribir números. Los logs guardan los tokens y errores de cada prueba.

```sh
python src/main.py --usuario antivsan796 --archivo prueba_anthony.lua
python src/main.py --usuario antivsan796 --archivo prueba_anthony_error.lua
python src/main.py --usuario antivsan796 --archivo prueba_anthony_limites.lua
```

## Avance 2, sintáctico

Con `ply.yacc` hice las reglas de asignación global, operaciones aritméticas,
matrices, `for` numérico y funciones con n argumentos. Mi código está marcado
con mi nombre en `src/parser.py`.

Las matrices permiten leer y cambiar valores con índices, como `matriz[2][1]`.
El `for` puede tener un paso o dejarlo omitido, y se puede usar dentro de otro
`for`. Las funciones reciben varios valores con `...` y pueden devolver un
resultado con `return`.

Mi prueba completa suma los elementos de una matriz y calcula su promedio.
También hice pruebas con errores, como un corchete sin cerrar, un `for` sin
`do` y una función con un parámetro después de `...`. El log indica el token
y la línea donde se encontró el error.

```sh
python src/main_sintactico.py
python src/main_sintactico.py --archivo prueba_anthony_for_error.lua
```

Las pruebas están en `src/pruebas/algoritmos/` y los logs quedan en
`src/pruebas/resultados/`.

## Avance 3

Empecé con mi regla del `for`: el paso no puede ser cero. Por ahora reviso
cuando está escrito como un número, incluso `-0.0` o `(0)`. Si se omite,
el paso es 1. El parser guarda ese dato y `src/semantico.py` lo revisa.

```sh
python src/main_semantico.py
python src/main_semantico.py --archivo prueba_anthony_semantico_for_error.lua
```

Cada ejecución guarda un log `semantico-antivsan796-fecha-hora.txt` en la
carpeta de resultados. La prueba con error tiene dos ciclos con paso cero.

Todavía me falta revisar los tipos del inicio, límite y paso, los pasos que
usan variables u operaciones y mi regla de concatenación.
