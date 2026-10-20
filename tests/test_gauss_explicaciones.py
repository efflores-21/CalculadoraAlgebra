"""Pruebas de la explicación pedagógica del método de Gauss."""

import unittest
from fractions import Fraction

from backend.clasificador import clasificar_sistema
from backend.eliminacion import resolver_sistema
from modulos.modulo_sistemas import (
    ModuloSistemas, _texto_pasos_gauss, _texto_sustitucion_gauss,
)


class ExplicacionesGauss(unittest.TestCase):
    def _resolver_y_presentar(self, A, b):
        aumentada = [fila[:] + [valor] for fila, valor in zip(A, b)]
        datos = resolver_sistema(aumentada, metodo="gauss")
        clase = clasificar_sistema(datos["matriz_escalonada"], datos["rango"])
        lineas = _texto_pasos_gauss(datos["pasos"], datos["matriz_escalonada"], len(A[0]))
        lineas.extend(_texto_sustitucion_gauss(datos, len(A[0])))
        lineas.extend(ModuloSistemas._verificar_solucion(
            None, A, b, datos["soluciones_generales"], datos["variables_libres"]
        ))
        return datos, clase, "\n".join(lineas)

    def test_pivoteo_multiplicador_sustitucion_y_verificacion_exactos(self):
        A = [[0, 2], [3, 1]]
        b = [1, 7]
        datos, clase, texto = self._resolver_y_presentar(A, b)

        self.assertEqual(clase["tipo"], "Consistente Determinado")
        self.assertEqual(datos["soluciones"], {0: Fraction(13, 6), 1: Fraction(1, 2)})
        self.assertIn("selección e intercambio de pivote", texto)
        self.assertIn("Candidatos en la columna: 0, 3.", texto)
        self.assertIn("SUSTITUCIÓN HACIA ATRÁS:", texto)
        self.assertIn("Resultado: la solución satisface todas las ecuaciones.", texto)
        x = [datos["soluciones"][j] for j in range(2)]
        self.assertEqual([sum(Fraction(A[i][j]) * x[j] for j in range(2)) for i in range(2)], b)

    def test_eliminacion_muestra_pivote_multiplicador_y_calculo_de_fila(self):
        A = [[2, 1], [5, 3]]
        b = [1, 2]
        datos, clase, texto = self._resolver_y_presentar(A, b)

        self.assertEqual(clase["tipo"], "Consistente Determinado")
        self.assertEqual(datos["soluciones"], {0: Fraction(1, 1), 1: Fraction(-1, 1)})
        self.assertIn("Pivote: a1,1 = 1", texto)
        self.assertIn("Multiplicador: m = 2 / 1 = 2", texto)
        self.assertIn("Cálculo de la fila:", texto)
        self.assertIn("x₁ = (2/5 − ((3/5)(-1))) / 1 = 1", texto)
        x = [datos["soluciones"][j] for j in range(2)]
        self.assertEqual([sum(Fraction(A[i][j]) * x[j] for j in range(2)) for i in range(2)], b)

    def test_sistema_indeterminado_conserva_variable_libre(self):
        datos, clase, texto = self._resolver_y_presentar([[1, 2]], [3])

        self.assertEqual(clase["tipo"], "Consistente Indeterminado")
        self.assertIn("variables libres permanecen como parámetros", texto)
        self.assertIn("x₁ = 3 - 2*t₂", texto)

    def test_sistema_inconsistente_no_presenta_sustitucion_unica(self):
        A, b = [[1, 1], [2, 2]], [1, 3]
        aumentada = [fila[:] + [valor] for fila, valor in zip(A, b)]
        datos = resolver_sistema(aumentada, metodo="gauss")
        clase = clasificar_sistema(datos["matriz_escalonada"], datos["rango"])

        self.assertEqual(clase["tipo"], "Inconsistente")
        self.assertTrue(all(fila[0] == 0 and fila[1] == 0 and fila[2] != 0
                            for fila in datos["matriz_escalonada"][datos["rango"]:]))


if __name__ == "__main__":
    unittest.main()
