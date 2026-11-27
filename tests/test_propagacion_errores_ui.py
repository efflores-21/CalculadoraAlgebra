"""Pruebas de integración y presentación para la propagación general."""

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.propagacion_errores import propagar_errores
from modulos import modulo_metodos_numericos as pantalla


class CampoFalso:
    def __init__(self, texto=""):
        self.texto = texto
        self.destruido = False
        self.opciones = None

    def get(self):
        return self.texto

    def insert(self, _indice, texto):
        self.texto = texto

    def grid(self, **opciones):
        self.opciones = opciones

    def destroy(self):
        self.destruido = True


class PresentacionPropagacionGeneral(unittest.TestCase):
    def resultado_referencia(self, metodo="maximo"):
        return propagar_errores(
            "x**2*y + 3*y", {"x": 2, "y": 3}, {"x": 0.1, "y": 0.2}, metodo
        )

    def test_resumen_distingue_metodo_resultado_e_intervalo(self):
        datos = self.resultado_referencia()
        texto = pantalla.ModuloMetodosNumericos._resumen_propagacion_general(datos)
        for esperado in ("Error máximo", "f = 21", "2.6", "[18.4, 23.6]", "no es un intervalo de confianza"):
            self.assertIn(esperado, texto)

    def test_resumen_estadistico_muestra_la_incertidumbre_correcta(self):
        datos = self.resultado_referencia("estadistico")
        texto = pantalla.ModuloMetodosNumericos._resumen_propagacion_general(datos)
        self.assertIn("Incertidumbre estadística", texto)
        self.assertIn("1.8439089", texto)

    def test_datos_y_procedimiento_muestran_sustituciones_y_derivadas(self):
        datos = self.resultado_referencia()
        vista_datos = pantalla.ModuloMetodosNumericos._datos_propagacion_general(datos)
        procedimiento = pantalla.ModuloMetodosNumericos._procedimiento_propagacion_general(datos)
        self.assertIn("x = 2 ± 0.1", vista_datos)
        self.assertIn("y = 3 ± 0.2", vista_datos)
        self.assertIn("(2)**2*(3)", procedimiento)
        self.assertIn("∂f/∂x = 2*x*y", procedimiento)
        self.assertIn("1.2 + 1.4 = 2.6", procedimiento)

    def test_contribuciones_presenta_filas_por_variable(self):
        texto = pantalla.ModuloMetodosNumericos._contribuciones_propagacion_general(self.resultado_referencia())
        self.assertIn("Variable | Valor | Incertidumbre", texto)
        self.assertIn("x = 2 ± 0.1", texto)
        self.assertIn("Contribución máx. = 1.2", texto)
        self.assertIn("Contribución estadística = 1.2", texto)

    def test_formulario_se_integra_en_seccion_existente_con_ambos_metodos(self):
        fuente = inspect.getsource(pantalla.ModuloMetodosNumericos._crear_errores)
        for texto in (
            "Propagación general de errores", "Función f(variables)",
            "Error máximo", "Incertidumbre estadística", "_actualizar_campos_propagacion",
            "Calcular propagación", "Ejemplo", "Limpiar", "Resultados de propagación",
        ):
            self.assertIn(texto, fuente)

    def test_actualizacion_dinamica_preserva_variables_comunes_y_elimina_ajenas(self):
        campos_previos = {
            "x": {"valor": CampoFalso("2.5"), "incertidumbre": CampoFalso("0.2")},
            "y": {"valor": CampoFalso("7"), "incertidumbre": CampoFalso("0.4")},
        }
        widgets_previos = [campo for fila in campos_previos.values() for campo in fila.values()]
        marco = SimpleNamespace(winfo_children=lambda: widgets_previos)
        modulo = SimpleNamespace(
            pe_funcion=SimpleNamespace(get=lambda: "x + z"),
            pe_estado_variables=SimpleNamespace(configure=Mock()),
            pe_marco_variables=marco,
            pe_campos_variables=campos_previos,
        )
        with patch.object(pantalla, "etiqueta", side_effect=lambda *_args, **_kwargs: CampoFalso()), patch.object(
            pantalla.ctk, "CTkEntry", side_effect=lambda *_args, **_kwargs: CampoFalso()
        ), patch.object(pantalla, "fuente_mono", return_value=object()):
            resultado = pantalla.ModuloMetodosNumericos._actualizar_campos_propagacion(modulo)
        self.assertTrue(resultado)
        self.assertEqual(set(modulo.pe_campos_variables), {"x", "z"})
        self.assertTrue(campos_previos["y"]["valor"].destruido)
        self.assertEqual(modulo.pe_campos_variables["x"]["valor"].get(), "2.5")
        self.assertEqual(modulo.pe_campos_variables["x"]["incertidumbre"].get(), "0.2")
        self.assertEqual(modulo.pe_campos_variables["z"]["valor"].get(), "0")

    def test_callback_de_ui_envia_valores_y_metodo_al_backend(self):
        panel = SimpleNamespace(contenido=SimpleNamespace(winfo_children=lambda: []))
        modulo = SimpleNamespace(
            pe_funcion=SimpleNamespace(get=lambda: "x**2"),
            pe_campos_variables={"x": {"valor": CampoFalso("2"), "incertidumbre": CampoFalso("0.1")}},
            pe_selector_metodo=SimpleNamespace(get=lambda: "Incertidumbre estadística"),
            pe_estado_variables=SimpleNamespace(configure=Mock()),
            e_resultado_propagacion=panel,
            _actualizar_campos_propagacion=lambda: True,
            _mostrar_resultado_propagacion_general=Mock(),
            _mostrar_error=Mock(),
        )
        pantalla.ModuloMetodosNumericos.calcular_propagacion_general(modulo)
        modulo._mostrar_resultado_propagacion_general.assert_called_once()
        datos = modulo._mostrar_resultado_propagacion_general.call_args.args[0]
        self.assertEqual(datos["metodo"], "estadistico")
        self.assertAlmostEqual(datos["error_maximo"], 0.4)

    def test_error_en_ui_no_cierra_la_aplicacion(self):
        panel = SimpleNamespace(contenido=SimpleNamespace(winfo_children=lambda: []))
        modulo = SimpleNamespace(
            pe_funcion=SimpleNamespace(get=lambda: "x"),
            pe_campos_variables={"x": {"valor": CampoFalso("1"), "incertidumbre": CampoFalso("-1")}},
            pe_selector_metodo=SimpleNamespace(get=lambda: "Error máximo"),
            pe_estado_variables=SimpleNamespace(configure=Mock()),
            e_resultado_propagacion=panel,
            _actualizar_campos_propagacion=lambda: True,
            _mostrar_error=Mock(),
        )
        pantalla.ModuloMetodosNumericos.calcular_propagacion_general(modulo)
        modulo._mostrar_error.assert_called_once()
        self.assertIsInstance(modulo._mostrar_error.call_args.args[0], ValueError)


if __name__ == "__main__":
    unittest.main()
