-- Buscar una fila con datos y luego sumar la matriz.
local matriz = {{1, 2, 3}, {4, 5, 6}}
local paso = 1

for fila = 1, #matriz do
    if matriz[fila][1] > 0 then
        break
    end
    paso = 0
end

local total = 0
for fila = 1, #matriz, paso do
    for columna = 1, #matriz[fila] do
        total = total + matriz[fila][columna]
    end
end

local function describir(resultado, ...)
    local etiquetas = {...}
    return "Total: " .. resultado .. ", etiquetas: " .. #etiquetas
end

print(describir(total, "matriz", "break"))
