local MAX_INTENTOS <const> = 3
local ruta = "C:\usuarios\marlo"
local codigo = "\300"
local mensaje = "Ingrese su nombre
local valido = true
local vacio = nil

local intentos = 0
repeat
    io.write('Clave: ')
    local clave = io.read("l")
    intentos = intentos + 1
until clave == "lua" or intentos >= MAX_INTENTOS $ 1

print("Bienvenido", valido, vacio) @
local ayuda = [==[ texto de ayuda
que nunca se cierra ]]
