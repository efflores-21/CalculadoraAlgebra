import unittest

import main
from modulos._comun import MARCAS
from modulos.teoremas.resumen_teoremas import obtener_resumen
from modulos.modulo_metodos_numericos import ModuloMetodosNumericos


class IntegracionMetodosNumericos(unittest.TestCase):
    def test_menu_tiene_una_sola_opcion_y_clase_asociada(self):
        entradas = [item for item in main.MODULOS if item[0] == "metodos_numericos"]
        self.assertEqual(len(entradas), 1)
        self.assertEqual(entradas[0][1], "Métodos numéricos")
        self.assertIs(main.ModuloMetodosNumericos, ModuloMetodosNumericos)
        self.assertEqual(MARCAS["metodos_numericos"], "P7")

    def test_resumen_teorico_disponible(self):
        resumen = obtener_resumen("metodos_numericos")
        self.assertIn("Bolzano", resumen)
        self.assertIn("PUNTO FLOTANTE", resumen)


if __name__ == "__main__":
    unittest.main()
