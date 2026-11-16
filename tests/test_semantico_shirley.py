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


# INICIO APORTE SHIRLEY ARAGÓN: PRUEBAS DE LAS REGLAS 1 Y 3
def errores(codigo):
    return analizar(textwrap.dedent(codigo).lstrip())


def mensaje_regla1(linea, nombre):
    return (f"Error semántico [Identificadores] en la línea {linea}: "
            f"la variable '{nombre}' no está declarada en este ámbito")


def mensaje_regla3(linea, nombre):
    return (f"Error semántico [Asignación] en la línea {linea}: "
            f"no se puede modificar la constante '{nombre}'")


class Regla1Identificadores(unittest.TestCase):
    def test_variable_declarada_es_valida(self):
        self.assertEqual(errores('''
            local a = 1
            b = 2
            print(a + b)
        '''), [])

    def test_variable_sin_declarar(self):
        self.assertEqual(errores('''
            print(y)
        '''), [mensaje_regla1(1, 'y')])

    def test_local_fuera_de_su_bloque(self):
        resultado = errores('''
            local n = 5
            if n > 1 then
                local x = 10
            end
            print(x)
        ''')
        self.assertIn(mensaje_regla1(5, 'x'), resultado)

    def test_variable_del_for_no_sale_del_bucle(self):
        resultado = errores('''
            for i = 1, 3 do
                print(i)
            end
            print(i)
        ''')
        self.assertEqual(resultado, [mensaje_regla1(4, 'i')])

    def test_local_no_se_ve_en_su_propia_declaracion(self):
        self.assertEqual(errores('''
            local x = x
        '''), [mensaje_regla1(1, 'x')])

    def test_funcion_usa_global_definida_despues(self):
        self.assertEqual(errores('''
            function a()
                b()
            end
            function b()
                print("ok")
            end
            a()
        '''), [])

    def test_until_ve_las_locales_del_cuerpo(self):
        self.assertEqual(errores('''
            local n = 0
            repeat
                local s = n + 1
                n = s
            until s >= 3
        '''), [])

    def test_funciones_de_lua_estan_declaradas(self):
        self.assertEqual(errores('''
            local t = {}
            print(type(t), tostring(1))
            io.write("hola")
        '''), [])


class Regla3Constantes(unittest.TestCase):
    def test_constante_no_se_modifica(self):
        self.assertEqual(errores('''
            local PI <const> = 3.1416
            PI = 3
        '''), [mensaje_regla3(2, 'PI')])

    def test_constante_leida_es_valida(self):
        self.assertEqual(errores('''
            local PI <const> = 3.1416
            local r = 2
            local area = PI * r * r
        '''), [])

    def test_modificar_constante_dentro_de_funcion(self):
        resultado = errores('''
            local MAX <const> = 10
            local function f()
                MAX = MAX + 1
            end
        ''')
        self.assertEqual(resultado, [mensaje_regla3(3, 'MAX')])

    def test_variable_normal_si_se_modifica(self):
        self.assertEqual(errores('''
            local a = 1
            a = 2
        '''), [])

    def test_campo_de_constante_si_se_modifica(self):
        self.assertEqual(errores('''
            local t <const> = {x = 1}
            t.x = 2
        '''), [])

    def test_local_nueva_oculta_la_constante(self):
        self.assertEqual(errores('''
            local PI <const> = 3
            local PI = 4
            PI = 5
        '''), [])
# FIN APORTE SHIRLEY ARAGÓN


if __name__ == '__main__':
    unittest.main()