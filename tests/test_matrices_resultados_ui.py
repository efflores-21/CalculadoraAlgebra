"""Pruebas de organización de las vistas de operaciones con matrices."""

import unittest

from modulos.modulo_matrices import _NOMBRES_OPERACION, _nombres_datos_operacion


class VistasOperacionesMatrices(unittest.TestCase):
    def test_las_nueve_operaciones_tienen_nombre_de_presentacion(self):
        esperadas = {
            "suma", "resta", "escalar", "producto", "transpuesta",
            "determinante", "inversa", "adjunta", "propiedades",
        }
        self.assertEqual(set(_NOMBRES_OPERACION), esperadas)
        self.assertTrue(all(_NOMBRES_OPERACION.values()))

    def test_datos_muestran_solo_las_matrices_que_participan(self):
        self.assertEqual(_nombres_datos_operacion("suma"), ("A", "B"))
        self.assertEqual(_nombres_datos_operacion("producto"), ("A", "B"))
        self.assertEqual(_nombres_datos_operacion("transpuesta"), ("A",))
        self.assertEqual(_nombres_datos_operacion("determinante"), ("A",))
        self.assertEqual(_nombres_datos_operacion("propiedades"), ("A", "B", "C"))


if __name__ == "__main__":
    unittest.main()
