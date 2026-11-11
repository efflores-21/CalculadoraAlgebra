"""Pruebas de las validaciones de entrada del módulo de métodos numéricos."""

import unittest

from backend.biseccion import resolver_biseccion
from backend.notacion_posicional import binario_a_decimal, decimal_a_binario
from modulos.modulo_metodos_numericos import _fila_tabla, _leer_entero, _leer_real


class EntradasMetodosNumericos(unittest.TestCase):
    def test_entero_invalido_da_mensaje_en_espanol(self):
        for texto in ("abc", "10.5", "--3", ""):
            with self.subTest(texto=texto), self.assertRaisesRegex(ValueError, "debe ser un número entero"):
                _leer_entero(texto, "El máximo de iteraciones")
        with self.assertRaisesRegex(ValueError, "como máximo 30 cifras"):
            _leer_entero("9" * 5000, "El valor decimal")
        self.assertEqual(_leer_entero(" 100 ", "El máximo"), 100)
        self.assertEqual(_leer_entero("-7", "El valor"), -7)

    def test_real_invalido_da_mensaje_en_espanol(self):
        with self.assertRaisesRegex(ValueError, "y mínimo debe ser un número real"):
            _leer_real("abc", "y mínimo")
        self.assertEqual(_leer_real("-2.5", "y mínimo"), -2.5)

    def test_numeros_enormes_se_rechazan_sin_trabar(self):
        with self.assertRaisesRegex(ValueError, "como máximo"):
            binario_a_decimal("1" * 20000)
        with self.assertRaisesRegex(ValueError, "como máximo"):
            decimal_a_binario(10 ** 40)
        self.assertEqual(binario_a_decimal("1" * 100)["decimal"], 2 ** 100 - 1)

    def test_tabla_de_biseccion_alineada(self):
        datos = resolver_biseccion("x**3 - 2*x - 5", 2, 3, 0.0001, 100)
        self.assertAlmostEqual(datos["raiz"], 2.0945, places=3)
        encabezado = _fila_tabla(("k", "a", "b", "f(a)", "f(b)", "xr", "f(xr)", "Eb", "Ea", "εa"))
        fila = _fila_tabla((1, "2", "3", "-1", "16", "2.5", "5.625", "0.5", "—", "—"))
        self.assertEqual(len(encabezado), len(fila))


if __name__ == "__main__":
    unittest.main()
