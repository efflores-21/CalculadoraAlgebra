"""Pruebas sin pantalla gráfica para el enrutamiento de la rueda."""

import unittest
from types import SimpleNamespace

from modulos._comun import _GestorRueda, _gestor_rueda


class RaizFalsa:
    def __init__(self):
        self.bindings = {}

    def bind_all(self, secuencia, callback, add=None):
        self.bindings.setdefault(secuencia, []).append((callback, add))

    def winfo_toplevel(self):
        return self


class WidgetFalso:
    def __init__(self, master=None, mapped=True):
        self.master = master
        self.mapped = mapped
        self.desp_horizontal = []
        self.desp_vertical = []
        self.ruedas = []
        self.ruedas_h = []

    def winfo_ismapped(self):
        return self.mapped

    def _rueda(self, evento):
        self.ruedas.append(evento)

    def _rueda_horizontal(self, evento):
        self.ruedas_h.append(evento)

    def _desplazar_v(self, pasos):
        self.desp_vertical.append(pasos)


class BindingsScroll(unittest.TestCase):
    def setUp(self):
        self.raiz = RaizFalsa()
        self.gestor = _GestorRueda(self.raiz)
        self.primero = WidgetFalso()
        self.segundo = WidgetFalso()
        self.gestor.registrar(self.primero)
        self.gestor.registrar(self.segundo)

    def test_instala_un_solo_despachador_por_evento_y_reutiliza_registros(self):
        self.gestor.registrar(self.primero)

        self.assertEqual(len(self.raiz.bindings), 4)
        self.assertTrue(all(len(llamadas) == 1 for llamadas in self.raiz.bindings.values()))
        self.assertTrue(all(llamadas[0][1] == "+" for llamadas in self.raiz.bindings.values()))

    def test_reutiliza_el_despachador_de_la_ventana(self):
        raiz = RaizFalsa()

        primero = _gestor_rueda(raiz)
        segundo = _gestor_rueda(raiz)

        self.assertIs(primero, segundo)
        self.assertEqual(sum(map(len, raiz.bindings.values())), 4)

    def test_rueda_se_dirige_al_contenedor_ancestro_del_widget_objetivo(self):
        hijo = WidgetFalso(master=self.primero)
        evento = SimpleNamespace(widget=hijo, delta=-120, num=5)

        retorno = self.raiz.bindings["<MouseWheel>"][0][0](evento)

        self.assertEqual(self.primero.ruedas, [evento])
        self.assertEqual(self.segundo.ruedas, [])
        self.assertEqual(retorno, "break")

    def test_shift_y_botones_linux_se_enrutan_sin_interferir_con_otro_contenedor(self):
        evento = SimpleNamespace(widget=self.segundo, delta=120, num=4)

        self.raiz.bindings["<Shift-MouseWheel>"][0][0](evento)
        self.raiz.bindings["<Button-4>"][0][0](evento)
        self.raiz.bindings["<Button-5>"][0][0](evento)

        self.assertEqual(self.segundo.ruedas_h, [evento])
        self.assertEqual(self.segundo.desp_vertical, [-1, 1])
        self.assertEqual(self.primero.desp_vertical, [])

    def test_no_enruta_a_contenedores_ocultos_o_destruidos(self):
        evento = SimpleNamespace(widget=self.primero, delta=-120, num=5)
        self.primero.mapped = False

        self.assertIsNone(self.raiz.bindings["<MouseWheel>"][0][0](evento))
        self.assertEqual(self.primero.ruedas, [])

        self.primero.mapped = True
        self.gestor.desregistrar(self.primero)
        self.assertIsNone(self.raiz.bindings["<MouseWheel>"][0][0](evento))
        self.assertEqual(self.primero.ruedas, [])


if __name__ == "__main__":
    unittest.main()
