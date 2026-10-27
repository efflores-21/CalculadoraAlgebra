"""Pruebas de la explicación de linealidad de matriz por vector."""

import unittest
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch

from modulos.modulo_propiedades import ModuloPropiedades


class Celda:
    def __init__(self, valor):
        self.valor = str(valor)

    def get(self):
        return self.valor


class ExplicacionesLinealidadMatrizVector(unittest.TestCase):
    def presentar(self):
        matriz = [
            [Fraction(1, 2), Fraction(1), Fraction(-1)],
            [Fraction(2), Fraction(0), Fraction(1, 3)],
        ]
        u = [Fraction(2), Fraction(-1), Fraction(3)]
        v = [Fraction(1), Fraction(2), Fraction(0)]
        modulo = SimpleNamespace(
            entradas_A=[[Celda(valor) for valor in fila] for fila in matriz],
            entradas_u=[Celda(valor) for valor in u],
            entradas_v=[Celda(valor) for valor in v],
            entry_c=Celda(Fraction(-3, 2)),
            _leer_vector=lambda celdas, nombre: [Fraction(celda.get()) for celda in celdas],
            resultado=object(),
        )

        with patch("modulos.modulo_propiedades.reemplazar_texto") as reemplazar:
            ModuloPropiedades.verificar(modulo)
        return reemplazar.call_args.args[1]

    def test_desarrolla_aditividad_homogeneidad_y_compara_resultados_exactos(self):
        texto = self.presentar()

        self.assertIn("dimensión 2×3", texto)
        self.assertIn("Componente 1: 2 + 1 = 3", texto)
        self.assertIn("(1/2)(3) = 3/2; (1)(1) = 1; (-1)(3) = -3", texto)
        self.assertIn("suma: 3/2 + 1 - 3 = -1/2", texto)
        self.assertIn("Au+Av = (-1/2, 7)", texto)
        self.assertIn("(1/2)(2) = 1; (1)(-1) = -1; (-1)(3) = -3", texto)
        self.assertIn("(1/2)(1) = 1/2; (1)(2) = 2; (-1)(0) = 0", texto)
        self.assertIn("Componente 1: (-3/2)(2) = -3", texto)
        self.assertIn("Componente 1: (-3/2)(-3) = 9/2", texto)
        self.assertIn("A(cu) = (9/2, -15/2)", texto)
        self.assertIn("c(Au) = (9/2, -15/2)", texto)
        self.assertIn("-> SE CUMPLE", texto)
        self.assertIn("no sustituye una demostración", texto)


if __name__ == "__main__":
    unittest.main()
