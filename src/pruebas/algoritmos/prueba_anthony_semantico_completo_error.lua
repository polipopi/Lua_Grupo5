-- Errores de mis reglas con valores guardados en variables.
local paso = 2
paso = paso - 2
for numero = 1, 3, paso do end

local activo = false
local estado = "Estado: " .. activo

local limites = {ultimo = "tres"}
for numero = 1, limites.ultimo do end

local cadena_cero = "0" .. "0"
for numero = 1, 3, cadena_cero do end

local resto = 7 % 0
for numero = 1, 3, resto do end

local dato = nil
local detalle = "Dato: " .. dato
