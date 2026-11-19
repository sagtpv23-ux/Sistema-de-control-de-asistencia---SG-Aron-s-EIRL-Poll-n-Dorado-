import os
import subprocess
import threading
import webbrowser

from controladores.web_controlador import app


def abrir_navegador():
    """Abre la pagina en Chrome a PANTALLA COMPLETA (F11 para salir).
    Si no encuentra Chrome, usa el navegador predeterminado."""
    url = "http://127.0.0.1:5000"
    rutas = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            subprocess.Popen([ruta, "--new-window", "--start-fullscreen", url])
            return
    webbrowser.open(url)


if __name__ == "__main__":
    threading.Timer(1.0, abrir_navegador).start()
    app.run(debug=False)
