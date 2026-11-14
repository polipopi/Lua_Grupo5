-- prueba sintactica if/elseif/else Shirley Aragon

local nota = 8
local asistencia = 90
local exonerado = false

if nota >= 9 then
    print("Excelente")
end

if nota >= 7 and asistencia > 80 then
    print("Aprobado")
else
    print("Reprobado")
end

if nota >= 9 then
    print("A")
elseif nota >= 8 then
    print("B")
elseif nota >= 7 then
    print("C")
else
    print("D")
end

if (nota > 5 and asistencia > 70) or exonerado then
    if not exonerado then
        print("Pasa por notas")
    end
end