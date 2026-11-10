import unittest

from backend.notacion_posicional import binario_a_decimal, decimal_a_binario, descomponer_decimal


class NotacionPosicional(unittest.TestCase):
    def test_ejemplos_de_la_tarea(self):
        self.assertEqual(descomponer_decimal(84506)["suma"], 84506)
        self.assertEqual(decimal_a_binario(243)["binario"], "11110011")
        datos = binario_a_decimal("11110011")
        self.assertEqual(datos["decimal"], 243)
        self.assertEqual(datos["suma"], 243)

    def test_negativos_y_cero(self):
        self.assertEqual(decimal_a_binario(-13)["binario"], "-1101")
        self.assertEqual(binario_a_decimal("-1101")["decimal"], -13)
        self.assertEqual(descomponer_decimal(0)["descomposicion"], "0 × 10^0")

    def test_rechaza_digitos_binarios_invalidos_y_no_enteros(self):
        for valor in ("", "10201", "0b101", "-"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                binario_a_decimal(valor)
        with self.assertRaises(ValueError):
            descomponer_decimal(2.5)


if __name__ == "__main__":
    unittest.main()
