"""Pruebas de transformaciones lineales: linealidad, núcleo, imagen y teorema de la dimensión."""

import unittest
from fractions import Fraction

from backend.transformaciones import analizar, aplicar, esta_en_imagen, verificar_linealidad
from modulos.modulo_transformaciones import _texto_dimension, _texto_nucleo


class TransformacionesLineales(unittest.TestCase):
    def setUp(self):
        self.A = [[1, 2, 0, 1], [2, 4, 1, 3], [3, 6, 1, 4]]
        self.datos = analizar(self.A)

    def test_rango_nulidad_y_teorema_de_la_dimension(self):
        self.assertEqual(self.datos["rango"], 2)
        self.assertEqual(self.datos["nulidad"], 2)
        self.assertTrue(self.datos["cumple_dimension"])
        self.assertEqual(self.datos["pivotes"], [0, 2])

    def test_base_del_nucleo_se_anula(self):
        self.assertEqual(self.datos["base_nucleo"], [[-2, 1, 0, 0], [-1, 0, -1, 1]])
        for vector in self.datos["base_nucleo"]:
            self.assertEqual(aplicar(self.A, vector), [0, 0, 0])

    def test_base_de_la_imagen_son_columnas_pivote_originales(self):
        self.assertEqual(self.datos["base_imagen"], [[1, 2, 3], [0, 1, 1]])

    def test_propiedades_de_suma_y_escalar(self):
        datos = verificar_linealidad(self.A, [1, 0, 1, 0], [0, 1, 0, 1], Fraction(2))
        self.assertTrue(datos["cumple_suma"])
        self.assertTrue(datos["cumple_escalar"])
        self.assertEqual(datos["T(u+v)"], [4, 10, 14])

    def test_combinacion_lineal_e_imagen(self):
        esta, x, _ = esta_en_imagen(self.A, [1, 3, 4])
        self.assertTrue(esta)
        self.assertEqual(aplicar(self.A, x), [1, 3, 4])
        self.assertFalse(esta_en_imagen(self.A, [1, 0, 0])[0])

    def test_inyectiva_y_sobreyectiva(self):
        datos = analizar([[1, 0], [0, 1], [1, 1]])
        self.assertTrue(datos["inyectiva"])
        self.assertFalse(datos["sobreyectiva"])
        self.assertIn("Inyectiva (uno a uno): Sí", "\n".join(_texto_dimension(datos)))

    def test_explicacion_del_nucleo(self):
        texto = "\n".join(_texto_nucleo(self.A, self.datos))
        self.assertIn("x₁ = (-2)·x₂ + (-1)·x₄", texto)
        self.assertIn("Nulidad(T) = número de variables libres = dim Nu(T) = 2", texto)

    def test_dimensiones_incompatibles(self):
        with self.assertRaises(ValueError):
            aplicar(self.A, [1, 2])


if __name__ == "__main__":
    unittest.main()
