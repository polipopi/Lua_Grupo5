# Lua_Grupo5

Mi usuario de GitHub es `antivsan796`.

En el avance 2 hice las reglas de asignación global, operaciones aritméticas,
matrices, `for` numérico y funciones con n argumentos. Mi código está marcado
con mi nombre en `src/parser.py`.

Para instalar PLY y probar mi algoritmo completo uso estos comandos desde
la carpeta del repositorio.

```sh
python -m pip install -r requirements.txt
python src/main_sintactico.py
```

Para elegir otra prueba uso `--archivo`, por ejemplo
`python src/main_sintactico.py --archivo prueba_anthony_for_error.lua`.
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
