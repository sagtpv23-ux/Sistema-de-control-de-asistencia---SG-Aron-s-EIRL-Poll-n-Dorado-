import sys
from controladores.consola_controlador import main


def configurar_utf8():

    for flujo in (sys.stdin, sys.stdout, sys.stderr):
        try:
            if not flujo.isatty() and flujo.encoding.lower().replace("-", "") != "utf8":
                flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

if __name__ == "__main__":
    configurar_utf8()
    main()
