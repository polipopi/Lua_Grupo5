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

Hice mis dos reglas semánticas. En el `for` numérico reviso que el inicio,
límite y paso sean números y que el paso sea distinto de cero. En la
concatenación reviso que `..` reciba cadenas o números.

Ahora sigo los valores de las variables locales y globales, sus cambios,
los campos de tablas y los parámetros y retornos de funciones. También
calculo operaciones y convierto cadenas numéricas como `"1"`, `"0xFF"`
y `"1e-3"` cuando se usan en los controles del ciclo. Los errores al calcular
esos controles u operandos de concatenación se guardan con su línea.

Para eso agregué al parser los datos del programa que usa mi análisis.
Corregí la precedencia de `not`, porque es un operador unario y puede aparecer
como operando de `..`.

Al integrar los cambios de Paula, pasé sus comprobaciones de llamadas y
operaciones a `src/reglas_paula.py`. Se usan con los valores que ya sigue
el analizador y mantienen sus mensajes de error.

```sh
python src/main_semantico.py
python src/main_semantico.py --archivo prueba_anthony_semantico_completo_error.lua
python -m unittest discover -s tests
```

Cada ejecución guarda un log `semantico-antivsan796-fecha-hora.txt` en la
carpeta de resultados. Mi prueba completa suma una matriz y describe el
resultado con una función de n argumentos. La prueba con errores usa pasos
iguales a cero, un límite que no es numérico y concatenaciones con tipos inválidos.

El análisis es estático. Las lecturas por teclado y las llamadas que no puedo
resolver quedan como valores desconocidos. Para mantener acotada la revisión,
calculo hasta 256 iteraciones conocidas y 12 niveles de llamadas; en los demás
casos sigo los tipos y los valores que todavía se pueden determinar.

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
