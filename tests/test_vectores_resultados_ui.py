"""Contratos de presentación de resultados para los módulos vectoriales."""

import inspect
import unittest

from modulos import modulo_operaciones_vectores, modulo_transformaciones, modulo_vectores


class VistasResultadosVectores(unittest.TestCase):
    def test_los_tres_modulos_definen_resumen_datos_y_procedimiento(self):
        for modulo in (modulo_vectores, modulo_operaciones_vectores, modulo_transformaciones):
            with self.subTest(modulo=modulo.__name__):
                fuente = inspect.getsource(modulo._crear_vistas_resultado)
                for vista in ("Resumen", "Datos", "Procedimiento"):
                    self.assertIn(vista, fuente)
                self.assertIn("CTkTabview", fuente)

    def test_las_presentaciones_conservan_el_procedimiento_completo(self):
        for modulo in (modulo_vectores, modulo_operaciones_vectores, modulo_transformaciones):
            with self.subTest(modulo=modulo.__name__):
                fuente = inspect.getsource(modulo._mostrar_resultado)
                self.assertIn("caja_procedimiento.insert", fuente)
                self.assertIn("reemplazar_texto", fuente)

    def test_las_vistas_de_datos_tienen_desplazamiento(self):
        for modulo in (modulo_vectores, modulo_operaciones_vectores, modulo_transformaciones):
            with self.subTest(modulo=modulo.__name__):
                fuente = inspect.getsource(modulo._mostrar_resultado)
                self.assertIn("MarcoDesplazable", fuente)


if __name__ == "__main__":
    unittest.main()
