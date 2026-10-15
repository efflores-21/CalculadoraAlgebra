"""Pruebas de la explicación de pivotes en la factorización LU."""

import unittest
from fractions import Fraction

from backend.factorizacion_lu import factorizar_lu, resolver_sistema_lu
from backend.operaciones_matriciales import multiplicar_matrices


class ExplicacionesPivoteLU(unittest.TestCase):
    def test_omite_columna_sin_pivote_y_puede_seleccionar_fuera_diagonal(self):
        A = [[0, 1], [0, 0]]
        L, U, pasos, explicaciones = factorizar_lu(A, incluir_explicaciones=True)

        self.assertEqual(multiplicar_matrices(L, U), A)
        self.assertEqual(U[0][1], Fraction(1))
        skip = next(p for p in explicaciones if "Buscar un pivote válido" in p["objetivo"])
        pivot = next(p for p in explicaciones if "U[1,2]" in p["procedimiento"])
        self.assertIn("columna siguiente", skip["fundamento"])
        self.assertIn("no necesariamente es diagonal", pivot["fundamento"])
        self.assertEqual(len(pasos), 0)

    def test_lu_regular_explica_pivote_y_multiplicador(self):
        A = [[2, 1], [4, 3]]
        L, U, _, explicaciones = factorizar_lu(A, incluir_explicaciones=True)

        self.assertEqual(multiplicar_matrices(L, U), A)
        self.assertTrue(any("U[1,1]" in p["procedimiento"] for p in explicaciones))
        self.assertTrue(any("4 / 2 = 2" in p["procedimiento"] for p in explicaciones))

    def test_traza_sin_pivoteo_explica_salto_de_columna(self):
        pasos = []
        resolver_sistema_lu([[0, 1], [0, 0]], [1, 0], registrar_paso=pasos.append)

        omision = next(p for p in pasos if "sin pivote" in p["descripcion"])
        pivote = next(p for p in pasos if "Pivote de la etapa" in p["descripcion"])
        self.assertIn("siguiente columna", omision["resultado"])
        self.assertIn("columna actual", pivote["fundamento"])

    def test_pivoteo_parcial_conserva_pa_igual_lu_y_explica_candidatos(self):
        A = [[0, 1], [2, 3]]
        pasos = []
        resultado = resolver_sistema_lu(A, [1, 5], registrar_paso=pasos.append, pivoteo_parcial=True)

        self.assertEqual(multiplicar_matrices(resultado["P"], A), multiplicar_matrices(resultado["L"], resultado["U"]))
        intercambio = next(p for p in pasos if "Intercambio parcial" in p["descripcion"])
        self.assertIn("Candidatos:", intercambio["procedimiento"])

    def test_rechaza_cero_que_requiere_permutar_filas(self):
        with self.assertRaisesRegex(ValueError, "pivoteo parcial"):
            factorizar_lu([[0, 1], [2, 3]])


if __name__ == "__main__":
    unittest.main()
