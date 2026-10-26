"""Pruebas pedagógicas de la resolución por matriz inversa."""

import unittest
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch

from backend.matrices import invertir_gauss_jordan
from modulos._comun import formatear_matriz
from modulos.modulo_sistemas import ModuloSistemas, _resolver_por_matriz_inversa


class ExplicacionesMatrizInversa(unittest.TestCase):
    def presentar(self, A, b):
        with patch("modulos.modulo_sistemas.reemplazar_texto") as reemplazar:
            ModuloSistemas._mostrar_inversa(SimpleNamespace(resultado=object()), A, b)
        return reemplazar.call_args.args[1]

    def test_singularidad_se_explica_y_no_intenta_formar_la_solucion(self):
        texto = self.presentar([[1, 2], [2, 4]], [3, 6])

        self.assertIn("A⁻¹ existe exactamente cuando det(A) ≠ 0", texto)
        self.assertIn("A es singular: sus filas o columnas son dependientes", texto)
        self.assertIn("no existe A⁻¹", texto)
        self.assertNotIn("Solución x =", texto)

    def test_intercambio_de_filas_y_pasos_de_gauss_jordan_se_interpretan(self):
        A = [[0, 2], [1, 1]]
        b = [1, 1]
        texto = self.presentar(A, b)

        self.assertIn("[A|I] → [I|A⁻¹]", texto)
        self.assertIn("fila aumentada completa", texto)
        self.assertIn("EA=I y B=E", texto)
        self.assertIn("Como A es cuadrada, E=A⁻¹", texto)
        self.assertIn("Intercambiar F1 y F2", texto)
        self.assertIn("la fila 2 aporta 1 en esa columna", texto)
        self.assertIn("Matriz aumentada antes de la operación:", texto)
        self.assertIn("Matriz aumentada después del intercambio:", texto)
        self.assertIn("Cálculo de cada entrada de la fila:", texto)
        self.assertIn("columna 2: 2 / 2 = 1", texto)
        self.assertIn("columna 3: 1 / 2 = 1/2", texto)
        self.assertIn("columna 2: 1 - (1)(1) = 0", texto)
        self.assertIn("columna 3: 0 - (1)(1/2) = -1/2", texto)

        _, pasos = invertir_gauss_jordan(A)
        self.assertIn("Forma reducida final [I|A⁻¹]:", texto)
        self.assertIn("no es una operación adicional", texto)
        self.assertNotIn("Fdestino", texto)
        cursor = 0
        for indice, (descripcion, estado) in enumerate(pasos[1:], 1):
            if descripcion.startswith("Forma reducida final"):
                posicion_paso = texto.index(f"{descripcion}:", cursor)
                posicion_estado = texto.index(formatear_matriz(estado), posicion_paso)
            else:
                posicion_paso = texto.index(f"Paso {indice}: {descripcion}.", cursor)
                posicion_despues = texto.index(
                    "Matriz aumentada después", posicion_paso
                )
                posicion_estado = texto.index(
                    formatear_matriz(estado), posicion_despues
                )
            self.assertGreaterEqual(posicion_estado, posicion_paso)
            cursor = posicion_estado + len(formatear_matriz(estado))

    def test_producto_y_verificacion_conservan_fracciones_exactas(self):
        A = [[2, 1], [1, 2]]
        b = [1, 0]
        inversa, _, solucion, producto_ax = _resolver_por_matriz_inversa(A, b)
        texto = self.presentar(A, b)

        self.assertEqual(inversa, [[Fraction(2, 3), Fraction(-1, 3)],
                                   [Fraction(-1, 3), Fraction(2, 3)]])
        self.assertEqual(solucion, [Fraction(2, 3), Fraction(-1, 3)])
        self.assertEqual(producto_ax, [Fraction(1), Fraction(0)])
        self.assertIn("x₁ = (2/3)(1) + (-1/3)(0)", texto)
        self.assertIn("Productos: 2/3 + 0 = 2/3", texto)
        self.assertIn("Por tanto, x₁ = 2/3", texto)
        self.assertIn("x₂ = (-1/3)(1) + (2/3)(0)", texto)
        self.assertIn("Productos: -1/3 + 0 = -1/3", texto)
        self.assertIn("Por tanto, x₂ = -1/3", texto)
        self.assertIn("el resultado de la fila i debe coincidir con bᵢ", texto)
        self.assertIn("Ecuación 1: (2)(2/3) + (1)(-1/3)", texto)
        self.assertIn("Productos: 4/3 + -1/3 = 1; = 1", texto)
        self.assertIn("Ecuación 2: (1)(2/3) + (2)(-1/3)", texto)
        self.assertIn("Productos: 2/3 + -2/3 = 0; = 0", texto)
        self.assertIn("Ax = b: Se cumple", texto)
        self.assertIn("la solución satisface todas las ecuaciones del sistema", texto)


if __name__ == "__main__":
    unittest.main()
