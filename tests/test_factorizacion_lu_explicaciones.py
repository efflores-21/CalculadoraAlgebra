"""Pruebas de la explicación de pivotes en la factorización LU."""

import unittest
from fractions import Fraction

from backend.factorizacion_lu import factorizar_lu, resolver_lu, resolver_sistema_lu
from backend.operaciones_matriciales import multiplicar_matrices
from modulos.modulo_lu import _texto_clasificacion, _texto_factorizacion, _texto_pasos_registrados, _texto_solucion


class ExplicacionesPivoteLU(unittest.TestCase):
    def test_omite_columna_sin_pivote_y_puede_seleccionar_fuera_diagonal(self):
        A = [[0, 1], [0, 0]]
        L, U, pasos, explicaciones = factorizar_lu(A, incluir_explicaciones=True)

        self.assertEqual(multiplicar_matrices(L, U), A)
        self.assertEqual(U[0][1], Fraction(1))
        skip = next(p for p in explicaciones if "Buscar un pivote válido" in p["objetivo"])
        pivot = next(p for p in explicaciones if "U[1,2]" in p["procedimiento"])
        self.assertIn("columna siguiente", skip["fundamento"])
        self.assertIn("fila activa", pivot["fundamento"])
        self.assertIn("U[1,2]", pivot["procedimiento"])
        self.assertEqual(len(pasos), 0)

    def test_lu_regular_explica_pivote_y_multiplicador(self):
        A = [[2, 1], [4, 3]]
        L, U, _, explicaciones = factorizar_lu(A, incluir_explicaciones=True)

        self.assertEqual(multiplicar_matrices(L, U), A)
        self.assertTrue(any("U[1,1]" in p["procedimiento"] for p in explicaciones))
        self.assertTrue(any("4 / 2 = 2" in p["procedimiento"] for p in explicaciones))
        self.assertFalse(any("columna(s)" in p["fundamento"] for p in explicaciones))
        trazas = []
        resolver_sistema_lu(A, [1, 2], registrar_paso=trazas.append)
        pivote = next(p for p in trazas if "Pivote de la etapa" in p["descripcion"])
        self.assertNotIn("columnas anteriores", pivote["fundamento"])

    def test_lu_regular_presenta_ambas_sustituciones_completas(self):
        A, b = [[2, 1], [4, 3]], [1, 2]
        datos = resolver_lu(A, b)
        texto = "\n".join(_texto_factorizacion(A, datos) + _texto_solucion(datos))

        self.assertIn("Traza técnica:", texto)
        self.assertIn("Explicación pedagógica:", texto)
        self.assertIn("1·y2 + (2)·y1 = 2", texto)
        self.assertIn("y2 = 2 − ((2)(1)) = 0", texto)
        self.assertIn("1·x2 + 0 = 0", texto)
        self.assertIn("2·x1 + (1)·x2 = 1", texto)

    def test_traza_sin_pivoteo_explica_salto_de_columna(self):
        pasos = []
        resolver_sistema_lu([[0, 1], [0, 0]], [1, 0], registrar_paso=pasos.append)

        omision = next(p for p in pasos if "sin pivote" in p["descripcion"])
        pivote = next(p for p in pasos if "Pivote de la etapa" in p["descripcion"])
        self.assertIn("columna siguiente", omision["resultado"])
        self.assertIn("fila activa", pivote["fundamento"])

    def test_pivoteo_parcial_conserva_pa_igual_lu_y_explica_candidatos(self):
        A = [[0, 1], [2, 3]]
        pasos = []
        resultado = resolver_sistema_lu(A, [1, 5], registrar_paso=pasos.append, pivoteo_parcial=True)

        self.assertEqual(multiplicar_matrices(resultado["P"], A), multiplicar_matrices(resultado["L"], resultado["U"]))
        intercambio = next(p for p in pasos if "Intercambio parcial" in p["descripcion"])
        self.assertIn("Candidatos antes del intercambio:", intercambio["procedimiento"])
        self.assertIn("Candidatos antes del intercambio: U[1,1]=0, U[2,1]=2", intercambio["procedimiento"])
        self.assertIn("pivote actual es cero", intercambio["fundamento"])
        pivote = next(p for p in pasos if "Pivote de la etapa 1" in p["descripcion"])
        self.assertIn("Candidatos actuales en U: U[1,1]=2, U[2,1]=0", pivote["procedimiento"])
        self.assertNotIn("U[1,1]=0, U[2,1]=2", pivote["procedimiento"])
        self.assertEqual(intercambio["U"], [[2, 3], [0, 1]])
        texto = "\n".join(_texto_pasos_registrados(pasos) + _texto_clasificacion(A, [1, 5], resultado))
        self.assertIn("EXPLICACIÓN PEDAGÓGICA", texto)
        self.assertIn("1·y1 + 0 = 5", texto)
        self.assertIn("1·y2 + 0 = 1", texto)
        self.assertIn("1·x2 + 0 = 1", texto)
        self.assertIn("2·x1 + (3)·x2 = 5", texto)

    def test_pivoteo_cambia_pivote_no_nulo_si_hay_candidato_mayor(self):
        pasos = []
        resolver_sistema_lu([[1, 1], [5, 6]], [2, 11], registrar_paso=pasos.append, pivoteo_parcial=True)

        intercambio = next(p for p in pasos if "Intercambio parcial" in p["descripcion"])
        pivote = next(p for p in pasos if "Pivote de la etapa 1" in p["descripcion"])
        eliminacion = next(p for p in pasos if "Eliminación" in p["descripcion"])
        self.assertIn("pivote actual no tiene el mayor", intercambio["fundamento"])
        self.assertIn("U[1,1]=1, U[2,1]=5", intercambio["procedimiento"])
        self.assertIn("U[1,1]=5, U[2,1]=1", pivote["procedimiento"])
        self.assertEqual(intercambio["U"], [[5, 6], [1, 1]])
        self.assertEqual(eliminacion["U"], [[5, 6], [0, Fraction(-1, 5)]])

    def test_no_quedan_fallbacks_pedagogicos_genericos(self):
        pasos = []
        resolver_sistema_lu([[0, 1], [2, 3]], [1, 5], registrar_paso=pasos.append, pivoteo_parcial=True)

        for paso in pasos:
            self.assertTrue(all(paso[campo] for campo in ("objetivo", "fundamento", "procedimiento", "resultado")))
            self.assertNotIn("Completar la etapa actual", paso["objetivo"])
            self.assertNotIn("El estado mostrado refleja", paso["resultado"])

    def test_rechaza_cero_que_requiere_permutar_filas(self):
        with self.assertRaisesRegex(ValueError, "pivoteo parcial"):
            factorizar_lu([[0, 1], [2, 3]])


if __name__ == "__main__":
    unittest.main()
