-- El resultado del paso es cero en los tres ciclos.
total = 0
for numero = 1, 3, 2 - 2 do
    total = total + numero
end
for numero = 1, 3, 4 * (3 - 3) do
    total = total + numero
end
for numero = 1, 3, 8 % 2 do
    total = total + numero
end
