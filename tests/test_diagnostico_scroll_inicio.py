"""Pruebas sintéticas del diagnóstico del scrollbar de Inicio.

No crean una ventana Tk y no verifican la entrega real de eventos gráficos.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modulos import _diagnostico_ui as diagnostico


class CanvasFalso:
    def __init__(self, identificador="canvas"):
        self.identificador = identificador
        self.bindings = {}
        self.ancho, self.alto = 600, 400
        self.region = "0 0 600 1200"
        self.y = (0.0, 0.33)
        self.elementos = (7,)
        self.tags = ("scrollbar_parts",)
        self.configuracion = {}
        self.itemconfiguraciones = []

    def bind(self, secuencia, callback, add=None):
        self.bindings.setdefault(secuencia, []).append((callback, add))

    def find_withtag(self, tag):
        return self.elementos

    def gettags(self, item):
        return self.tags

    def bbox(self, tag):
        return (0, 0, 600, 1200)

    def cget(self, nombre):
        return self.region

    def configure(self, **opciones):
        self.configuracion.update(opciones)
        if "scrollregion" in opciones:
            self.region = opciones["scrollregion"]
        return "canvas-configure-result"

    def itemconfigure(self, item, *args, **opciones):
        self.itemconfiguraciones.append((item, args, dict(opciones)))
        return "itemconfigure-result"

    def itemcget(self, item, opcion):
        return self.configuracion.get(f"item-{item}-{opcion}", "600")

    def coords(self, item):
        return (0, 0)

    def yview(self):
        return self.y

    def winfo_width(self):
        return self.ancho

    def winfo_height(self):
        return self.alto

    def winfo_reqwidth(self):
        return self.ancho

    def winfo_reqheight(self):
        return self.alto

    def update_idletasks(self):
        return "update-result"


class ScrollbarFalso:
    def __init__(self, canvas, master=None):
        self._canvas = canvas
        self.master = master
        self.rango = (0.0, 0.33)
        self.oculto = False

    def get(self):
        return self.rango

    def grid_info(self):
        return {"row": 1, "column": 1, "sticky": "nsew", "padx": (0, 1), "pady": 4}

    def winfo_reqwidth(self):
        return 16

    def grid_remove(self):
        self.oculto = True

    def _draw(self, resultado="drawn"):
        self._canvas.update_idletasks()
        return resultado


class ParentFalso:
    pass


class ScrollbarTtkFalso:
    def __init__(self, master, orient, command, **opciones):
        if "width" in opciones:
            raise RuntimeError("ttk.Scrollbar no acepta width como opción del widget")
        self.master = master
        self.orient = orient
        self.command = command
        self.bindings = {}
        self.grid_opciones = None

    def grid(self, **opciones):
        self.grid_opciones = opciones

    def bind(self, secuencia, callback, add=None):
        self.bindings.setdefault(secuencia, []).append((callback, add))

    def set(self, inicio, fin):
        self.rango = (inicio, fin)

    def identify(self, x, y):
        return "slider"


class InicioFalso:
    def __init__(self):
        self._parent_canvas = CanvasFalso("contenido")
        self._parent_frame = ParentFalso()
        self._scrollbar = ScrollbarFalso(CanvasFalso("scrollbar"), self._parent_frame)
        self.bindings = {}
        self.ancho, self.alto = 600, 400
        self._create_window_id = 99
        self.tareas = {}
        self.proxima_tarea = 1

    def bind(self, secuencia, callback, add=None):
        self.bindings.setdefault(secuencia, []).append((callback, add))

    def winfo_width(self):
        return self.ancho

    def winfo_height(self):
        return self.alto

    def winfo_reqwidth(self):
        return self.ancho

    def winfo_reqheight(self):
        return self.alto

    def configure(self, **opciones):
        self.configuracion = dict(opciones)
        return "frame-configure-result"

    def after(self, milisegundos, callback):
        identificador = self.proxima_tarea
        self.proxima_tarea += 1
        self.tareas[identificador] = callback
        return identificador

    def after_cancel(self, identificador):
        self.tareas.pop(identificador, None)


class DiagnosticoScrollInicio(unittest.TestCase):
    def setUp(self):
        self.inicio = InicioFalso()
        self.registros = []
        self.activo = patch.object(diagnostico, "ACTIVO", True)
        self.activo.start()
        self.registrar = patch.object(
            diagnostico, "registrar",
            side_effect=lambda tipo, **datos: self.registros.append((tipo, datos)),
        )
        self.registrar.start()
        self.addCleanup(self.activo.stop)
        self.addCleanup(self.registrar.stop)

    @staticmethod
    def evento(widget, x=3, y=24):
        return SimpleNamespace(widget=widget, x=x, y=y)

    def enviar(self, secuencia, evento):
        callback = self.inicio._scrollbar._canvas.bindings[secuencia][-1][0]
        return callback(evento)

    def test_instrumenta_canvas_real_por_bindings_aditivos_y_sin_repetir(self):
        medidor = diagnostico.instrumentar_inicio(self.inicio)
        nuevamente = diagnostico.instrumentar_inicio(self.inicio)

        self.assertIs(medidor, nuevamente)
        self.assertIs(medidor.canvas, self.inicio._parent_canvas)
        self.assertIs(medidor.canvas_barra, self.inicio._scrollbar._canvas)
        for secuencia in ("<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>"):
            self.assertEqual(self.inicio._scrollbar._canvas.bindings[secuencia][-1][1], "+")

    def test_press_movimiento_configure_y_release_emiten_resumen_completo(self):
        diagnostico.instrumentar_inicio(self.inicio)
        barra = self.inicio._scrollbar._canvas
        self.enviar("<ButtonPress-1>", self.evento(barra))
        self.inicio._parent_canvas.y = (0.2, 0.53)
        self.inicio._parent_canvas.alto = 390
        self.enviar("<B1-Motion>", self.evento(barra, y=40))
        medidor = self.inicio._diagnostico_scroll_inicio
        medidor.configure_evento(self.evento(self.inicio._parent_canvas), "canvas_contenido")
        self.enviar("<ButtonRelease-1>", self.evento(barra, y=40))

        tipos = [tipo for tipo, _ in self.registros]
        self.assertIn("dashboard_scroll_instrumentacion", tipos)
        self.assertIn("dashboard_scroll_press", tipos)
        self.assertIn("dashboard_scroll_release", tipos)
        self.assertIn("dashboard_scroll_arrastre", tipos)
        press = next(datos for tipo, datos in self.registros if tipo == "dashboard_scroll_press")
        resumen = next(datos for tipo, datos in self.registros if tipo == "dashboard_scroll_arrastre")
        self.assertEqual(press["pantalla"], "Inicio / Dashboard / CTkScrollableFrame")
        self.assertEqual(press["elemento"], "thumb")
        self.assertEqual(press["tags"], ["scrollbar_parts"])
        self.assertEqual(resumen["estado"], "completa")
        self.assertEqual(resumen["movimientos_recibidos"], 1)
        self.assertEqual(resumen["configures"]["canvas_contenido"], 1)
        self.assertTrue(resumen["cambios_geometricos"])
        self.assertEqual(resumen["yview_fin"], (0.2, 0.53))

    def test_mide_configure_scrollregion_ventana_y_callbacks_sin_alterar_retorno(self):
        diagnostico.instrumentar_inicio(self.inicio)
        barra_canvas = self.inicio._scrollbar._canvas
        self.enviar("<ButtonPress-1>", self.evento(barra_canvas))
        canvas = self.inicio._parent_canvas

        self.assertEqual(canvas.configure(scrollregion="0 0 600 1200"), "canvas-configure-result")
        self.assertEqual(canvas.itemconfigure(99, width=600), "itemconfigure-result")
        self.assertEqual(self.inicio.configure(height=400), "frame-configure-result")
        self.assertEqual(self.inicio._scrollbar._draw("original-result"), "original-result")
        self.inicio._diagnostico_scroll_inicio.configure_evento(
            self.evento(canvas), "canvas_contenido"
        )
        self.enviar("<ButtonRelease-1>", self.evento(barra_canvas))

        resumen = next(datos for tipo, datos in self.registros if tipo == "dashboard_scroll_arrastre")
        self.assertEqual(resumen["geometria_inicio"]["canvas_solicitadas"], [600, 400])
        self.assertEqual(resumen["geometria_inicio"]["frame_solicitadas"], [600, 400])
        self.assertEqual(resumen["callbacks_durante_arrastre"]["scrollregion_llamadas"], 1)
        self.assertEqual(resumen["callbacks_durante_arrastre"]["ventana_itemconfigure_total"], 1)
        self.assertEqual(resumen["callbacks_durante_arrastre"]["frame_configure_total"], 1)
        self.assertEqual(resumen["callbacks_durante_arrastre"]["scrollbar_draw_total"], 1)
        self.assertEqual(resumen["callbacks_durante_arrastre"]["update_idletasks_total"], 1)
        self.assertEqual(resumen["configures_durante_arrastre"]["canvas_contenido"], 1)

    def test_pista_y_press_indeterminado_se_registran_sin_descartarse(self):
        diagnostico.instrumentar_inicio(self.inicio)
        barra = self.inicio._scrollbar._canvas
        barra.tags = ("border_parts",)
        self.enviar("<ButtonPress-1>", self.evento(barra))
        self.enviar("<ButtonRelease-1>", self.evento(barra))
        press_pista = next(datos for tipo, datos in self.registros if tipo == "dashboard_scroll_press")
        self.assertEqual(press_pista["elemento"], "pista")
        self.assertFalse(next(
            datos for tipo, datos in self.registros if tipo == "dashboard_scroll_arrastre"
        )["press_reconocido"])

        barra.elementos = ()
        self.enviar("<ButtonPress-1>", self.evento(barra))
        self.enviar("<ButtonRelease-1>", self.evento(barra))
        presses = [datos for tipo, datos in self.registros if tipo == "dashboard_scroll_press"]
        self.assertEqual(presses[-1]["elemento"], "indeterminado")

    def test_instrumentacion_desactivada_no_instala_bindings(self):
        diagnostico.ACTIVO = False
        self.assertIsNone(diagnostico.instrumentar_inicio(self.inicio))
        self.assertEqual(self.inicio._scrollbar._canvas.bindings, {})

    def test_variante_ttk_reutiliza_canvas_contenido_y_celda_de_barra(self):
        from tkinter import ttk

        with patch.dict("os.environ", {"CALCULADORA_INICIO_SCROLLBAR": "ttk"}), \
                patch.object(ttk, "Scrollbar", ScrollbarTtkFalso):
            variante = diagnostico.configurar_variante_scroll_inicio(self.inicio)

        barra = self.inicio._diagnostico_scrollbar_activo
        self.assertEqual(variante, "ttk")
        self.assertTrue(self.inicio._scrollbar.oculto)
        self.assertEqual(barra.command.__self__, self.inicio._parent_canvas)
        yscrollcommand = self.inicio._parent_canvas.configuracion["yscrollcommand"]
        self.assertEqual(yscrollcommand.__self__, barra)
        self.assertEqual(yscrollcommand.__func__, barra.set.__func__)
        self.assertEqual(barra.grid_opciones["row"], 1)
        self.assertEqual(barra.grid_opciones["column"], 1)
        self.assertIs(self.inicio._parent_canvas, diagnostico.instrumentar_inicio(self.inicio).canvas)

        medidor = self.inicio._diagnostico_scroll_inicio
        self.assertIs(medidor.canvas_barra, barra)
        medidor.press_evento(self.evento(barra))
        self.assertEqual(medidor.press["elemento"], "thumb")
        medidor.release_evento(self.evento(barra))

    def test_variante_ctk_conserva_el_scrollbar_original(self):
        with patch.dict("os.environ", {"CALCULADORA_INICIO_SCROLLBAR": "ctk"}):
            variante = diagnostico.configurar_variante_scroll_inicio(self.inicio)

        self.assertEqual(variante, "ctk")
        self.assertIs(self.inicio._diagnostico_scrollbar_activo, self.inicio._scrollbar)
        self.assertFalse(self.inicio._scrollbar.oculto)
        self.assertEqual(self.inicio._parent_canvas.configuracion, {})


if __name__ == "__main__":
    unittest.main()
