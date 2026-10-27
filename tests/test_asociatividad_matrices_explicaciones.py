"""Pruebas de la explicación pedagógica de asociatividad matricial."""

import unittest
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch

from modulos.modulo_propiedades import (
    ModuloPropiedades,
    TEOREMAS_PRODUCTO,
    calcular_teorema_producto,
)


class Celda:
    def __init__(self, valor):
        self.valor = str(valor)

    def get(self):
        return self.valor


class ExplicacionesAsociatividadMatrices(unittest.TestCase):
    def setUp(self):
        self.A = [
            [Fraction(1, 2), Fraction(1), Fraction(0)],
            [Fraction(0), Fraction(-1), Fraction(2)],
        ]
        self.B = [
            [Fraction(1), Fraction(0)],
            [Fraction(2), Fraction(1)],
            [Fraction(0), Fraction(1, 2)],
        ]
        self.C = [[Fraction(2)], [Fraction(-1)]]

    def calcular(self, A=None, B=None, C=None):
        return calcular_teorema_producto(
            TEOREMAS_PRODUCTO[0],
            self.A if A is None else A,
            self.B if B is None else B,
            self.C if C is None else C,
        )

    def presentar(self):
        entradas = {
            nombre: [[Celda(valor) for valor in fila] for fila in matriz]
            for nombre, matriz in (("A", self.A), ("B", self.B), ("C", self.C))
        }
        modulo = SimpleNamespace(
            teorema_producto_var=SimpleNamespace(get=lambda: TEOREMAS_PRODUCTO[0]),
            entradas_producto=entradas,
            _leer_matriz_transposicion=ModuloPropiedades._leer_matriz_transposicion,
            resultado=object(),
        )
        with patch("modulos.modulo_propiedades.reemplazar_texto") as reemplazar:
            ModuloPropiedades.verificar_producto(modulo)
        return reemplazar.call_args.args[1]

    def test_productos_intermedios_orden_y_resultados_son_exactos(self):
        pasos, nombre_izq, izquierda, nombre_der, derecha, coincide, conclusion = self.calcular()

        self.assertEqual([nombre for nombre, _ in pasos], ["AB", "(AB)C", "BC", "A(BC)"])
        self.assertEqual(pasos[0][1], [[Fraction(5, 2), Fraction(1)], [Fraction(-2), Fraction(0)]])
        self.assertEqual(pasos[1][1], [[Fraction(4)], [Fraction(-4)]])
        self.assertEqual(pasos[2][1], [[Fraction(2)], [Fraction(3)], [Fraction(-1, 2)]])
        self.assertEqual(pasos[3][1], [[Fraction(4)], [Fraction(-4)]])
        self.assertTrue(all(isinstance(valor, Fraction) for _, matriz in pasos for fila in matriz for valor in fila))
        self.assertEqual((nombre_izq, nombre_der), ("(AB)C", "A(BC)"))
        self.assertEqual(izquierda, derecha)
        self.assertTrue(coincide)
        self.assertIn("Para las matrices ingresadas", conclusion)

    def test_presentacion_desarrolla_ambos_lados_y_compara_entradas(self):
        texto = self.presentar()

        self.assertIn("A (2×3) =", texto)
        self.assertIn("B (3×2) =", texto)
        self.assertIn("C (2×1) =", texto)
        pasos = [
            "Lado izquierdo: primero calculamos AB.",
            "Ahora multiplicamos el resultado AB por C.",
            "Lado derecho: primero calculamos BC.",
            "Ahora multiplicamos A por el resultado BC.",
        ]
        posiciones = [texto.index(paso) for paso in pasos]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertIn("Entrada (1,1): (1/2)·(1) = 1/2", texto)
        self.assertIn("suma: 1/2 + 2 + 0 = 5/2", texto)
        self.assertIn("Entrada (1,1): (5/2)·(2) = 5; (1)·(-1) = -1", texto)
        self.assertIn("suma: 5 - 1 = 4", texto)
        self.assertIn("Entrada (3,1): (0)·(2) = 0; (1/2)·(-1) = -1/2", texto)
        self.assertIn("(AB)C =", texto)
        self.assertIn("A(BC) =", texto)
        self.assertIn("Entrada (1,1): 4 = 4", texto)
        self.assertIn("Entrada (2,1): -4 = -4", texto)
        self.assertIn("Conclusión para estas matrices:", texto)
        self.assertIn("((AB)C)ᵢⱼ = Σₖ(Σᵣ aᵢᵣbᵣₖ)cₖⱼ", texto)
        self.assertIn("no es una demostración universal", texto)

    def test_dimensiones_incompatibles_conservan_error_del_producto(self):
        with self.assertRaisesRegex(ValueError, "No se puede calcular AB"):
            self.calcular(B=[[Fraction(1)]])


if __name__ == "__main__":
    unittest.main()
