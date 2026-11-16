"""Pruebas de Jacobi y Gauss-Seidel (Tarea 8): convergencia, reordenamiento y advertencias."""

import unittest
from fractions import Fraction

import main
from backend.metodos_iterativos import (
    buscar_reordenamiento,
    es_diagonal_dominante,
    iterar,
    resolver,
    residuo,
    solucion_referencia,
)
from modulos._comun import MARCAS
from modulos.modulo_iterativos import CASOS, resumen, texto_resultado

A1 = [[10, -1, 2, 0], [-1, 11, -1, 3], [2, -1, 10, -1], [0, 3, -1, 8]]
B1 = [6, 25, -11, 15]


class JacobiGaussSeidel(unittest.TestCase):
    def test_caso_1_converge_y_gauss_seidel_es_mas_rapido(self):
        datos = resolver(A1, B1, [0, 0, 0, 0], 1e-6, 100)
        self.assertTrue(datos["dominante"])
        for metodo in ("jacobi", "gauss_seidel"):
            r = datos[metodo]
            self.assertEqual(r["estado"], "converge")
            for xi, esperado in zip(r["x"], (1, 2, -1, 1)):
                self.assertAlmostEqual(xi, esperado, delta=1e-5)
            self.assertLess(r["residuo"], 1e-4)
        self.assertEqual(datos["comparacion"]["mas_rapido"], "gauss_seidel")
        self.assertEqual(datos["referencia"], [1, 2, -1, 1])

    def test_jacobi_usa_solo_la_iteracion_anterior(self):
        r = iterar("jacobi", [[4.0, 1.0], [2.0, 5.0]], [9.0, 12.0], [0.0, 0.0], 1e-12, 1)
        # Con x⁽⁰⁾ = 0: x₁ = 9/4 y x₂ = 12/5 (no usa el x₁ recién calculado).
        self.assertEqual(r["tabla"][0]["x"], [9 / 4, 12 / 5])

    def test_gauss_seidel_usa_el_valor_recien_calculado(self):
        r = iterar("gauss_seidel", [[4.0, 1.0], [2.0, 5.0]], [9.0, 12.0], [0.0, 0.0], 1e-12, 1)
        # x₁ = 9/4 y luego x₂ = (12 − 2·9/4)/5 con el x₁ nuevo.
        self.assertEqual(r["tabla"][0]["x"], [9 / 4, (12 - 2 * 9 / 4) / 5])

    def test_criterio_de_parada_y_error_en_la_tabla(self):
        r = iterar("jacobi", [[4.0, 1.0], [2.0, 5.0]], [9.0, 12.0], [0.0, 0.0], 1e-8, 500)
        self.assertEqual(r["estado"], "converge")
        self.assertLessEqual(r["tabla"][-1]["error"], 1e-8)
        self.assertGreater(r["tabla"][-2]["error"], 1e-8)

    def test_caso_2_reordena_ceros_de_la_diagonal(self):
        A, b = [[0, 1, 3], [5, 0, 2], [1, 4, 0]], [11, 11, 9]
        datos = resolver(A, b, [0, 0, 0], 1e-8, 100)
        self.assertEqual(datos["orden"], [1, 2, 0])
        self.assertEqual(datos["ceros_originales"], [0, 1, 2])
        self.assertTrue(datos["dominante"])
        self.assertEqual(datos["gauss_seidel"]["estado"], "converge")

    def test_sin_reordenar_los_ceros_detienen_el_calculo(self):
        with self.assertRaisesRegex(ValueError, "ceros en la diagonal"):
            resolver([[0, 1], [1, 0]], [1, 1], [0, 0], 1e-6, 10, reordenar=False)

    def test_no_se_fuerza_un_reordenamiento_que_no_existe(self):
        orden, motivo = buscar_reordenamiento([[0.0, 0.0], [1.0, 1.0]])
        self.assertIsNone(orden)
        self.assertIn("No se encontró", motivo)
        with self.assertRaisesRegex(ValueError, "ceros en la diagonal"):
            resolver([[0, 0], [1, 1]], [1, 1], [0, 0], 1e-6, 10)

    def test_caso_3_no_converge_y_lo_advierte(self):
        datos = resolver([[1, 3], [1, 2]], [4, 3], [0, 0], 1e-6, 50)
        self.assertFalse(datos["dominante"])
        for metodo in ("jacobi", "gauss_seidel"):
            self.assertNotEqual(datos[metodo]["estado"], "converge")
            self.assertTrue(datos[metodo]["error_creciente"])
        texto = texto_resultado(datos)
        self.assertIn("NO prueba que diverjan", texto)
        self.assertIn("ninguno converge", resumen(datos))

    def test_divergencia_fuerte_se_detiene_sin_valores_no_finitos(self):
        r = iterar("gauss_seidel", [[1.0, 1000.0], [1000.0, 1.0]], [1.0, 1.0], [0.0, 0.0], 1e-6, 10000)
        self.assertEqual(r["estado"], "diverge")
        self.assertLess(r["iteraciones"], 100)

    def test_no_dominante_pero_converge(self):
        # Simétrica definida positiva sin dominancia estricta: Gauss-Seidel converge igual.
        A = [[2, 1, 1], [1, 2, 1], [1, 1, 2]]
        self.assertFalse(es_diagonal_dominante(A))
        datos = resolver(A, [4, 4, 4], [0, 0, 0], 1e-8, 500, reordenar=False)
        self.assertEqual(datos["gauss_seidel"]["estado"], "converge")

    def test_validaciones_de_entrada(self):
        casos = [([[1, 2]], [1], [0], 1e-6, 10, "cuadrada"), ([[1]], [1, 2], [0], 1e-6, 10, "b debe"),
                 ([[1]], [1], [0, 0], 1e-6, 10, "inicial"), ([[1]], [1], [0], 0, 10, "positiva"),
                 ([[1]], [1], [0], -1, 10, "positiva"), ([[1]], [1], [0], 1e-6, 0, "máximo"),
                 ([[1]], [1], [0], 1e-6, 10001, "máximo"), ([[1]], [1], [0], "abc", 10, "número")]
        for A, b, x0, tol, maximo, texto in casos:
            with self.subTest(texto=texto), self.assertRaisesRegex(ValueError, texto):
                resolver(A, b, x0, tol, maximo)

    def test_referencia_y_residuo(self):
        self.assertEqual(solucion_referencia([[2, 1], [1, 3]], [3, 4]), [Fraction(1), Fraction(1)])
        self.assertIsNone(solucion_referencia([[1, 2], [2, 4]], [1, 2]))
        self.assertEqual(residuo([[2.0, 1.0], [1.0, 3.0]], [1.0, 1.0], [3.0, 4.0]), 0)

    def test_casos_de_la_guia_y_menu(self):
        self.assertEqual(len(CASOS), 3)
        self.assertEqual(MARCAS["iterativos"], "P8")
        self.assertIn("iterativos", [clave for clave, *_ in main.MODULOS])


if __name__ == "__main__":
    unittest.main()
