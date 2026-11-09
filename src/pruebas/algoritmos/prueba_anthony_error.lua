local reporte = {
    filas = {{42, 0xFF, 3.14}; {0, 125, .5}},
    escala = 0.5
}

local lectura = reporte.filas[1][1] @ reporte.escala
print(lectura)
