-- Los controles de estos ciclos tienen tipos incorrectos.
for numero = true, 3 do end
for numero = 1, nil do end
for numero = 1, 3, {} do end
for numero = function(...) return 1 end, 3 do end
