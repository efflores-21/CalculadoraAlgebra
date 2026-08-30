"""
Programa Principal - Calculadora de Álgebra Lineal con interfaz gráfica
"""

import time
import tkinter as tk
from frontend.interfaz import InterfazCalculadora


if __name__ == "__main__":
    try:
        root = tk.Tk()
    except tk.TclError:
        print("No se pudo abrir la interfaz gráfica. Ejecuta el programa en un entorno con escritorio disponible.")
        raise SystemExit(1)

    root.deiconify()
    app = InterfazCalculadora(root)

    try:
        while root.winfo_exists():
            root.update()
            root.update_idletasks()
            time.sleep(0.02)
    except tk.TclError:
        pass