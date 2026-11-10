import unittest

from backend.errores_numericos import analizar_punto_flotante, calcular_errores, propagar_error, resumen_tipos_error


class ErroresNumericos(unittest.TestCase):
    def test_errores_absoluto_relativo_porcentual_y_cero(self):
        datos = calcular_errores(10, 9)
        self.assertEqual(datos["absoluto"], 1)
        self.assertEqual(datos["relativo"], 0.1)
        self.assertEqual(datos["porcentual"], 10)
        cero = calcular_errores(0, 2)
        self.assertIsNone(cero["relativo"])
        self.assertIsNone(cero["porcentual"])

    def test_punto_flotante_epsilon_overflow_y_underflow(self):
        datos = analizar_punto_flotante()
        self.assertFalse(datos["igual_a_03"])
        self.assertGreater(datos["epsilon"], 0)
        self.assertFalse(datos["overflow_es_finito"])
        self.assertEqual(datos["underflow"], 0.0)
        self.assertEqual(datos["perdida"], 0.0)

    def test_propagacion_compara_cambio_real_y_linealizacion(self):
        datos = propagar_error(0.5, 1e-4)
        self.assertAlmostEqual(datos["derivada"], __import__("math").cos(0.5) + 1)
        self.assertGreaterEqual(datos["diferencia_absoluta"], 0)
        self.assertLess(datos["diferencia_absoluta"], 1e-6)

    def test_tipos_distinguen_truncamiento_y_modelado(self):
        tipos = dict(resumen_tipos_error())
        self.assertIn("serie de Taylor", tipos["Truncamiento"])
        self.assertIn("idealizadas", tipos["Modelado"])


if __name__ == "__main__":
    unittest.main()
