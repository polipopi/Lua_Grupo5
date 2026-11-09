local MAX_ESTUDIANTES <const> = 3
local TITULO = [[=== Registro de asistencia ===]]

local presentes = {}
local cursos = { ["Lenguajes"] = true, ['Redes'] = true, Calculo = false }

local function saludar(nombre, saludo)
    saludo = saludo or "Hola"
    return saludo .. ", " .. nombre .. "!"
end

print(TITULO)
io.write("Curso: ", 'Lenguajes', "\n")
print("Ingrese los nombres (escriba \"fin\" para terminar):")

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

local buscado = io.read("l")
if presentes[buscado] then
    print(saludar(buscado, "Bienvenido"))
else
    print('No se encontro a ' .. tostring(buscado) .. '\t(ausente)')
end

local activo = cursos["Lenguajes"] == true and not cursos.Calculo
print("Total presentes: " .. contador, "Curso activo: " .. tostring(activo))
