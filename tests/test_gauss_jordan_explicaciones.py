"""Pruebas de las explicaciones pedagógicas de Gauss-Jordan."""

import unittest
from fractions import Fraction

from backend.clasificador import clasificar_sistema
from backend.eliminacion import resolver_sistema
from modulos.modulo_sistemas import (
    ModuloSistemas, _texto_lectura_rref, _texto_pasos_gauss_jordan,
)


class ExplicacionesGaussJordan(unittest.TestCase):
    def resolver_y_presentar(self, A, b):
        aumentada = [fila[:] + [valor] for fila, valor in zip(A, b)]
        datos = resolver_sistema(aumentada, metodo="gauss-jordan")
        clase = clasificar_sistema(datos["matriz_escalonada"], datos["rango"])
        lineas = _texto_pasos_gauss_jordan(datos["pasos"], len(A[0]))
        lineas.extend(_texto_lectura_rref(datos, clase["tipo"], len(A[0])))
        return datos, clase, "\n".join(lineas)

    def test_solucion_unica_explicita_eliminacion_arriba_y_abajo(self):
        datos, clase, texto = self.resolver_y_presentar([[1, 1], [1, -1]], [3, 1])

        self.assertEqual(clase["tipo"], "Consistente Determinado")
        self.assertEqual(datos["soluciones"], {0: Fraction(2), 1: Fraction(1)})
        self.assertIn("eliminación debajo del pivote", texto)
        self.assertIn("eliminación encima del pivote", texto)
        self.assertIn("No hay variables libres", texto)

    def test_intercambio_muestra_objetivo_candidatos_y_filas(self):
        datos, clase, texto = self.resolver_y_presentar([[0, 1], [1, 1]], [2, 3])

        self.assertEqual(clase["tipo"], "Consistente Determinado")
        self.assertEqual(datos["soluciones"], {0: Fraction(1), 1: Fraction(2)})
        self.assertIn("intercambio para colocar el pivote", texto)
        self.assertIn("Candidatos: 0, 1", texto)
        self.assertIn("F1 ↔ F2", texto)

    def test_soluciones_infinitas_mantienen_variables_libres(self):
        datos, clase, texto = self.resolver_y_presentar([[1, 1], [2, 2]], [3, 6])

        self.assertEqual(clase["tipo"], "Consistente Indeterminado")
        self.assertEqual(datos["variables_libres"], [1])
        self.assertIn("variables libres", texto)
        self.assertEqual(datos["soluciones_generales"][0], (Fraction(3), {1: Fraction(-1)}))

    def test_sistema_incompatible_muestra_fila_contradiccion(self):
        _, clase, texto = self.resolver_y_presentar([[1, 1], [2, 2]], [1, 3])

        self.assertEqual(clase["tipo"], "Inconsistente")
        self.assertIn("representa 0 = -1/2", texto)
        self.assertIn("sistema es incompatible", texto)

    def test_verificacion_sustituye_en_sistema_original(self):
        A, b = [[1, 1], [1, -1]], [3, 1]
        datos, clase, _ = self.resolver_y_presentar(A, b)
        verificacion = "\n".join(ModuloSistemas._verificar_solucion(
            None, A, b, datos["soluciones_generales"], datos["variables_libres"]
        ))

        self.assertEqual(clase["tipo"], "Consistente Determinado")
        self.assertIn("Ec. 1: (1)(2) + (1)(1) = 3  = 3", verificacion)
        self.assertIn("Ec. 2: (1)(2) + (-1)(1) = 1  = 1", verificacion)
        self.assertIn("la solución satisface todas las ecuaciones", verificacion)


if __name__ == "__main__":
    unittest.main()
