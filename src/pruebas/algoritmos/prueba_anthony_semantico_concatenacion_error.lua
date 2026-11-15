-- Tipos que no se pueden concatenar.
resumen = "Total: " .. nil
estado = true .. " activo"
detalle = "Datos: " .. {1, 2}
operacion = "Funcion: " .. function(...) return 1 end
