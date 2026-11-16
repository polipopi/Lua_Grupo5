-- ==================================================
-- ALGORITMO MARLO VALLE - ANALIZADOR SEMANTICO
-- Calculo de notas con conversiones validas y break
-- ==================================================

local MAX_NOTAS <const> = 5

-- Regla 6: cadenas que si representan numeros
local base = "10" + 5
local extra = "0x0A" * 2
local promedioTexto = " 7.5 " + 0
local bono = tonumber("3") + tostring(2)

local function sumarNotas(notas, limite)
    limite = limite or MAX_NOTAS
    local suma = 0
    local contador = 0
    -- Regla 7: break dentro de un for
    for i = 1, #notas do
        if contador >= limite then
            break
        end
        suma = suma + notas[i]
        contador = contador + 1
    end
    return suma, contador
end

local notas = {base, extra, promedioTexto, bono, "8"}
local total, cantidad = sumarNotas(notas)
print("Total: " .. total, "Notas: " .. cantidad)

-- Regla 7: break dentro de while y repeat
local intento = 0
while true do
    intento = intento + 1
    if intento == 3 then break end
end

repeat
    io.write("Ingrese una nota (fin para terminar): ")
    local entrada = io.read("l")
    if entrada == nil or entrada == "fin" then
        break
    end
    local valor = tonumber(entrada)
    if valor ~= nil then
        print("Nota registrada: " .. valor)
    end
until false
