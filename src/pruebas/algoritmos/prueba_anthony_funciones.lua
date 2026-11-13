-- Funcion con un parametro fijo y una cantidad variable de numeros.
function sumar(factor, ...)
    numeros = {...}
    suma = 0
    for i = 1, #numeros do
        suma = suma + numeros[i]
    end
    return suma * factor
end

function contar(...)
    recibidos = {...}
    return #recibidos
end

resultado = sumar(0.5, 8, 6, 6)
cantidad = contar(10, 20, 30)
sin_datos = contar()
operacion = sumar
mensaje = "Suma ponderada"
activo = true
terminado = false
pendiente = nil
print(mensaje, resultado, cantidad, sin_datos)
