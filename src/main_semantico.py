from argparse import ArgumentParser
from datetime import datetime
from itertools import count
from pathlib import Path
from semantico import analizar


BASE_DIR = Path(__file__).resolve().parent


# INICIO APORTE ANTHONY SANTANA: PRUEBAS DEL SEMANTICO
def ejecutar_analisis(archivo, usuario='antivsan796'):
    ruta = BASE_DIR / 'pruebas' / 'algoritmos' / archivo
    errores = analizar(ruta.read_text(encoding='utf-8'))

    resultados = [f'Archivo: {ruta.name}', 'Analisis semantico del programa.']
    if errores:
        resultados.extend(errores)
    else:
        resultados.append('No se encontraron errores semanticos.')

    carpeta = BASE_DIR / 'pruebas' / 'resultados'
    carpeta.mkdir(exist_ok=True)
    ahora = datetime.now()
    for intento in count():
        hora = ahora.strftime('%d-%m-%Y-%Hh%M')
        if intento:
            hora = ahora.strftime('%d-%m-%Y-%Hh%M%S%f') + str(intento)
        log = carpeta / f'semantico-{usuario}-{hora}.txt'
        try:
            salida = log.open('x', encoding='utf-8')
            break
        except FileExistsError:
            continue
    with salida:
        salida.write('\n'.join(resultados) + '\n')

    print('\n'.join(resultados))
    print(f'Log generado: {log}')


if __name__ == '__main__':
    argumentos = ArgumentParser(description='Pruebas del analizador semantico')
    argumentos.add_argument('--archivo', default='prueba_anthony_semantico_completo.lua')
    argumentos.add_argument('--usuario', default='antivsan796')
    opciones = argumentos.parse_args()
    ejecutar_analisis(opciones.archivo, opciones.usuario)
# FIN APORTE ANTHONY SANTANA
