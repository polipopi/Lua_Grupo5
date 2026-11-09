-- ALGORITMO 3 SHIRLEY ARAGON (con errores lexicos)
-- Contiene caracteres invalidos a proposito para
-- comprobar el reporte de errores con linea y posicion
 
-- Identificadores y palabras reservadas correctos
local notas = {10, 8, 9}
local contador = 0
 
for i = 1, 3 do
    contador = contador + notas[i]
end
 
-- Error 1: el arroba no es parte de un identificador
local promedio@ = contador / 3
 
-- Error 2: signo de dolar no reconocido
local costo$ = 25
 
--[[ comentario largo correcto
     de varias lineas ]]
 
-- Error 3: signo de interrogacion no reconocido
local activo? = true
 
repeat
    promedio = promedio - 1
until promedio < 5
 
print(promedio)
 
