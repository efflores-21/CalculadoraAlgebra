"""Pruebas de presentación de las conversiones de notación posicional."""

import inspect
import unittest
from types import SimpleNamespace

from modulos.modulo_metodos_numericos import ModuloMetodosNumericos


class PresentacionNotacionPosicional(unittest.TestCase):
    def _modulo_falso(self, decimal="-13", binario="-1101"):
        modulo = SimpleNamespace(
            n_decimal=SimpleNamespace(get=lambda: decimal),
            n_binario=SimpleNamespace(get=lambda: binario),
            resultados=[],
            errores=[],
        )
        modulo._presentar_resultado_notacion = lambda *args: modulo.resultados.append(args)
        modulo._mostrar_error = modulo.errores.append
        return modulo

    def test_decimal_a_binario_conserva_resultado_y_desarrollo(self):
        modulo = self._modulo_falso()

        ModuloMetodosNumericos.convertir_decimal(modulo)

        titulo, valor, equivalencia, detalles, procedimiento = modulo.resultados[0]
        self.assertEqual(titulo, "Conversión decimal → binario")
        self.assertEqual(valor, "-1101")
        self.assertEqual(equivalencia, "(-13)₁₀ = (-1101)₂")
        self.assertIn("-(1 × 10^1 + 3 × 10^0)", procedimiento)
        self.assertIn("Comprobación: la conversión inversa produce -13₁₀.", procedimiento)
        self.assertIn("Valor original: -13", detalles)
        self.assertFalse(modulo.errores)

    def test_binario_a_decimal_conserva_suma_y_comprobacion(self):
        modulo = self._modulo_falso()

        ModuloMetodosNumericos.convertir_binario(modulo)

        titulo, valor, equivalencia, detalles, procedimiento = modulo.resultados[0]
        self.assertEqual(titulo, "Conversión binario → decimal")
        self.assertEqual(valor, "-13")
        self.assertEqual(equivalencia, "(-1101)₂ = (-13)₁₀")
        self.assertIn("-(1 × 2^3 + 1 × 2^2 + 0 × 2^1 + 1 × 2^0)", procedimiento)
        self.assertIn("= -(8 + 4 + 0 + 1) = (-13)₁₀", procedimiento)
        self.assertIn("decimal a binario devuelve -1101", procedimiento)
        self.assertIn("Dígitos: 4", detalles)
        self.assertFalse(modulo.errores)

    def test_entrada_invalida_se_sigue_reportando_sin_resultado(self):
        modulo = self._modulo_falso(binario="102")

        ModuloMetodosNumericos.convertir_binario(modulo)

        self.assertFalse(modulo.resultados)
        self.assertEqual(len(modulo.errores), 1)
        self.assertIsInstance(modulo.errores[0], ValueError)

    def test_vistas_reutilizan_panel_tarjeta_y_texto_con_ajuste(self):
        crear = inspect.getsource(ModuloMetodosNumericos._crear_notacion)
        presentar = inspect.getsource(ModuloMetodosNumericos._presentar_resultado_notacion)

        for texto in ("Decimal → binario", "Binario → decimal", "Resultado"):
            self.assertIn(texto, crear)
        self.assertIn("Panel(", crear)
        self.assertIn("TarjetaResultado(", presentar)
        self.assertIn("wrap=\"word\"", presentar)
        self.assertIn("Desarrollo posicional", presentar)


if __name__ == "__main__":
    unittest.main()
