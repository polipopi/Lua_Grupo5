-- Suma de los elementos de una matriz con dos for numericos.
matriz = {{1, 2, 3}, {4, 5, 6}}
total = 0
for fila = 1, #matriz do
    for columna = 1, #matriz[fila] do
        total = total + matriz[fila][columna]
    end
end

descendente = 0
for numero = 5, 1, -2 do
    descendente = descendente + numero
end
