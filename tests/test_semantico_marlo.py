from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import sys
import textwrap
import unittest


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'src'))
with redirect_stderr(StringIO()):
    from semantico import analizar


# INICIO APORTE MARLO VALLE: PRUEBAS DE LAS REGLAS 6 Y 7
def errores(codigo):
    return analizar(textwrap.dedent(codigo).lstrip())


class Regla6Conversion(unittest.TestCase):
    def test_cadenas_numericas_son_validas(self):
        self.assertEqual(errores('''
            local a = "10" + 5
            local b = 3 * "0x10"
            local c = "  2.5  " - 1
            local d = "1e3" / 2
        '''), [])

    def test_cadena_no_numerica(self):
        self.assertEqual(errores('''
            local a = "10" + 5
            local b = "diez" + 5
        '''), ['Error semántico [Conversión] en la línea 2: '
               'la cadena "diez" no puede convertirse a número'])

    def test_menos_unario_y_variables(self):
        resultado = errores('''
            local texto = "abc"
            local n = -texto
        ''')
        self.assertEqual(len(resultado), 1)
        self.assertIn('la cadena "abc"', resultado[0])

    def test_lectura_desconocida_no_se_reporta(self):
        self.assertEqual(errores('local n = io.read("l") + 1'), [])

    def test_conversion_explicita(self):
        self.assertEqual(errores('''
            local n = tonumber("diez")
            local t = tostring(5) .. " ok"
        '''), [])

    def test_regla_4_se_mantiene_para_otros_tipos(self):
        resultado = errores('local r = "hola" + true')
        self.assertEqual(len(resultado), 2)
        self.assertIn('[Conversión]', resultado[0])
        self.assertIn("entre string y boolean", resultado[1])


class Regla7Break(unittest.TestCase):
    def test_break_dentro_de_bucles(self):
        self.assertEqual(errores('''
            local x = 0
            while true do break end
            for i = 1, 3 do if i == 2 then break end end
            for k in pairs({}) do break end
            repeat x = x + 1 break until x > 3
        '''), [])

    def test_break_en_if_sin_bucle(self):
        self.assertEqual(errores('''
            local x = 1
            if x > 0 then
                break
            end
        '''), ["Error semántico [Estructuras de Control] en la línea 3: "
               "'break' fuera de un bucle"])

    def test_funcion_dentro_de_bucle(self):
        resultado = errores('''
            for i = 1, 2 do
                local f = function() break end
            end
        ''')
        self.assertEqual(len(resultado), 1)
        self.assertIn('línea 2', resultado[0])

    def test_break_suelto(self):
        self.assertEqual(len(errores('break')), 1)


class ClasesConMetatablas(unittest.TestCase):
    def test_metodos_heredados_no_son_errores(self):
        self.assertEqual(errores('''
            local Animal = {}
            Animal.__index = Animal
            function Animal.nuevo(nombre)
                local obj = setmetatable({}, Animal)
                obj.nombre = nombre
                return obj
            end
            function Animal:hablar() return self.nombre end
            local Perro = setmetatable({}, Animal)
            Perro.__index = Perro
            function Perro.nuevo(nombre)
                return setmetatable(Animal.nuevo(nombre), Perro)
            end
            function Perro:ladrar() return "guau" end
            local p = Perro.nuevo("Toby")
            print(p:ladrar(), p:hablar())
        '''), [])

    def test_campo_que_no_es_funcion_sigue_siendo_error(self):
        resultado = errores('''
            local t = {}
            t.valor = 5
            t.valor(3)
        ''')
        self.assertEqual(len(resultado), 1)
        self.assertIn('no es una función', resultado[0])
# FIN APORTE MARLO VALLE


if __name__ == '__main__':
    unittest.main()
