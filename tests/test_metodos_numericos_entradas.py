"""Pruebas de las validaciones de entrada del módulo de métodos numéricos."""

import unittest

from backend.biseccion import resolver_biseccion
from backend.notacion_posicional import binario_a_decimal, decimal_a_binario, descomponer_decimal
from modulos.modulo_metodos_numericos import _filas_a_mostrar, _leer_entero, _leer_real


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

    def test_biseccion_para_en_el_limite_de_precision(self):
        datos = resolver_biseccion("x**2-2", 1, 2, 1e-300, 10000)
        self.assertLess(datos["iteraciones"], 100)
        self.assertFalse(datos["alcanzada_tolerancia"])
        self.assertIn("precisión", datos["motivo"])

    def test_biseccion_avisa_asintota_y_no_avisa_raiz_normal(self):
        for funcion, a, b in (("tan(x)", 1, 2), ("1/(x-0.3)", 0, 1)):
            with self.subTest(funcion=funcion):
                self.assertIn("discontinuidad", resolver_biseccion(funcion, a, b, 1e-6, 100)["aviso_discontinuidad"])
        self.assertEqual(resolver_biseccion("x**3-2*x-5", 2, 3, 1e-6, 100)["aviso_discontinuidad"], "")

    def test_negativos_se_escriben_entre_parentesis(self):
        self.assertEqual(descomponer_decimal(-13)["descomposicion"], "-(1 × 10^1 + 3 × 10^0)")
        self.assertEqual(binario_a_decimal("-1101")["descomposicion"], "-(1 × 2^3 + 1 × 2^2 + 0 × 2^1 + 1 × 2^0)")

    def test_numeros_enormes_se_rechazan_sin_trabar(self):
        with self.assertRaisesRegex(ValueError, "como máximo"):
            binario_a_decimal("1" * 20000)
        with self.assertRaisesRegex(ValueError, "como máximo"):
            decimal_a_binario(10 ** 40)
        self.assertEqual(binario_a_decimal("1" * 100)["decimal"], 2 ** 100 - 1)

    def test_tabla_de_biseccion_limita_filas(self):
        corta = resolver_biseccion("x**3 - 2*x - 5", 2, 3, 0.0001, 100)["tabla"]
        self.assertEqual(_filas_a_mostrar(corta), corta)
        larga = list(range(300))
        filas = _filas_a_mostrar(larga)
        self.assertEqual(len(filas), 51)
        self.assertIsNone(filas[25])
        self.assertIs(filas[-1], larga[-1])


if __name__ == "__main__":
    unittest.main()
