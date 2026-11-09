-- ==================================================
-- ALGORITMO MARLO VALLE
-- ==================================================

--[[
  Registro de asistencia de estudiantes.
  Usa constante, conjunto, funcion con parametro
  opcional, repeat ... until, impresion y lectura.
]]

-- Constante
local MAX_ESTUDIANTES <const> = 3
local TITULO = [[=== Registro de asistencia ===]]

-- Conjunto: tabla cuyas claves son los elementos
local presentes = {}
local cursos = { ["Lenguajes"] = true, ['Redes'] = true, Calculo = false }

-- Funcion con parametro opcional
local function saludar(nombre, saludo)
    saludo = saludo or "Hola"
    return saludo .. ", " .. nombre .. "!"
end

-- Impresion de datos
print(TITULO)
io.write("Curso: ", 'Lenguajes', "\n")
print("Ingrese los nombres (escriba \"fin\" para terminar):")

-- Lectura de datos con repeat ... until
local contador = 0
local nombre = nil
repeat
    io.write("Nombre: ")
    nombre = io.read("l")
    if nombre ~= nil and nombre ~= "fin" then
        presentes[nombre] = true
        contador = contador + 1
        print(saludar(nombre))
    end
until nombre == "fin" or nombre == nil or contador >= MAX_ESTUDIANTES

-- Lectura de un numero
io.write("Ingrese el numero de aula: ")
local aula = io.read("n")
print("Aula:", aula)

-- Pertenencia al conjunto
local buscado = io.read("l")
if presentes[buscado] then
    print(saludar(buscado, "Bienvenido"))
else
    print('No se encontro a ' .. tostring(buscado) .. '\t(ausente)')
end

local activo = cursos["Lenguajes"] == true and not cursos.Calculo
print("Total presentes: " .. contador, "Curso activo: " .. tostring(activo))
