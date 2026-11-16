-- Prueba semantica de Shirley: con errores

local PI <const> = 3.1416
local MAXIMO <const> = 100
local radio = 5

-- error regla 3
PI = 3
MAXIMO = MAXIMO + 1

-- error regla 1: interno solo existe dentro del if
if radio > 2 then
    local interno = 10
end
print(interno)

-- error regla 1: nunca se declaro
local suma = radio + desconocida

-- error regla 1: i solo existe dentro del for
for i = 1, 3 do
    print(i)
end
print(i)

-- esto esta bien
local ok = 1
print(ok)