"""Pruebas del contrato de interacción del graficador de la interfaz."""

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modulos.modulo_metodos_numericos import ModuloMetodosNumericos


class Campo:
    def __init__(self, valor):
        self.valor = valor

    def get(self):
        return self.valor


class Estado:
    def __init__(self):
        self.texto = None
        self.color = None

    def configure(self, text, text_color):
        self.texto, self.color = text, text_color


class PresentacionGraficador(unittest.TestCase):
    def test_controles_estan_en_panel_y_canvas_se_expande_con_la_ventana(self):
        fuente = inspect.getsource(ModuloMetodosNumericos._crear_graficador)
        for control in ("Función f(x)", "x mínimo", "x máximo", "y mínimo", "y máximo"):
            self.assertIn(control, fuente)
        self.assertIn("self.canvas.grid(row=1, column=0, sticky=\"nsew\"", fuente)
        self.assertIn("<Configure>", fuente)
        self.assertIn("Graficar", fuente)

    def test_graficar_conserva_expresion_limites_y_dibuja_la_muestra(self):
        muestra = {"segmentos": [[(0, 0), (1, 1)]]}
        estado = Estado()
        llamadas = []
        modulo = SimpleNamespace(
            g_expr=Campo("sin(x) + x**2"), g_xmin=Campo("-2"), g_xmax=Campo("3"),
            g_ymin=Campo("-4"), g_ymax=Campo("5"), g_estado=estado,
            _repintar_ultima_grafica=lambda: llamadas.append("redibujar"),
            _mostrar_error=lambda error: self.fail(str(error)),
        )
        with patch("modulos.modulo_metodos_numericos.muestrear_funcion", return_value=muestra) as muestrear:
            ModuloMetodosNumericos.dibujar_grafica(modulo)
        muestrear.assert_called_once_with("sin(x) + x**2", "-2", "3", limites_y=(-4.0, 5.0))
        self.assertIs(modulo.ultima_muestra, muestra)
        self.assertEqual(llamadas, ["redibujar"])
        self.assertIn("1 segmento", estado.texto)

    def test_limites_y_incompletos_conservan_manejo_de_error_existente(self):
        errores, estado = [], Estado()
        modulo = SimpleNamespace(
            g_expr=Campo("x"), g_xmin=Campo("-1"), g_xmax=Campo("1"),
            g_ymin=Campo("0"), g_ymax=Campo(""), g_estado=estado,
            _mostrar_error=errores.append,
        )
        with patch("modulos.modulo_metodos_numericos.muestrear_funcion") as muestrear:
            ModuloMetodosNumericos.dibujar_grafica(modulo)
        muestrear.assert_not_called()
        self.assertEqual(len(errores), 1)
        self.assertIn("ambos límites", str(errores[0]))
        self.assertIn("No se pudo graficar", estado.texto)


if __name__ == "__main__":
    unittest.main()
