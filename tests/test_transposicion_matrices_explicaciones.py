"""Pruebas pedagógicas para (AB)ᵀ = BᵀAᵀ."""

import unittest
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch

from modulos.modulo_propiedades import (
    ModuloPropiedades,
    TEOREMAS_TRANSPOSICION,
    calcular_teorema_transposicion,
)


class Celda:
    def __init__(self, valor):
        self.valor = str(valor)

    def get(self):
        return self.valor


class ExplicacionesTransposicionProducto(unittest.TestCase):
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

    def calcular(self, A=None, B=None):
        return calcular_teorema_transposicion(
            TEOREMAS_TRANSPOSICION[3],
            self.A if A is None else A,
            self.B if B is None else B,
        )

    def presentar(self, A=None, B=None):
        A = self.A if A is None else A
        B = self.B if B is None else B
        modulo = SimpleNamespace(
            teorema_transposicion_var=SimpleNamespace(
                get=lambda: TEOREMAS_TRANSPOSICION[3]
            ),
            entradas_A_transposicion=[
                [Celda(valor) for valor in fila] for fila in A
            ],
            entradas_B_transposicion=[
                [Celda(valor) for valor in fila] for fila in B
            ],
            _leer_matriz_transposicion=ModuloPropiedades._leer_matriz_transposicion,
            resultado=object(),
        )
        with patch("modulos.modulo_propiedades.reemplazar_texto") as reemplazar:
            ModuloPropiedades.verificar_transposicion(modulo)
        return reemplazar.call_args.args[1] if reemplazar.call_args else None

    def test_producto_rectangular_compatible_y_resultados_exactos(self):
        pasos, nombre_izq, izquierda, nombre_der, derecha, coincide = self.calcular()

        self.assertEqual(
            [nombre for nombre, _ in pasos],
            ["AB", "(AB)ᵀ", "Bᵀ", "Aᵀ", "BᵀAᵀ"],
        )
        esperado = [[Fraction(5, 2), Fraction(-2)], [Fraction(1), Fraction(0)]]
        self.assertEqual(izquierda, esperado)
        self.assertEqual(derecha, esperado)
        self.assertEqual((nombre_izq, nombre_der), ("(AB)ᵀ", "BᵀAᵀ"))
        self.assertTrue(coincide)
        self.assertTrue(
            all(
                isinstance(valor, Fraction)
                for _, matriz in pasos
                for fila in matriz
                for valor in fila
            )
        )

    def test_presentacion_desarrolla_dimensiones_indices_y_comparacion(self):
        texto = self.presentar()

        secciones = [
            "Dimensiones: A es 2×3 y B es 3×2.",
            "AB es 2×2; (AB)ᵀ es 2×2; Bᵀ es 2×3; Aᵀ es 3×2;",
            "Resultados intermedios calculados:",
            "Desarrollo del lado izquierdo:",
            "Transponer intercambia los índices:",
            "Desarrollo del lado derecho:",
            "Comparación entrada por entrada de (AB)ᵀ y BᵀAᵀ:",
            "Conclusión:",
        ]
        posiciones = [texto.index(seccion) for seccion in secciones]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertIn("suma: 1/2 + 2 + 0 = 5/2", texto)
        self.assertIn("(AB)[1,2] = 1; (AB)ᵀ[2,1] = 1", texto)
        self.assertIn("suma: 1/2 + 2 + 0 = 5/2", texto)
        self.assertIn("Entrada (1,1): 5/2 = 5/2 (coinciden)", texto)
        self.assertIn("Entrada (1,2): -2 = -2 (coinciden)", texto)
        self.assertIn("Entrada (2,1): 1 = 1 (coinciden)", texto)
        self.assertIn("Entrada (2,2): 0 = 0 (coinciden)", texto)
        self.assertIn("se cumple para las matrices ingresadas", texto)
        self.assertIn("no es por sí solo una demostración universal", texto)

    def test_fracciones_de_entrada_se_conservan_en_ambos_productos(self):
        A = [[Fraction(1, 3), Fraction(1, 2)]]
        B = [[Fraction(3, 2)], [Fraction(2, 5)]]
        pasos, _, izquierda, _, derecha, coincide = self.calcular(A, B)

        esperado = [[Fraction(7, 10)]]
        self.assertEqual(izquierda, esperado)
        self.assertEqual(derecha, esperado)
        self.assertTrue(coincide)
        self.assertTrue(
            all(
                isinstance(valor, Fraction)
                for _, matriz in pasos
                for fila in matriz
                for valor in fila
            )
        )
        texto = self.presentar(A, B)
        self.assertIn("(1/3)·(3/2) = 1/2", texto)
        self.assertIn("(1/2)·(2/5) = 1/5", texto)
        self.assertIn("suma: 1/2 + 1/5 = 7/10", texto)

    def test_producto_incompatible_se_rechaza_con_validacion_existente(self):
        B = [[Fraction(1), Fraction(0)]]
        with self.assertRaises(ValueError):
            self.calcular(B=B)

        with patch("modulos.modulo_propiedades.mensaje_error") as error:
            texto = self.presentar(B=B)
        error.assert_called_once()
        self.assertIsNone(texto)
        self.assertIn("No se puede multiplicar", str(error.call_args.args[0]))


if __name__ == "__main__":
    unittest.main()
