
-- PRUEBAS DE PAULA BASTIDAS

-- 1. Declaracion de variables locales
local a = 20
local b = 5
local nombre = "Paula"

-- 2. Operadores aritmeticos
local suma = a + b
local resta = a - b
local multiplicacion = a * b
local division = a / b
local divisionEntera = a // b
local modulo = a % b
local potencia = a ^ 2

-- 3. Operadores relacionales
local igual = a == 20
local diferente = a ~= 5
local menor = a < 30
local menorIgual = a <= 20
local mayor = a > 10
local mayorIgual = a >= 20

-- 4. Concatenacion
local saludo = "Hola " .. nombre

-- 5. Asignacion multiple
local x, y = 10, 20
x, y = y, x

-- 6. Estructura while
local contador = 1
while contador < 4 do
    contador = contador + 1
end

-- 7. Tabla (estructura de datos)
local persona = {
    nombre = "Paula",
    edad = 21
}

-- 8. Funcion anonima
local doble = function(numero)
    return numero * 2
end

local resultado = doble(5)

-- 9. Llamadas a print
print(suma)
print(resta)
print(multiplicacion)
print(division)
print(divisionEntera)
print(modulo)
print(potencia)
print(saludo)
print(resultado)
