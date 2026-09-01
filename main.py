"""
Punto de entrada principal para ejecutar la calculadora.
"""

from frontend.interfaz import InterfazCalculadora

if __name__ == "__main__":
    app = InterfazCalculadora()
    app.mainloop()