from pathlib import Path
from datetime import datetime
from lexer import lexer

BASE_DIR = Path(__file__).resolve().parent

def ejecutar_analisis():

    archivo = BASE_DIR / "pruebas" / "algoritmos" / "prueba_paula.lua"

    codigo = archivo.read_text(encoding="utf-8")

    lexer.lineno = 1
    lexer.errors = []
    lexer.input(codigo)

    resultados = []

    print("\n===== TOKENS RECONOCIDOS =====\n")

    while True:
        token = lexer.token()

        if token is None:
            break

        linea = (
            f"Token: {token.type:<12} "
            f"Valor: {str(token.value):<15} "
            f"Linea: {token.lineno}"
        )

        print(linea)
        resultados.append(linea)

    print("\n===== ERRORES LEXICOS =====\n")

    if lexer.errors:
        for error in lexer.errors:
            print(error)
            resultados.append(error)
    else:
        print("No se encontraron errores lexicos.")
        resultados.append("No se encontraron errores lexicos.")

    carpeta_logs = BASE_DIR / "pruebas" / "resultados"
    carpeta_logs.mkdir(exist_ok=True)

    fecha = datetime.now().strftime("%d-%m-%Y-%Hh%M%S")
    nombre = f"lexico-politopoli-{fecha}.txt"

    ruta = carpeta_logs / nombre

    ruta.write_text(
        "\n".join(resultados),
        encoding="utf-8"
    )

    print(f"\nLog generado: {ruta}")


if __name__ == "__main__":
    ejecutar_analisis()
