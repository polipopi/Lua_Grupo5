-- Prueba semantica de Shirley: sin errores

local PI <const> = 3.1416
local MAXIMO <const> = 100
local radio = 5
local area = PI * radio * radio

-- global asignada antes de usarse
total = 0
total = total + area

-- cada mensaje se ve solo dentro de su bloque
if area > 50 then
    local mensaje = "area grande"
    print(mensaje)
else
    local mensaje = "area pequena"
    print(mensaje)
end

local function circunferencia(r)
    return 2 * PI * r
end

-- la funcion usa otra que se define mas abajo
function mostrar(valor)
    mostrar_extra(valor)
end

function mostrar_extra(valor)
    print(valor, MAXIMO)
end

mostrar(circunferencia(radio))

for i = 1, 3 do
    local doble = i * 2
    print(i, doble)
end

-- el until ve las locales del cuerpo
local n = 0
repeat
    local siguiente = n + 1
    n = siguiente
until siguiente >= 3

-- una local nueva puede repetir el nombre
local radio = 10
radio = radio + 1

-- los campos de una tabla const si se pueden cambiar
local config <const> = {limite = 10}
config.limite = 20
print(config.limite, n, radio)