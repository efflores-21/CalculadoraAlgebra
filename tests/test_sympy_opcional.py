"""La calculadora debe abrir aunque falte SymPy; solo Newton-Raphson avisa que la necesita."""

import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Simula una computadora sin SymPy: sys.modules["sympy"] = None hace fallar el import.
SIN_SYMPY = (
    "import sys; sys.modules['sympy'] = None; sys.path.insert(0, {raiz!r})\n"
    # Este import es el que antes cerraba la calculadora al iniciar (main.py lo carga).
    "import modulos.modulo_metodos_numericos\n"
    "from backend.newton_raphson import resolver_newton_raphson\n"
    "try:\n"
    "    resolver_newton_raphson('x**2 - 2', 1, 1e-8, 50)\n"
    "except ValueError as error:\n"
    "    print('AVISO:', error)\n"
)


class SympyOpcional(unittest.TestCase):
    def test_sin_sympy_la_calculadora_abre_y_newton_avisa(self):
        entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
        salida = subprocess.run([sys.executable, "-c", SIN_SYMPY.format(raiz=RAIZ)], capture_output=True,
                                text=True, encoding="utf-8", env=entorno, timeout=120)
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertIn("AVISO: Newton-Raphson necesita la librería SymPy", salida.stdout)

    def test_sympy_esta_en_requirements(self):
        with open(os.path.join(RAIZ, "requirements.txt"), encoding="utf-8") as archivo:
            self.assertIn("sympy", archivo.read())


if __name__ == "__main__":
    unittest.main()
