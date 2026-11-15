-- Los controles de los ciclos usan operaciones con numeros.
total = 0
for numero = 1 + 1, 2 * 3, 6 / 3 do
    total = total + numero
end
for numero = 9 // 2, 1, -(5 % 3) do
    total = total + numero
end
for numero = 0, 2 ^ 3, (3 - 1) ^ 2 do
    total = total + numero
end
