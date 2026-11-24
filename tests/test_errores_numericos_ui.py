"""Pruebas de la organización visual del módulo de Errores Numéricos."""

import inspect
import unittest
from types import SimpleNamespace

from modulos.modulo_metodos_numericos import ModuloMetodosNumericos


class PresentacionErroresNumericos(unittest.TestCase):
    def _modulo_falso(self, verdadero="10", aproximado="9.8", x="0.5", delta="0.01"):
        modulo = SimpleNamespace(
            e_verdadero=SimpleNamespace(get=lambda: verdadero),
            e_aproximado=SimpleNamespace(get=lambda: aproximado),
            e_x=SimpleNamespace(get=lambda: x),
            e_dx=SimpleNamespace(get=lambda: delta),
            e_resultado=SimpleNamespace(contenido=SimpleNamespace(grid=lambda: None)),
            e_resultado_propagacion=SimpleNamespace(contenido=SimpleNamespace(grid=lambda: None)),
            errores=[], tarjetas=[], procedimientos=[],
        )
        modulo._mostrar_error = modulo.errores.append
        modulo._limpiar_panel_error = lambda _panel: None
        modulo._tarjeta_error = lambda _parent, titulo, valor, detalle=None: (
            modulo.tarjetas.append((titulo, valor, detalle)) or
            SimpleNamespace(grid=lambda **_opciones: None)
        )
        modulo._procedimiento_error = lambda _parent, titulo, texto, _fila, _columnas: (
            modulo.procedimientos.append((titulo, texto))
        )
        return modulo

    def test_error_absoluto_relativo_porcentual_y_caso_cero(self):
        modulo = self._modulo_falso()

        ModuloMetodosNumericos.calcular_errores(modulo)

        valores = dict((titulo, valor) for titulo, valor, _detalle in modulo.tarjetas)
        self.assertEqual(valores["Valor verdadero"], "10.0")
        self.assertEqual(valores["Valor aproximado"], "9.8")
        self.assertEqual(valores["Error absoluto"], "0.1999999999999993")
        self.assertEqual(valores["Error relativo"], "0.02")
        self.assertEqual(valores["Error porcentual"], "2%")
        self.assertIn("|10.0 − 9.8|", modulo.procedimientos[0][1])
        self.assertFalse(modulo.errores)

        cero = self._modulo_falso(verdadero="0", aproximado="2")
        ModuloMetodosNumericos.calcular_errores(cero)
        valores_cero = dict((titulo, valor) for titulo, valor, _detalle in cero.tarjetas)
        self.assertEqual(valores_cero["Error relativo"], "No definido porque el valor verdadero es cero.")
        self.assertEqual(valores_cero["Error porcentual"], "No definido.")

    def test_propagacion_presenta_resultados_y_procedimiento_existentes(self):
        modulo = self._modulo_falso()

        ModuloMetodosNumericos.calcular_propagacion(modulo)

        titulos = {titulo for titulo, _valor, _detalle in modulo.tarjetas}
        self.assertEqual(
            titulos,
            {"f(x)", "f(x + Δx)", "Cambio real · Δy", "Cambio aproximado · Δy",
             "Diferencia absoluta", "Derivada · f'(x)"},
        )
        titulo, procedimiento = modulo.procedimientos[0]
        self.assertEqual(titulo, "Desarrollo de la propagación")
        self.assertIn("f'(x) = cos(x) + 2x", procedimiento)
        self.assertIn("linealización de primer orden", procedimiento)
        self.assertFalse(modulo.errores)

    def test_entradas_invalidas_conservan_el_manejo_de_error(self):
        modulo = self._modulo_falso(verdadero="inválido")

        ModuloMetodosNumericos.calcular_errores(modulo)

        self.assertFalse(modulo.tarjetas)
        self.assertEqual(len(modulo.errores), 1)
        self.assertIsInstance(modulo.errores[0], ValueError)

    def test_interfaz_agrupa_operaciones_y_presenta_procedimientos_en_paneles(self):
        crear = inspect.getsource(ModuloMetodosNumericos._crear_errores)
        errores = inspect.getsource(ModuloMetodosNumericos.calcular_errores)
        propagacion = inspect.getsource(ModuloMetodosNumericos.calcular_propagacion)

        for texto in (
            "Representación en punto flotante", "Tipos de error",
            "Valor verdadero", "Valor aproximado", "Perturbación Δx",
            "Resultados de la comparación", "Resultados de propagación",
        ):
            self.assertIn(texto, crear)
        self.assertIn("_procedimiento_error", errores)
        self.assertIn("_procedimiento_error", propagacion)
        self.assertIn("wrap=\"word\"", inspect.getsource(ModuloMetodosNumericos._procedimiento_error))


if __name__ == "__main__":
    unittest.main()
