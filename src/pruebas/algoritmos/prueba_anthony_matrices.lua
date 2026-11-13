-- Acceso y cambio de valores en una matriz.
matriz = {{42, 0xFF, 3.14,}; {0, 125, .5};}
suma = matriz[1][1] + matriz[2][2]
matriz[2][1] = suma * 0.5
fila = {}
fila[1] = matriz[1][3]
matriz[3] = fila
