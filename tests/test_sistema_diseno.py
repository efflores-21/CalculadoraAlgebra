"""Pruebas de contrato para los tokens y componentes base de la interfaz."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk

from modulos import _comun


class SistemaDiseno(unittest.TestCase):
    def test_paleta_y_aliases_legacy_estan_definidos(self):
        self.assertEqual(_comun.COLOR["fondo"], "#10151D")
        self.assertEqual(_comun.COLOR["tarjeta"], "#18212C")
        self.assertEqual(_comun.COLOR["acento"], "#43B3D5")
        self.assertEqual(_comun.COLOR["ok"], _comun.COLOR["verde"])
        self.assertEqual(_comun.COLOR["mal"], _comun.COLOR["error"])
        self.assertEqual(_comun.COLOR["primario"], _comun.COLOR["acento"])

    def test_espaciado_y_jerarquia_tipografica_son_consistentes(self):
        self.assertEqual(list(_comun.ESPACIADO.values()), [4, 8, 12, 16, 24, 32])
        self.assertLess(_comun.TAMANO_TEXTO["ayuda"], _comun.TAMANO_TEXTO["cuerpo"])
        self.assertLess(_comun.TAMANO_TEXTO["cuerpo"], _comun.TAMANO_TEXTO["subtitulo"])
        self.assertLess(_comun.TAMANO_TEXTO["subtitulo"], _comun.TAMANO_TEXTO["titulo"])

    def test_componentes_y_variantes_publicas_estan_disponibles(self):
        for componente in (
            _comun.Panel, _comun.TarjetaResultado, _comun.encabezado_seccion,
            _comun.etiqueta_estado, _comun.entrada_texto,
            _comun.boton_neutral, _comun.boton_advertencia, _comun.boton_destructivo,
        ):
            self.assertTrue(callable(componente))
        self.assertTrue(issubclass(_comun.Panel, ctk.CTkFrame))
        self.assertTrue(issubclass(_comun.TarjetaResultado, ctk.CTkFrame))

    @patch("modulos._comun.ctk.CTkButton")
    def test_variantes_de_boton_aplican_tokens_y_aceptan_altura_personalizada(self, boton):
        with patch("modulos._comun.fuente", return_value=object()):
            _comun.boton_primario(object(), "Calcular", lambda: None, width=120)
            opciones = boton.call_args.kwargs
            self.assertEqual(opciones["fg_color"], _comun.COLOR["primario"])
            self.assertEqual(opciones["hover_color"], _comun.COLOR["primario_hover"])
            self.assertEqual(opciones["text_color_disabled"], _comun.COLOR["primario_deshabilitado"])

            _comun.boton_destructivo(object(), "Eliminar", lambda: None, height=44)
            self.assertEqual(boton.call_args.kwargs["height"], 44)
            self.assertEqual(boton.call_args.kwargs["fg_color"], _comun.COLOR["error"])

            _comun.boton_texto(object(), "Volver", lambda: None)
            self.assertEqual(boton.call_args.kwargs["height"], 32)

    @patch("modulos._comun.ctk.CTkEntry")
    def test_entrada_texto_aplica_tema_y_alineacion_solicitada(self, entrada):
        with patch("modulos._comun.fuente", return_value=object()):
            _comun.entrada_texto(object(), ancho=240, placeholder="Buscar", justify="center")
        opciones = entrada.call_args.kwargs
        self.assertEqual(opciones["width"], 240)
        self.assertEqual(opciones["placeholder_text"], "Buscar")
        self.assertEqual(opciones["justify"], "center")
        self.assertEqual(opciones["fg_color"], _comun.COLOR["suave"])

    @patch("modulos._comun.ctk.CTkLabel")
    def test_etiqueta_estado_comunica_tipo_con_simbolo_y_texto(self, etiqueta):
        with patch("modulos._comun.fuente", return_value=object()):
            _comun.etiqueta_estado(object(), "Convergió", "converged")
        opciones = etiqueta.call_args.kwargs
        self.assertIn("Convergió", opciones["text"])
        self.assertTrue(opciones["text"].startswith("✓"))
        self.assertEqual(opciones["text_color"], _comun.COLOR["ok"])

    def test_tema_customtkinter_usa_los_tokens_principales(self):
        ruta = Path(__file__).resolve().parents[1] / "modulos" / "tema_minimalista.json"
        tema = json.loads(ruta.read_text(encoding="utf-8"))
        self.assertEqual(tema["CTk"]["fg_color"], [_comun.COLOR["fondo"]] * 2)
        self.assertEqual(tema["CTkFrame"]["fg_color"], [_comun.COLOR["tarjeta"]] * 2)
        self.assertEqual(tema["CTkButton"]["fg_color"], [_comun.COLOR["primario"]] * 2)
        self.assertEqual(tema["CTkButton"]["hover_color"], [_comun.COLOR["primario_hover"]] * 2)
        self.assertEqual(tema["CTkEntry"]["text_color"], [_comun.COLOR["texto"]] * 2)


if __name__ == "__main__":
    unittest.main()
