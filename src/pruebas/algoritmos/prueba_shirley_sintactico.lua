-- prueba sintactica Shirley Aragon

local edad = 20
local a, b = 5, 10

local notas = {10, 8, 9}
notas[4] = 7
local primera = notas[1]

local esMayor = edad >= 18
local aprobado = (edad > 17 and b > 7) or not esMayor
local complejo = edad ~= 0 and (primera == 10 or notas[2] < 5) and not false

function sumar(x, y)
    return x + y
end

local total = sumar(3, 4)

if notas[1] >= 9 then
    print("Excelente")
elseif notas[1] >= 7 and edad > 17 then
    print("Aprobado")
else
    print("Reprobado")
end

if aprobado then
    if total > 5 or esMayor then
        print("Total:", total)
    end
end