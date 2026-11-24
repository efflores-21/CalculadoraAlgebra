"""Regresiones para conservar instancias al cambiar de módulo."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import main


class AreaFalsa:
    def __init__(self):
        self.widgets = []

    def winfo_children(self):
        return list(self.widgets)


class ModuloFalso:
    instancias = []

    def __init__(self, parent, volver):
        self.parent = parent
        self.volver = volver
        self.visible = False
        self.entradas = {"valor": ""}
        parent.widgets.append(self)
        self.instancias.append(self)

    def grid(self, **_opciones):
        self.visible = True

    def grid_remove(self):
        self.visible = False

    def destroy(self):
        self.parent.widgets.remove(self)


class PreservacionEstadoNavegacion(unittest.TestCase):
    def setUp(self):
        ModuloFalso.instancias = []
        self.area = AreaFalsa()
        self.unbinds_globales = []
        self.app = SimpleNamespace(
            paneles={},
            area_principal=self.area,
            modulo_activo=None,
            unbind_all=lambda secuencia: self.unbinds_globales.append(secuencia),
            _limpiar_area=lambda: main.MenuPrincipal._limpiar_area(self.app),
            _actualizar_navegacion=lambda: None,
            mostrar_menu=lambda: None,
        )

    def _navegar(self, nombre):
        main.MenuPrincipal.mostrar_modulo(self.app, nombre)

    def _volver_a_inicio(self):
        self.app.modulo_activo = None
        main.MenuPrincipal._limpiar_area(self.app)

    def test_conserva_entradas_al_volver_desde_inicio_y_otro_modulo(self):
        clases = {"sistemas": ModuloFalso, "matrices": ModuloFalso}
        with patch.dict(main.CLASES_MODULOS, clases, clear=True):
            self._navegar("sistemas")
            sistemas = self.app.paneles["sistemas"]
            sistemas.entradas["valor"] = "2, 3, 5"

            self._volver_a_inicio()
            self.assertFalse(sistemas.visible)
            self._navegar("matrices")
            matrices = self.app.paneles["matrices"]
            self._navegar("sistemas")

            self.assertIs(self.app.paneles["sistemas"], sistemas)
            self.assertEqual(sistemas.entradas["valor"], "2, 3, 5")
            self.assertEqual(sum(widget.visible for widget in self.area.widgets), 1)
            self.assertTrue(sistemas.visible)
            self.assertFalse(matrices.visible)
            self.assertEqual(self.unbinds_globales, [])

    def test_reutiliza_instancia_y_no_acumula_modulos_alternados(self):
        with patch.dict(main.CLASES_MODULOS, {"sistemas": ModuloFalso}, clear=True):
            self._navegar("sistemas")
            instancia = self.app.paneles["sistemas"]
            self._volver_a_inicio()
            self._navegar("sistemas")

            self.assertIs(self.app.paneles["sistemas"], instancia)
            self.assertEqual(len(self.app.paneles), 1)
            self.assertEqual(len(self.area.widgets), 1)
            self.assertEqual(len(ModuloFalso.instancias), 1)

    def test_la_limpieza_explicita_del_modulo_sigue_reflejada_al_reabrirlo(self):
        with patch.dict(main.CLASES_MODULOS, {"sistemas": ModuloFalso}, clear=True):
            self._navegar("sistemas")
            modulo = self.app.paneles["sistemas"]
            modulo.entradas["valor"] = ""
            self._volver_a_inicio()
            self._navegar("sistemas")

            self.assertEqual(self.app.paneles["sistemas"].entradas["valor"], "")


if __name__ == "__main__":
    unittest.main()
