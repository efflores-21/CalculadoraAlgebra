import unittest

from backend.biseccion import iteraciones_teoricas, resolver_biseccion


class Biseccion(unittest.TestCase):
    def test_casos_del_pdf_alcanzan_tolerancia(self):
        casos = [("x**3-2*x-5", 2, 3, 2.09455148), ("cos(x)-x", 0, 1, 0.73908513),
                 ("x**2-2", 1, 2, 1.41421356), ("x**3+x-1", 0, 1, 0.68232780)]
        for funcion, a, b, referencia in casos:
            with self.subTest(funcion=funcion):
                datos = resolver_biseccion(funcion, a, b, 1e-4, 100)
                self.assertTrue(datos["alcanzada_tolerancia"])
                self.assertAlmostEqual(datos["raiz"], referencia, delta=1e-4)
                self.assertLessEqual(datos["cota_error"], 1e-4)
                self.assertIn("continuidad", datos["advertencia"])

    def test_raiz_en_extremo_y_raiz_exacta_intermedia(self):
        self.assertEqual(resolver_biseccion("x**2-1", 1, 2, 1e-4, 100)["raiz"], 1)
        self.assertEqual(resolver_biseccion("x", -1, 1, 1e-6, 10)["raiz"], 0)

    def test_intervalo_sin_cambio_de_signo(self):
        with self.assertRaisesRegex(ValueError, "no presenta cambio de signo"):
            resolver_biseccion("x**2+1", -1, 1, 1e-4, 100)

    def test_discontinuidad_en_punto_medio_se_advierte(self):
        with self.assertRaisesRegex(ValueError, "discontinuidad"):
            resolver_biseccion("1/x", -1, 1, 1e-4, 100)

    def test_maximo_insuficiente_y_traza_previa_a_actualizar(self):
        datos = resolver_biseccion("x**2-2", 1, 2, 1e-12, 2)
        self.assertFalse(datos["alcanzada_tolerancia"])
        self.assertIn("máximo", datos["motivo"])
        self.assertEqual(datos["tabla"][0]["a"], 1)
        self.assertEqual(datos["tabla"][0]["b"], 2)
        self.assertEqual(datos["tabla"][0]["intervalo_siguiente"], (1.0, 1.5))
        self.assertEqual(iteraciones_teoricas(0, 1, 1e-4), 14)
        self.assertIsNone(datos["tabla"][0]["error_relativo_aprox"])
        self.assertIsNotNone(datos["tabla"][1]["error_relativo_aprox"])

    def test_validaciones_de_intervalo_tolerancia_y_limite(self):
        for args in (("x", 2, 1, 0.1, 10), ("x", 0, 1, 0, 10), ("x", 0, 1, 0.1, 0), ("x", 0, 1, 0.1, 1.5), ("x", 0, 1, 0.1, 10001)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                resolver_biseccion(*args)


if __name__ == "__main__":
    unittest.main()
