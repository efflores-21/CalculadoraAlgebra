import unittest

from backend.graficador import muestrear_funcion


class MuestreoGrafico(unittest.TestCase):
    def test_muestrea_al_menos_mil_puntos_y_respeta_limites(self):
        datos = muestrear_funcion("x**2", -2, 2, limites_y=(-1, 3))
        self.assertEqual(len(datos["puntos"]), 1200)
        self.assertTrue(datos["segmentos"])
        self.assertTrue(all(-1 <= y <= 3 for segmento in datos["segmentos"] for _, y in segmento))

    def test_excluye_dominio_y_separa_asintota(self):
        radical = muestrear_funcion("sqrt(x)", -1, 1)
        self.assertTrue(any(punto is None for punto in radical["puntos"]))
        racional = muestrear_funcion("1/x", -1, 1)
        self.assertGreaterEqual(len(racional["segmentos"]), 2)

    def test_valida_limites_y_cantidad(self):
        for args in (("x", 1, 1), ("x", 0, 1, 999)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                muestrear_funcion(*args)


if __name__ == "__main__":
    unittest.main()
