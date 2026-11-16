from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime
from unittest.mock import patch
import sys
import textwrap
import unittest


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'src'))
import main_semantico as runner


class SemanticoAnthony(unittest.TestCase):
    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.base_anterior = runner.BASE_DIR
        runner.BASE_DIR = Path(self.temporal.name)
        (runner.BASE_DIR / 'pruebas/algoritmos').mkdir(parents=True)

    def tearDown(self):
        runner.BASE_DIR = self.base_anterior
        self.temporal.cleanup()

    def revisar(self, codigo, cantidad=0, contiene=None):
        archivo = runner.BASE_DIR / 'pruebas/algoritmos/caso.lua'
        archivo.write_text(textwrap.dedent(codigo).lstrip(), encoding='utf-8')
        salida = StringIO()
        with redirect_stdout(salida):
            runner.ejecutar_analisis('caso.lua')
        log = Path(salida.getvalue().rsplit('Log generado: ', 1)[1].strip())
        texto = log.read_text(encoding='utf-8')
        self.assertNotIn('Error sintactico', texto)
        self.assertNotIn('Error léxico', texto)
        self.assertEqual(texto.count('Error semantico'), cantidad, texto)
        if contiene is not None:
            self.assertIn(contiene, texto)
        return texto

    def test_asignacion_y_cambio_de_valor(self):
        self.revisar('dato = "bien" x = dato .. 1 dato = nil x = dato .. 2', 1, 'valor nil')
        self.revisar('paso = 2 paso = paso - 2 for i = 1, 3, paso do end', 1, 'no puede ser cero')
        self.revisar('a, b = 0, 1 a, b = b, a for i = 1, 3, b do end', 1, 'no puede ser cero')

    def test_ambitos_locales(self):
        self.revisar('paso = 2 if true then local paso = 0 end for i = 1, 3, paso do end')
        self.revisar('local paso = 1 if true then local paso = paso + 1 end for i = 1, 3, paso do end')
        self.revisar('local paso = 0 for paso = 1, 3 do end for i = 1, 3, paso do end', 1)
        self.revisar('local paso = 1 function leer() return paso end local paso = 0 for i = 1, 3, leer() do end')
        self.revisar('local paso = 1 function leer() return paso end paso = 0 for i = 1, 3, leer() do end', 1)
        self.revisar('local dato = "a" local f = function(...) return dato end local dato = nil x = f() .. "b"')

    def test_condiciones_y_cortocircuito(self):
        self.revisar('paso = 1 if false then paso = 0 else paso = 2 end for i = 1, 3, paso do end')
        self.revisar('paso = 1 if io.read() then paso = 0 end for i = 1, 3, paso do end')
        self.revisar('paso = 1 if io.read() then paso = 0 else paso = 0 end for i = 1, 3, paso do end', 1)
        self.revisar('x = false and (nil .. "a") y = true or (nil .. "a")')
        self.revisar('x = (nil or "a") .. (0 and "b")')
        self.revisar('x = not "a" .. "b"', 1, 'valor boolean')
        self.revisar('a = {} b = {} if io.read() then a = b end if a == b then x = "a" else x = nil end y = x .. "b"')

    def test_lecturas_desconocidas(self):
        self.revisar('dato = io.read() x = dato .. "a" for i = 1, 3, dato do end')
        self.revisar('paso = 1 function cambiar() paso = 0 return true end x = io.read() and cambiar() for i = 1, 3, paso do end')

    def test_funciones_y_parametros(self):
        self.revisar('function unir(x) return "a" .. x end unir("b") unir(nil)', 1, 'valor nil')
        self.revisar('function cero(...) return 2 - 2 end paso = cero() for i = 1, 3, paso do end', 1)
        self.revisar('x = nil function f(...) return x .. "b" end x = "a" f()')
        self.revisar('function f(...) return futuro .. "b" end futuro = "a" f()')
        self.revisar('function f(...) return futuro .. "b" end local futuro = "a" f()', 1, 'valor nil')
        self.revisar('paso = 1 function cambiar(...) paso = 0 end for i = 1, 3, paso do end')
        self.revisar('paso = 1 function cambiar(...) paso = 0 end cambiar() for i = 1, 3, paso do end', 1)
        self.revisar('function f(x) if x then return "a" end return nil end dato = f(io.read()) x = dato .. "b"')
        self.revisar('function crear(x) return function(...) return x end end f = crear("a") g = crear(nil) if f == g then x = nil else x = "bien" end y = x .. "b"')

    def test_varargs_y_retornos(self):
        self.revisar('function contar(...) local datos = {...} return #datos end paso = contar(4, 5) - 2 for i = 1, 3, paso do end', 1)
        self.revisar('function datos(...) return 1, 0 end a, paso = datos() for i = 1, 3, paso do end', 1)
        self.revisar('function datos(...) return 1, 0 end a, paso = (datos()) for i = 1, 3, paso do end', 1, 'se recibio nil')
        self.revisar('function f(n) return f(n) end x = f(1) .. "a"')
        self.revisar('function f(x) local t = {x} for i = 1, 3, #t - 1 do end end f(nil)')
        self.revisar('function f(x) local t = {x} for i = 1, 3, #t - 1 do end end f("a")', 1)

    def test_tablas_indices_y_aliases(self):
        self.revisar('datos = {paso = 1} copia = datos copia.paso = 0 for i = 1, 3, datos.paso do end', 1)
        self.revisar('m = {{1, 2}, {3, 4}} paso = m[1][2] - 2 for i = 1, 3, paso do end', 1)
        self.revisar('t = {[true] = nil, [1] = "a"} x = t[1] .. "b"')
        self.revisar('t = {1} t[1] = nil for i = 1, 3, #t do end', 1)
        self.revisar('local T = {} function T:cero(...) return 0 end for i = 1, 3, T:cero() do end', 1)
        self.revisar('clave = {} t = {[clave] = "a"} if true then x = 1 end y = t[clave] .. "b"')

    def test_efectos_de_bucles(self):
        self.revisar('paso = 1 for i = 1, 3 do paso = 0 end for j = 1, 3, paso do end', 1)
        self.revisar('paso = 1 for i = 1, 3 do paso = paso - 1 end for j = 1, 3, paso do end')
        self.revisar('paso = 1 for i = 3, 1 do paso = 0 end for j = 1, 3, paso do end')
        self.revisar('paso = 1 repeat local dato = 0 paso = dato until true for j = 1, 3, paso do end', 1)
        self.revisar('for i = 1, 3 do for j = 1, 3, i - 2 do end end', 1, 'no puede ser cero')
        self.revisar('paso = 1 for i = 0, 0 do paso = i end for j = 1, 3, paso do end', 1)

    def test_conversiones_de_cadenas(self):
        for paso in ('"1"', '"0x1"', '"1e0"', '[=[1]=]', r'"\049"', r'"\x31"', r'"\u{31}"'):
            with self.subTest(paso=paso):
                self.revisar(f'for i = "1", "3", {paso} do end')
        for paso in ('"0"', '"0.0"', '"0x0"', r'"\048"', '"0" .. "0"'):
            with self.subTest(paso=paso):
                self.revisar(f'for i = 1, 3, {paso} do end', 1, 'no puede ser cero')
        for paso in ('"texto"', '"inf"', '"nan"', '"1_0"', '"0x"'):
            with self.subTest(paso=paso):
                self.revisar(f'for i = 1, 3, {paso} do end', 1, 'cadena no representa un numero')
        self.revisar('paso = tonumber("0") for i = 1, 3, paso do end', 1)
        self.revisar('paso = tonumber("10", 2) - 2 for i = 1, 3, paso do end', 1)
        self.revisar('x = tostring(false) .. "a"')
        self.revisar('for i = 1, 3, tostring(false) do end', 1, 'cadena no representa un numero')

    def test_operaciones_y_errores_en_controles(self):
        for operacion in ('2 - 2', '4 * (3 - 3)', '8 % 2', '-0.0', '1 / (1 / 0)'):
            with self.subTest(operacion=operacion):
                self.revisar(f'for i = 1, 3, {operacion} do end', 1, 'no puede ser cero')
        self.revisar('for i = 1, 3, 1 // 0 do end', 1, 'division entera por cero')
        self.revisar('x = "a" .. (1 % 0)', 1, 'modulo entero por cero')
        self.revisar('for i = 1, 3, 1 / 0 do end')
        self.revisar('for i = 1, 3, 1 / ((0 / 0) / 0) do end')
        self.revisar('for i = 1, 3, (2 ^ 53 + 1) - 2 ^ 53 do end', 1)

    def test_algoritmos_anteriores(self):
        nombres = ('prueba_paula.lua', 'prueba_shirley_sintactico.lua',
                   'prueba_marlo_sintactico.lua', 'prueba_anthony_completo.lua',
                   'prueba_anthony_semantico_for.lua', 'prueba_anthony_semantico_tipos.lua',
                   'prueba_anthony_semantico_operaciones.lua',
                   'prueba_anthony_semantico_concatenacion.lua',
                   'prueba_anthony_semantico_completo.lua')
        for nombre in nombres:
            with self.subTest(nombre=nombre):
                codigo = (RAIZ / 'src/pruebas/algoritmos' / nombre).read_text(encoding='utf-8')
                self.revisar(codigo)

    def test_algoritmo_completo_con_errores(self):
        codigo = (RAIZ / 'src/pruebas/algoritmos/prueba_anthony_semantico_completo_error.lua').read_text(encoding='utf-8')
        self.revisar(codigo, 6)

    def test_reglas_integradas_de_paula(self):
        codigo = (RAIZ / 'src/pruebas/algoritmos/prueba_semantica_paula.lua').read_text(encoding='utf-8')
        texto = self.revisar(codigo)
        self.assertEqual(texto.count('Error semántico'), 4, texto)
        self.assertIn("'total' no es una función", texto)
        self.assertIn("no se puede aplicar '+' entre number y boolean", texto)
        self.assertIn("no se puede aplicar '+' entre number y table", texto)
        # Regla 6 (Marlo): una cadena que no es numeral se reporta como error de conversion.
        self.assertIn('la cadena "hola" no puede convertirse a número', texto)

    def test_errores_previos_al_semantico(self):
        for codigo, categoria in [('x = "a" .. nil y = +', 'Error sintactico'),
                                   ('x = "a" .. nil @', 'Error léxico')]:
            archivo = runner.BASE_DIR / 'pruebas/algoritmos/caso.lua'
            archivo.write_text(codigo, encoding='utf-8')
            salida = StringIO()
            with redirect_stdout(salida):
                runner.ejecutar_analisis('caso.lua')
            log = Path(salida.getvalue().rsplit('Log generado: ', 1)[1].strip())
            texto = log.read_text(encoding='utf-8')
            self.assertIn(categoria, texto)
            self.assertNotIn('Error semantico', texto)
        self.revisar('x = "bien" .. 1')

    def test_reinicio_despues_de_error(self):
        self.revisar('dato = nil x = "a" .. dato', 1)
        self.revisar('dato = "bien" x = "a" .. dato')

    def test_logs_con_la_misma_hora(self):
        with patch.object(runner, 'datetime') as reloj:
            reloj.now.return_value = datetime(2026, 11, 15, 12, 0)
            for _ in range(3):
                self.revisar('dato = "bien" x = "a" .. dato')
        logs = list((runner.BASE_DIR / 'pruebas/resultados').glob('*.txt'))
        self.assertEqual(len(logs), 3)

    def test_break_conserva_los_valores_al_salir(self):
        cuerpos = (
            'for i = 1, 3 do break paso = 0 texto = nil .. "x" end',
            'for i = 1, 1000 do break paso = 0 end',
            'for clave, valor in pairs({1, 2}) do break paso = 0 end',
            'while true do break paso = 0 end',
            'repeat break paso = 0 until true',
            'for i = 1, 3 do if i == 1 then break end paso = 0 end',
        )
        for cuerpo in cuerpos:
            with self.subTest(cuerpo=cuerpo):
                texto = self.revisar(f'paso = 1 {cuerpo} for j = 1, 3, paso do end')
                self.assertNotIn('Error', texto)
        self.revisar('paso = 1 for i = 1, 3 do paso = 0 break end for j = 1, 3, paso do end', 1)

    def test_break_condicional_con_valor_desconocido(self):
        for cuerpo in (
            'for i = 1, 3 do if io.read() then break end paso = 0 end',
            'while true do if io.read() then break end paso = 0 break end',
            'repeat if io.read() then break end paso = 0 until true',
        ):
            with self.subTest(cuerpo=cuerpo):
                texto = self.revisar(f'paso = 1 {cuerpo} for j = 1, 3, paso do end')
                self.assertNotIn('Error', texto)

    def test_break_solo_sale_del_bucle_interno(self):
        self.revisar('''
            paso = 1
            for i = 1, 3 do
                for j = 1, 3 do break end
                paso = 0
            end
            for numero = 1, 3, paso do end
        ''', 1, 'no puede ser cero')
        texto = self.revisar('''
            paso = 1
            while true do
                for i = 1, 3 do break end
                break
                paso = 0
            end
            for numero = 1, 3, paso do end
        ''')
        self.assertNotIn('Error', texto)

    def test_break_y_return_en_funciones(self):
        definicion = '''
            function elegir(condicion)
                for i = 1, 3 do
                    if condicion then return 0 else break end
                end
                return 1
            end
        '''
        self.revisar(definicion + 'for i = 1, 3, elegir(false) do end')
        self.revisar(definicion + 'for i = 1, 3, elegir(true) do end', 1)
        texto = self.revisar('''
            paso = 1
            function interrumpir(...)
                break
                paso = 0
            end
            for i = 1, 1 do interrumpir() end
            for j = 1, 3, paso do end
        ''')
        self.assertIn("'break' fuera de un bucle", texto)
        self.assertNotIn("el paso del 'for' no puede ser cero", texto)


if __name__ == '__main__':
    unittest.main()
