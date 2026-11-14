-- ==================================================
-- ALGORITMO MARLO VALLE - ERRORES SINTACTICOS
-- ==================================================

-- Atributo desconocido en una constante
local LIMITE <constante> = 5

-- repeat sin condicion despues de until
local n = 0
repeat
    n = n + 1
until
local total = n

-- Metodo sin nombre despues de los dos puntos
function Persona:(edad)
    self.edad = edad
end

-- Llamada sin cerrar el parentesis
print("Total: " .. n
