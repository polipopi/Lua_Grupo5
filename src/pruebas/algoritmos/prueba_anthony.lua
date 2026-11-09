local filas = {{42, 0xFF, 3.14}; {}; {0, 125, .5}}
filas.factor = 0.5

function filas:suma(...)
    local total = 0
    for _, numero in ipairs({...}) do
        total = total + numero
    end
    return total * self.factor
end

for i = 1, #filas do
    if #filas[i] == 0 then goto siguiente end
    print("Fila " .. i, filas:suma(table.unpack(filas[i])))
    ::siguiente::
end

print(filas:suma(1e-3, 2E5))
