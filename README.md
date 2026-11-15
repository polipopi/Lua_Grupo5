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

Empecé con mi regla del `for`: el paso no puede ser cero. Reviso cuando está
escrito como un número, incluso `-0.0` o `(0)`. Si se omite, el paso es 1.
El parser guarda ese dato y `src/semantico.py` lo revisa.

También reviso los tipos del inicio, límite y paso cuando aparecen como
valores literales. Un booleano, `nil`, una tabla o una función producen un
error con la línea del ciclo y el dato que tiene el tipo incorrecto.

Ahora también calculo operaciones con números en los controles del ciclo.
Por ejemplo, `2 - 2` y `4 * (3 - 3)` se detectan como pasos iguales a cero.
Uso las operaciones `+`, `-`, `*`, `/`, `//`, `%` y `^`, con sus paréntesis.

También agregué mi regla de concatenación. Reviso que `..` reciba cadenas
o números. Si encuentro un booleano, `nil`, una tabla o una función, el error
indica la línea y el operando incorrecto. Por ahora reviso valores literales
y operaciones numéricas que puedo calcular.

```sh
python src/main_semantico.py
python src/main_semantico.py --archivo prueba_anthony_semantico_operaciones_error.lua
python src/main_semantico.py --archivo prueba_anthony_semantico_concatenacion.lua
python src/main_semantico.py --archivo prueba_anthony_semantico_concatenacion_error.lua
```

Cada ejecución guarda un log `semantico-antivsan796-fecha-hora.txt` en la
carpeta de resultados.

Todavía me falta revisar los valores que vienen de variables, las conversiones
de cadenas en los controles del `for` y los errores dentro de las operaciones.

## Aporte de Marlo Valle (`marsalvatore28`)

### Avance 1, léxico

En `src/lexer.py` hice las cadenas, los booleanos, `nil` y el manejo de
tokens de error. Las cadenas pueden usar comillas simples, dobles o corchetes
largos como `[[texto]]`. Cada error léxico se muestra con su línea y posición,
por ejemplo un carácter no reconocido, una cadena sin cerrar o una secuencia
de escape inválida.

```sh
python src/main.py --usuario marsalvatore28 --archivo prueba_marlo.lua
python src/main.py --usuario marsalvatore28 --archivo prueba_marlo_error.lua
```

### Avance 2, sintáctico

En `src/parser.py` agregué las reglas de constantes (`local PI <const> = 3.14`),
`repeat ... until`, funciones locales con parámetro opcional, conjuntos con su
recorrido `for elemento in pairs(conjunto)`, impresión y lectura de datos
(incluida la forma `print "texto"`) y clases con propiedades y métodos
(`function Clase:metodo()` y `objeto:metodo()`).

Mi prueba registra a un estudiante en varios cursos usando una clase, un
conjunto, una constante y un ciclo `repeat`. La prueba con errores tiene un
atributo desconocido, un `until` sin condición, un método sin nombre y un
paréntesis sin cerrar.

```sh
python src/main_sintactico.py --usuario marsalvatore28 --archivo prueba_marlo_sintactico.lua
python src/main_sintactico.py --usuario marsalvatore28 --archivo prueba_marlo_sintactico_error.lua
```
