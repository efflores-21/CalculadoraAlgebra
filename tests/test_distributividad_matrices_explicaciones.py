"""Pruebas de las explicaciones de distributividad matricial."""

import unittest
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch

from modulos.modulo_propiedades import (
    ModuloPropiedades,
    TEOREMAS_PRODUCTO,
    _comparar_matrices_distributividad,
    calcular_teorema_producto,
)


class Celda:
    def __init__(self, valor):
        self.valor = str(valor)

    def get(self):
        return self.valor


class ExplicacionesDistributividadMatrices(unittest.TestCase):
    def setUp(self):
        self.A = [
            [Fraction(1, 2), Fraction(1), Fraction(0)],
            [Fraction(0), Fraction(-1), Fraction(2)],
        ]
        self.C = [
            [Fraction(0), Fraction(1)],
            [Fraction(1), Fraction(0)],
            [Fraction(2), Fraction(-1, 2)],
        ]
        self.B_izquierda = [
            [Fraction(1), Fraction(0)],
            [Fraction(2), Fraction(1)],
            [Fraction(0), Fraction(1, 2)],
        ]
        self.B_derecha = [
            [Fraction(1), Fraction(0), Fraction(1)],
            [Fraction(2), Fraction(1), Fraction(0)],
        ]

    def calcular(self, teorema, A, B, C):
        return calcular_teorema_producto(teorema, A, B, C)

    def presentar(self, teorema, A, B, C):
        entradas = {
            nombre: [[Celda(valor) for valor in fila] for fila in matriz]
            for nombre, matriz in (("A", A), ("B", B), ("C", C))
        }
        modulo = SimpleNamespace(
            teorema_producto_var=SimpleNamespace(get=lambda: teorema),
            entradas_producto=entradas,
            _leer_matriz_transposicion=ModuloPropiedades._leer_matriz_transposicion,
            resultado=object(),
        )
        with patch("modulos.modulo_propiedades.reemplazar_texto") as reemplazar:
            ModuloPropiedades.verificar_producto(modulo)
        return reemplazar.call_args.args[1]

    def test_distributividad_izquierda_desarrolla_sumas_productos_y_comparacion(self):
        datos = self.calcular(
            TEOREMAS_PRODUCTO[1], self.A, self.B_izquierda, self.C
        )
        pasos, nombre_izq, izquierda, nombre_der, derecha, cumple, conclusion = datos

        self.assertEqual(
            [nombre for nombre, _ in pasos],
            ["B + C", "A(B+C)", "AB", "AC", "AB + AC"],
        )
        self.assertEqual(pasos[0][1], [[Fraction(1), Fraction(1)], [Fraction(3), Fraction(1)], [Fraction(2), Fraction(0)]])
        self.assertEqual(izquierda, [[Fraction(7, 2), Fraction(3, 2)], [Fraction(1), Fraction(-1)]])
        self.assertEqual(derecha, izquierda)
        self.assertEqual((nombre_izq, nombre_der), ("A(B+C)", "AB+AC"))
        self.assertTrue(cumple)
        self.assertIn("matrices ingresadas", conclusion)
        self.assertTrue(all(isinstance(valor, Fraction) for _, matriz in pasos for fila in matriz for valor in fila))

        texto = self.presentar(TEOREMAS_PRODUCTO[1], self.A, self.B_izquierda, self.C)
        self.assertIn("A (2×3) =", texto)
        self.assertIn("B (3×2) =", texto)
        self.assertIn("C (3×2) =", texto)
        orden = [
            "Primero sumamos B + C entrada por entrada.",
            "Lado izquierdo: calculamos A(B + C).",
            "Lado derecho: calculamos AB.",
            "Calculamos AC.",
            "Sumamos AB + AC entrada por entrada.",
            "Comparación entrada por entrada:",
        ]
        posiciones = [texto.index(marca) for marca in orden]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertIn("Entrada (1,1): 1 + 0 = 1", texto)
        self.assertIn("Entrada (1,1): (1/2)·(1) = 1/2", texto)
        self.assertIn("suma: 1/2 + 3 + 0 = 7/2", texto)
        self.assertIn("Entrada (1,1): 7/2 = 7/2 (coinciden)", texto)
        self.assertIn("A(B+C) y AB+AC coinciden para las matrices ingresadas", texto)
        self.assertIn("no demuestra la ley para todas las matrices", texto)

    def test_distributividad_derecha_desarrolla_sumas_productos_y_comparacion(self):
        datos = self.calcular(
            TEOREMAS_PRODUCTO[2], self.A, self.B_derecha, self.C
        )
        pasos, nombre_izq, izquierda, nombre_der, derecha, cumple, conclusion = datos

        self.assertEqual(
            [nombre for nombre, _ in pasos],
            ["A + B", "(A+B)C", "AC", "BC", "AC + BC"],
        )
        self.assertEqual(pasos[0][1], [[Fraction(3, 2), Fraction(1), Fraction(1)], [Fraction(2), Fraction(0), Fraction(2)]])
        self.assertEqual(izquierda, [[Fraction(3), Fraction(1)], [Fraction(4), Fraction(1)]])
        self.assertEqual(derecha, izquierda)
        self.assertEqual((nombre_izq, nombre_der), ("(A+B)C", "AC+BC"))
        self.assertTrue(cumple)
        self.assertIn("matrices ingresadas", conclusion)
        self.assertTrue(all(isinstance(valor, Fraction) for _, matriz in pasos for fila in matriz for valor in fila))

        texto = self.presentar(TEOREMAS_PRODUCTO[2], self.A, self.B_derecha, self.C)
        orden = [
            "Primero sumamos A + B entrada por entrada.",
            "Lado izquierdo: calculamos (A + B)C.",
            "Lado derecho: calculamos AC.",
            "Calculamos BC.",
            "Sumamos AC + BC entrada por entrada.",
            "Comparación entrada por entrada:",
        ]
        posiciones = [texto.index(marca) for marca in orden]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertIn("Entrada (1,1): 1/2 + 1 = 3/2", texto)
        self.assertIn("Entrada (1,1): (3/2)·(0) = 0", texto)
        self.assertIn("suma: 0 + 1 + 2 = 3", texto)
        self.assertIn("Entrada (2,1): 4 = 4 (coinciden)", texto)
        self.assertIn("(A+B)C y AC+BC coinciden para las matrices ingresadas", texto)
        self.assertIn("no demuestra la ley para todas las matrices", texto)

    def test_comparacion_identifica_posicion_y_valores_que_difieren(self):
        texto = _comparar_matrices_distributividad(
            [[Fraction(1), Fraction(2)]], [[Fraction(1), Fraction(3)]]
        )
        self.assertIn("Entrada (1,1): 1 = 1 (coinciden)", texto)
        self.assertIn("Entrada (1,2): 2 ≠ 3 (difieren)", texto)

    def test_dimensiones_incompatibles_conservan_validaciones(self):
        casos = (
            (TEOREMAS_PRODUCTO[1], self.A, self.B_izquierda, [[Fraction(1), Fraction(0)]]),
            (TEOREMAS_PRODUCTO[1], self.A, self.B_izquierda, self.C[:2]),
            (TEOREMAS_PRODUCTO[2], self.A, [[Fraction(1), Fraction(0)]], self.C),
            (TEOREMAS_PRODUCTO[2], self.A, self.B_derecha, [[Fraction(1), Fraction(0)]]),
        )
        for teorema, A, B, C in casos:
            with self.subTest(teorema=teorema, B=B, C=C):
                with self.assertRaises(ValueError):
                    self.calcular(teorema, A, B, C)


if __name__ == "__main__":
    unittest.main()
