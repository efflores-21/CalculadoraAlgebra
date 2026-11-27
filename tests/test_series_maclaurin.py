"""Pruebas matemáticas y de validación para la serie de Maclaurin."""

import math
import unittest
from fractions import Fraction
from unittest.mock import patch

from backend import series_maclaurin as maclaurin


class SeriesMaclaurin(unittest.TestCase):
    def calcular(self, expresion, x=1, n=5):
        return maclaurin.calcular_maclaurin(expresion, x, n)

    def test_exp_tiene_coeficientes_factoriales(self):
        datos = self.calcular("exp(x)")
        self.assertEqual([t["coeficiente"] for t in datos["terminos"]],
                         [1, 1, Fraction(1, 2), Fraction(1, 6), Fraction(1, 24)])

    def test_seno_incluye_coeficientes_nulos(self):
        datos = self.calcular("sin(x)", n=6)
        self.assertEqual([t["coeficiente"] for t in datos["terminos"]],
                         [0, 1, 0, Fraction(-1, 6), 0, Fraction(1, 120)])

    def test_coseno_alterna_terminos_pares(self):
        datos = self.calcular("cos(x)", n=6)
        self.assertEqual([t["coeficiente"] for t in datos["terminos"]],
                         [1, 0, Fraction(-1, 2), 0, Fraction(1, 24), 0])

    def test_polinomio_se_reproduce_hasta_el_orden_incluido(self):
        datos = self.calcular("x**3 - 2*x + 4", n=5)
        x = maclaurin.sp.Symbol("x", real=True)
        self.assertEqual(datos["polinomio"].expand(), x**3 - 2*x + 4)

    def test_primer_coeficiente_no_nulo_en_orden_superior(self):
        datos = self.calcular("x**4", n=5)
        self.assertEqual([t["coeficiente"] for t in datos["terminos"]], [0, 0, 0, 0, 1])

    def test_coeficientes_racionales_se_conservan_exactos(self):
        datos = self.calcular("x/2 + x**2/3", n=3)
        self.assertEqual([t["coeficiente"] for t in datos["terminos"]], [0, Fraction(1, 2), Fraction(1, 3)])

    def test_evaluacion_en_cero_coincide_con_termino_constante(self):
        datos = self.calcular("exp(x)", x=0, n=4)
        self.assertEqual(datos["aproximacion"], 1)

    def test_aproximacion_de_exp_con_cuatro_terminos(self):
        datos = self.calcular("exp(x)", x=1, n=4)
        self.assertAlmostEqual(datos["aproximacion"], 8/3)

    def test_valor_real_se_evalua_con_el_parser_existente(self):
        self.assertAlmostEqual(self.calcular("exp(x)")["valor_real"], math.e)

    def test_error_absoluto_es_diferencia_no_negativa(self):
        datos = self.calcular("exp(x)", x=1, n=2)
        self.assertAlmostEqual(datos["error_absoluto"], math.e - 2)

    def test_error_relativo_porcentual(self):
        datos = self.calcular("exp(x)", x=1, n=2)
        self.assertAlmostEqual(datos["error_relativo_porcentual"], (math.e - 2) / math.e * 100)

    def test_error_relativo_indefinido_si_valor_real_es_cero(self):
        datos = self.calcular("x - 1", x=1, n=1)
        self.assertEqual(datos["valor_real"], 0)
        self.assertIsNone(datos["error_relativo_porcentual"])

    def test_una_cantidad_de_terminos_es_valida(self):
        datos = self.calcular("exp(x)", n=1)
        self.assertEqual(datos["numero_terminos"], 1)
        self.assertEqual(datos["polinomio"], 1)

    def test_rechaza_cantidades_de_terminos_invalidas(self):
        for n in (0, -1, 31, 1.5, True, "5"):
            with self.subTest(n=n), self.assertRaises(ValueError):
                maclaurin.calcular_maclaurin("x", 1, n)

    def test_rechaza_funcion_no_permitida(self):
        with self.assertRaises(ValueError):
            self.calcular("__import__('os')")

    def test_rechaza_sintaxis_invalida(self):
        with self.assertRaises(ValueError):
            self.calcular("sin(")

    def test_rechaza_funcion_no_definida_en_cero(self):
        with self.assertRaisesRegex(ValueError, "no está definida.*x = 0"):
            self.calcular("1/x")

    def test_rechaza_logaritmo_no_definido_en_cero(self):
        with self.assertRaisesRegex(ValueError, "no está definida.*x = 0"):
            self.calcular("log(x)")

    def test_rechaza_derivada_singular_en_cero(self):
        with self.assertRaises(ValueError):
            self.calcular("sqrt(x)", n=2)

    def test_rechaza_funcion_no_diferenciable_en_cero(self):
        with self.assertRaisesRegex(ValueError, "derivada de orden 1 no existe"):
            self.calcular("abs(x)", n=2)

    def test_funcion_combinada_exponencial_y_polinomio(self):
        datos = self.calcular("x**2*exp(x)", x=1, n=6)
        x = maclaurin.sp.Symbol("x", real=True)
        self.assertEqual(datos["polinomio"].expand(), x**2 + x**3 + x**4/2 + x**5/6)

    def test_avisa_si_la_funcion_no_se_evalua_en_el_x_solicitado(self):
        datos = self.calcular("log(1+x)", x=-2, n=4)
        self.assertIsNone(datos["valor_real"])
        self.assertIn("no se pudo evaluar", datos["aviso_evaluacion"])

    def test_informa_que_convergencia_depende_de_funcion_y_punto(self):
        datos = self.calcular("1/(1-x)", x=2, n=4)
        self.assertIn("radio de convergencia", datos["nota_convergencia"])
        self.assertIn("no converge", datos["aviso_convergencia"])
        self.assertEqual(datos["aproximacion"], 15)

    def test_validacion_finita_de_x(self):
        for x in (float("nan"), float("inf"), True, "abc"):
            with self.subTest(x=x), self.assertRaises(ValueError):
                self.calcular("x", x=x)

    def test_mensaje_claro_si_sympy_no_esta_disponible(self):
        with patch.object(maclaurin, "sp", None), self.assertRaisesRegex(ValueError, "necesita SymPy"):
            maclaurin.calcular_maclaurin("x", 0, 1)


if __name__ == "__main__":
    unittest.main()
