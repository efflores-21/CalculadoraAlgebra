"""Programa principal de la calculadora de sistemas lineales."""

import tkinter as tk

from frontend.interfaz import InterfazCalculadora


if __name__ == "__main__":
    try:
        root = tk.Tk()
    except tk.TclError:
        print("No se pudo abrir la interfaz gráfica. Ejecuta el programa en un entorno con escritorio disponible.")
        raise SystemExit(1)

    root.title("Calculadora de Álgebra Lineal")
    root.minsize(900, 700)
    app = InterfazCalculadora(root)
    root.mainloop()