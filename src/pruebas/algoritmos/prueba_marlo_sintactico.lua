-- ==================================================
-- ALGORITMO MARLO VALLE - ANALIZADOR SINTACTICO
-- Inscripcion de estudiantes en cursos
-- ==================================================

-- Constante
local MAX_CURSOS <const> = 3
local SALUDO <const> = "Bienvenido"

-- Clase Estudiante con propiedades y metodos
local Estudiante = {}
Estudiante.__index = Estudiante

function Estudiante.nuevo(nombre, edad)
    local obj = setmetatable({}, Estudiante)
    obj.nombre = nombre
    obj.edad = edad or 18
    obj.cursos = {}
    obj.total = 0
    return obj
end

-- Conjunto: los cursos inscritos son las claves de la tabla
function Estudiante:inscribir(curso)
    if self.cursos[curso] then
        return false
    end
    self.cursos[curso] = true
    self.total = self.total + 1
    return true
end

function Estudiante:mostrar()
    print("Estudiante: " .. self.nombre, "Edad: " .. self.edad)
    for curso in pairs(self.cursos) do
        print("  - " .. curso)
    end
end

-- Funcion local con parametro opcional
local function saludar(nombre, saludo)
    saludo = saludo or SALUDO
    return saludo .. ", " .. nombre .. "!"
end

-- Conjunto de cursos disponibles
local disponibles = {Lenguajes = true, ["Redes"] = true, Calculo = true}
disponibles["Fisica"] = true
disponibles.Calculo = nil

-- Impresion y lectura de datos
print "=== Inscripcion de cursos ==="
io.write("Ingrese su nombre: ")
local nombre = io.read("l")
io.write("Ingrese su edad: ")
local edad = io.read("n")
local linea = io.read "l"

local estudiante = Estudiante.nuevo(nombre, edad)
print(saludar(estudiante.nombre))
print(saludar(estudiante.nombre, "Hola"))

-- Repeat ... until
local curso = nil
repeat
    io.write("Curso a inscribir (fin para terminar): ")
    curso = io.read("l")
    if curso ~= nil and curso ~= "fin" and disponibles[curso] then
        local agregado = estudiante:inscribir(curso)
        if not agregado then
            print("Ya estaba inscrito en " .. curso)
        end
    end
until curso == nil or curso == "fin" or estudiante.total >= MAX_CURSOS

estudiante:mostrar()
