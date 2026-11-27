"""Casos de frontera y condiciones matemáticas del clasificador REF/RREF."""

import unittest
from fractions import Fraction

from backend.clasificador_forma_escalonada import clasificar_forma_escalonada


class ClasificadorFormaEscalonada(unittest.TestCase):
    def test_matriz_en_ref_y_rref(self):
        resultado = clasificar_forma_escalonada([[1, 0, 2], [0, 1, -3]])
        self.assertTrue(resultado["es_ref"])
        self.assertTrue(resultado["es_rref"])
        self.assertEqual(resultado["numero_pivotes"], 2)

    def test_ref_que_no_es_rref_por_pivote_no_unitario(self):
        resultado = clasificar_forma_escalonada([[1, 2, 0], [0, 2, 1]])
        self.assertTrue(resultado["es_ref"])
        self.assertFalse(resultado["es_rref"])
        self.assertFalse(resultado["condiciones"]["pivotes_iguales_a_uno"]["cumple"])

    def test_no_ref_si_los_pivotes_no_avanzan_a_la_derecha(self):
        resultado = clasificar_forma_escalonada([[0, 1], [1, 0]])
        self.assertFalse(resultado["es_ref"])
        self.assertFalse(resultado["es_rref"])
        self.assertFalse(resultado["condiciones"]["pivotes_avanzan_derecha"]["cumple"])

    def test_no_ref_si_una_fila_nula_precede_una_no_nula(self):
        resultado = clasificar_forma_escalonada([[0, 0, 0], [1, 0, 2]])
        self.assertEqual(resultado["filas_nulas"], [1])
        self.assertFalse(resultado["condiciones"]["filas_nulas_al_final"]["cumple"])
        self.assertFalse(resultado["es_ref"])

    def test_no_ref_si_hay_elementos_no_nulos_debajo_de_un_pivote(self):
        resultado = clasificar_forma_escalonada([[1, 0], [2, 1]])
        self.assertFalse(resultado["condiciones"]["ceros_debajo_pivotes"]["cumple"])
        self.assertFalse(resultado["es_ref"])

    def test_pivotes_distintos_de_uno_pueden_cumplir_ref(self):
        resultado = clasificar_forma_escalonada([[2, 0, 1], [0, -3, 2]])
        self.assertTrue(resultado["es_ref"])
        self.assertFalse(resultado["es_rref"])
        self.assertEqual([p["valor"] for p in resultado["posiciones_pivote"]],
                         [Fraction(2), Fraction(-3)])

    def test_matriz_rectangular_en_ref(self):
        resultado = clasificar_forma_escalonada([[1, 2, 3, 4], [0, 0, 2, 5]])
        self.assertEqual(resultado["dimensiones"], (2, 4))
        self.assertTrue(resultado["es_ref"])
        self.assertFalse(resultado["es_rref"])

    def test_matriz_rectangular_en_rref(self):
        resultado = clasificar_forma_escalonada([[1, 0, 2, 0], [0, 1, 0, 3]])
        self.assertEqual(resultado["dimensiones"], (2, 4))
        self.assertTrue(resultado["es_rref"])

    def test_matriz_completamente_nula_es_ref_y_rref(self):
        resultado = clasificar_forma_escalonada([[0, 0, 0], [0, 0, 0]])
        self.assertTrue(resultado["es_ref"])
        self.assertTrue(resultado["es_rref"])
        self.assertEqual(resultado["numero_pivotes"], 0)
        self.assertEqual(resultado["filas_nulas"], [1, 2])

    def test_columnas_de_ceros_no_impiden_una_rref(self):
        resultado = clasificar_forma_escalonada([[0, 1, 0, 2], [0, 0, 0, 0]])
        self.assertTrue(resultado["es_rref"])
        self.assertEqual(resultado["columnas_pivote"], [1])

    def test_acepta_entradas_negativas_exactamente(self):
        resultado = clasificar_forma_escalonada([[-2, 3, 0], [0, -1, 4]])
        self.assertTrue(resultado["es_ref"])
        self.assertFalse(resultado["es_rref"])
        self.assertEqual(resultado["posiciones_pivote"][0]["valor"], Fraction(-2))

    def test_fracciones_se_clasifican_sin_aproximaciones(self):
        resultado = clasificar_forma_escalonada(
            [[Fraction(1, 2), 1], [0, Fraction(3, 4)]]
        )
        self.assertTrue(resultado["es_ref"])
        self.assertFalse(resultado["es_rref"])
        self.assertEqual(resultado["posiciones_pivote"][1]["valor"], Fraction(3, 4))

    def test_pivote_uno_con_otro_elemento_en_columna_impide_rref(self):
        resultado = clasificar_forma_escalonada([[2, 1], [0, 1], [0, 0]])
        self.assertTrue(resultado["es_ref"])
        self.assertFalse(resultado["es_rref"])
        self.assertFalse(resultado["condiciones"]["pivotes_unicos_en_columna"]["cumple"])

    def test_filas_nulas_al_final_cumplen_la_condicion_ref(self):
        resultado = clasificar_forma_escalonada([[1, 2], [0, 0], [0, 0]])
        self.assertTrue(resultado["condiciones"]["filas_nulas_al_final"]["cumple"])
        self.assertEqual(resultado["filas_nulas"], [2, 3])

    def test_matriz_de_una_fila(self):
        resultado = clasificar_forma_escalonada([[0, -2, 3]])
        self.assertTrue(resultado["es_ref"])
        self.assertEqual(resultado["posiciones_pivote"],
                         [{"fila": 1, "columna": 2, "valor": Fraction(-2)}])

    def test_matriz_de_una_columna(self):
        resultado = clasificar_forma_escalonada([[2], [0]])
        self.assertTrue(resultado["es_ref"])
        self.assertFalse(resultado["es_rref"])
        self.assertEqual(resultado["columnas_pivote"], [0])

    def test_posiciones_legibles_y_columnas_pivote_base_cero(self):
        resultado = clasificar_forma_escalonada([[0, 2, 1], [0, 0, -3]])
        self.assertEqual(resultado["posiciones_pivote"], [
            {"fila": 1, "columna": 2, "valor": Fraction(2)},
            {"fila": 2, "columna": 3, "valor": Fraction(-3)},
        ])
        self.assertEqual(resultado["columnas_pivote"], [1, 2])

    def test_rechaza_matriz_vacia_y_no_rectangular(self):
        with self.assertRaisesRegex(ValueError, "no puede estar vacía"):
            clasificar_forma_escalonada([])
        with self.assertRaisesRegex(ValueError, "rectangular"):
            clasificar_forma_escalonada([[1, 2], [3]])
        with self.assertRaisesRegex(ValueError, "secuencia"):
            clasificar_forma_escalonada([[1, 2], 3])


if __name__ == "__main__":
    unittest.main()
