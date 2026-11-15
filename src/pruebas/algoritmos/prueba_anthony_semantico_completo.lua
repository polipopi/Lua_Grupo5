-- Suma de una matriz y descripcion del resultado.
local matriz = {{1, 2, 3}, {4, 5, 6}}
local inicio = "1"
local paso = "1"
local total = 0

for fila = inicio, #matriz, paso do
    for columna = 1, #matriz[fila] do
        total = total + matriz[fila][columna]
    end
end

local function describir(resultado, ...)
    local etiquetas = {...}
    return "Total: " .. resultado .. ", etiquetas: " .. #etiquetas
end

local estado = nil
if total > 0 then
    estado = "listo"
else
    estado = "sin datos"
end
print(describir(total, "matriz", estado))
