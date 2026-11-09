-- ALGORITMO 2 SHIRLEY ARAGON
-- Palabras reservadas: if/elseif/else, while, for,
-- repeat/until, break, goto, in, and, or, not
 
local nota = 8
local asistencia = 90
local aprobado = false
local exonerado = nil
 
-- Estructura if / elseif / else
if nota >= 9 then
    print("Excelente")
elseif nota >= 7 and asistencia > 80 then
    print("Aprobado")
    aprobado = true
else
    print("Reprobado")
end
 
-- Operadores logicos como palabras reservadas
local pasa = (nota >= 7 and asistencia > 80) or exonerado
local inactivo = not aprobado
 
-- Bucle while con break
local i = 1
while i <= 10 do
    if i == 5 then
        break
    end
    i = i + 1
end
 
-- Bucle for numerico
for k = 1, 10, 2 do
    print(k)
end
 
-- Bucle for generico con in
local notas = {10, 8, 9}
for indice, valor in ipairs(notas) do
    print(indice, valor)
end
 
-- Bucle repeat ... until
local n = 0
repeat
    n = n + 1
until n >= 3
 
-- Salto con goto y etiqueta
goto fin
print("esto no se imprime")
::fin::
 
--[[ fin del algoritmo 2 ]]
 