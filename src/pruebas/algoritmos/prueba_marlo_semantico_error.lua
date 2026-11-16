-- ==================================================
-- ALGORITMO MARLO VALLE - ERRORES SEMANTICOS
-- ==================================================

-- Regla 6: cadenas que no representan numeros
local nota = "diez" + 5
local nombre = "Ana"
local doble = nombre * 2
local negativo = -"cinco"

-- Regla 7: break fuera de un bucle
local aprobado = nota ~= nil
if aprobado then
    break
end

for i = 1, 3 do
    local revisar = function(valor)
        if valor > 2 then
            break
        end
        return valor
    end
    print(revisar(i))
end
