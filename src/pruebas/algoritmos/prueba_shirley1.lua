-- Prueba lexica: identificadores, palabras reservadas y comentarios (Shirley Aragon)
-- Shirley Aragon
 
local edad = 20
local _temp, valorMax2 = 5, 10
local notas = {10, 8, 9}
notas[4] = 7
 
local esMayor = edad >= 18
local aprobado = (edad > 17 and valorMax2 > 7) or not esMayor
 
--[==[ comentario con nivel ]] sigue siendo comentario ]==]
if notas[1] >= 9 then
    print("Excelente")
elseif notas[1] >= 7 then
    print("Aprobado")
else
    print("Reprobado")
end
 
function sumar(a, b)
    return a + b
end
 
local total = sumar(3, 4) -- llamada con retorno
 