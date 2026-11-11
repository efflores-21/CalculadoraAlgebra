import unittest

from backend.funciones import compilar_funcion


class EvaluadorSeguro(unittest.TestCase):
    def test_operaciones_constantes_y_funciones(self):
        self.assertAlmostEqual(compilar_funcion("sin(pi/2) + x**2 - abs(-1)")(2), 4)
        self.assertAlmostEqual(compilar_funcion("log(e*x, e)")(1), 1)
        self.assertAlmostEqual(compilar_funcion("sqrt(4)+asin(0)+acos(1)+atan(0)")(0), 2)

    def test_rechaza_codigo_atributos_nombres_y_nodos(self):
        for expresion in ("__import__('os')", "x.__class__", "open('x')", "y+1", "[x]", "(lambda: 1)()"):
            with self.subTest(expresion=expresion), self.assertRaises(ValueError):
                compilar_funcion(expresion)

    def test_rechaza_sintaxis_complejidad_y_potencia_excesiva(self):
        with self.assertRaisesRegex(ValueError, "sintaxis"):
            compilar_funcion("x +")
        with self.assertRaisesRegex(ValueError, "exponente"):
            compilar_funcion("x**1001")
        with self.assertRaisesRegex(ValueError, "larga"):
            compilar_funcion("x" * 501)

    def test_controla_dominio_division_y_valores_no_finitos(self):
        for expresion in ("1/x", "sqrt(x)", "log(x)", "exp(1000)", "(-1)**0.5"):
            funcion = compilar_funcion(expresion)
            with self.subTest(expresion=expresion), self.assertRaises(ValueError):
                funcion(0 if expresion in ("1/x", "log(x)", "exp(1000)") else -1)


if __name__ == "__main__":
    unittest.main()
