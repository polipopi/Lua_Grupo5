-- Matriz, for numerico y funcion con n argumentos.
matriz = {{1, 2, 3}; {4, 5, 6}}
total = 0

for fila = 1, #matriz do
    for columna = 1, #matriz[fila] do
        total = total + matriz[fila][columna]
    end
end

function promedio(...)
    datos = {...}
    suma = 0
    for posicion = 1, #datos do
        suma = suma + datos[posicion]
    end
    return suma / #datos
end

media = promedio(matriz[1][1], matriz[1][2], matriz[1][3],
                 matriz[2][1], matriz[2][2], matriz[2][3])
matriz[2][3] = media
print("Total", total, "Promedio", media)
