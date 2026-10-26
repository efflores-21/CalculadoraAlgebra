"""Pruebas pedagógicas para (A+B)ᵀ = Aᵀ+Bᵀ."""

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


class ExplicacionesTransposicionSuma(unittest.TestCase):
    def setUp(self):
        self.A = [
            [Fraction(1, 2), Fraction(1), Fraction(0)],
            [Fraction(0), Fraction(-1), Fraction(2)],
        ]
        self.B = [
            [Fraction(1), Fraction(0), Fraction(1)],
            [Fraction(2), Fraction(1), Fraction(0)],
        ]

    def calcular(self, A=None, B=None):
        return calcular_teorema_transposicion(
            TEOREMAS_TRANSPOSICION[1],
            self.A if A is None else A,
            self.B if B is None else B,
        )

    def presentar(self, A=None, B=None):
        A = self.A if A is None else A
        B = self.B if B is None else B
        modulo = SimpleNamespace(
            teorema_transposicion_var=SimpleNamespace(
                get=lambda: TEOREMAS_TRANSPOSICION[1]
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

    def test_resultados_rectangulares_dimensiones_y_pasos_exactos(self):
        pasos, nombre_izq, izquierda, nombre_der, derecha, coincide = self.calcular()

        self.assertEqual(
            [nombre for nombre, _ in pasos],
            ["A + B", "(A + B)ᵀ", "Aᵀ", "Bᵀ", "Aᵀ + Bᵀ"],
        )
        suma_esperada = [
            [Fraction(3, 2), Fraction(1), Fraction(1)],
            [Fraction(2), Fraction(0), Fraction(2)],
        ]
        resultado_esperado = [
            [Fraction(3, 2), Fraction(2)],
            [Fraction(1), Fraction(0)],
            [Fraction(1), Fraction(2)],
        ]
        self.assertEqual(pasos[0][1], suma_esperada)
        self.assertEqual(izquierda, resultado_esperado)
        self.assertEqual(derecha, resultado_esperado)
        self.assertEqual((nombre_izq, nombre_der), ("(A + B)ᵀ", "Aᵀ + Bᵀ"))
        self.assertTrue(coincide)
        self.assertTrue(
            all(
                isinstance(valor, Fraction)
                for _, matriz in pasos
                for fila in matriz
                for valor in fila
            )
        )

    def test_presentacion_desarrolla_sumas_indices_y_compara_todas_las_entradas(self):
        texto = self.presentar()

        secciones = [
            "Dimensiones: A y B son ambas 2×3;",
            "Resultados intermedios calculados:",
            "Lado izquierdo: sumamos A+B entrada por entrada.",
            "Al transponer, la entrada de posición (i,j) pasa a (j,i).",
            "Lado derecho: Aᵀ y Bᵀ son matrices de 3×2;",
            "Comparación entrada por entrada de (A+B)ᵀ y Aᵀ+Bᵀ:",
            "Conclusión:",
        ]
        posiciones = [texto.index(seccion) for seccion in secciones]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertIn("Entrada (1,1): 1/2 + 1 = 3/2", texto)
        self.assertIn("Entrada (2,3): 2 + 0 = 2", texto)
        self.assertIn("(A+B)[1,2] = 1; (A+B)ᵀ[2,1] = 1", texto)
        self.assertIn("Entrada (1,1): 1/2 + 1 = 3/2", texto)
        comparaciones = (
            "Entrada (1,1): 3/2 = 3/2 (coinciden)",
            "Entrada (1,2): 2 = 2 (coinciden)",
            "Entrada (2,1): 1 = 1 (coinciden)",
            "Entrada (2,2): 0 = 0 (coinciden)",
            "Entrada (3,1): 1 = 1 (coinciden)",
            "Entrada (3,2): 2 = 2 (coinciden)",
        )
        for comparacion in comparaciones:
            with self.subTest(comparacion=comparacion):
                self.assertIn(comparacion, texto)
        self.assertIn("se verifica para las matrices ingresadas", texto)
        self.assertIn("no constituye por sí solo una demostración universal", texto)

    def test_sumas_con_fracciones_se_muestran_exactamente(self):
        A = [[Fraction(1, 3), Fraction(1, 2)]]
        B = [[Fraction(1, 6), Fraction(-1, 5)]]
        pasos, _, izquierda, _, derecha, coincide = self.calcular(A, B)

        esperado = [[Fraction(1, 2)], [Fraction(3, 10)]]
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
        self.assertIn("1/3 + 1/6 = 1/2", texto)
        self.assertIn("1/2 + -1/5 = 3/10", texto)

    def test_dimensiones_incompatibles_se_rechazan_por_la_validacion_existente(self):
        B = [[Fraction(1), Fraction(2)]]
        with self.assertRaisesRegex(ValueError, "Dimensiones incompatibles para la suma"):
            self.calcular(B=B)

        with patch("modulos.modulo_propiedades.mensaje_error") as error:
            texto = self.presentar(B=B)
        error.assert_called_once()
        self.assertIsNone(texto)
        self.assertIn("Dimensiones incompatibles para la suma", str(error.call_args.args[0]))


if __name__ == "__main__":
    unittest.main()
