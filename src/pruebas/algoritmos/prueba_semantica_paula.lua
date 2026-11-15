-- PRUEBAS SEMANTICAS

-- REGLA 2: IDENTIFICADORES
local total = 5
total(3)

-- Una funcion declarada si debe poder llamarse
function calcular()
    return 10
end

calcular()

-- REGLA 4: OPERACIONES
local edad = 20
local resultado = edad + true

local datos = {}
local otroResultado = edad + datos

-- REGLA 4: CADENAS QUE REPRESENTAN NUMEROS
local numeroTexto = "25"
local sumaTexto = numeroTexto + 5

-- Esta operacion debe generar error
local textoInvalido = "hola"
local sumaInvalida = textoInvalido + 5