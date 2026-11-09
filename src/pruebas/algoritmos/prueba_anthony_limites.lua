local factor = 1.e+2
local inicio, paso = .5e1, 2.
local lecturas = {0X0A, 0007; 5E+1}

for i = 1, #lecturas do
    local lectura = (inicio + paso * lecturas[i]) / factor
    local etiqueta = "Lectura "..i
    print(etiqueta, lectura)
end
