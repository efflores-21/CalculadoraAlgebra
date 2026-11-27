"""Pruebas de integración y explicación de la pestaña de Maclaurin."""

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.series_maclaurin import calcular_maclaurin
from modulos import modulo_metodos_numericos as pantalla


class PresentacionMaclaurin(unittest.TestCase):
    def test_resumen_presenta_polinomio_aproximacion_y_errores(self):
        datos = calcular_maclaurin("exp(x)", 1, 4)
        texto = pantalla.ModuloMetodosNumericos._resumen_maclaurin(datos)
        for esperado in ("Función: f(x)", "P_4(x)", "Aproximación", "Valor real", "Error absoluto", "Error relativo porcentual", "Conclusión"):
            self.assertIn(esperado, texto)

    def test_procedimiento_muestra_derivadas_factoriales_y_sustitucion(self):
        datos = calcular_maclaurin("exp(x)", 1, 3)
        texto = pantalla._texto_procedimiento_maclaurin(datos)
        for esperado in ("Fórmula general", "f⁽1⁾(x)", "f⁽1⁾(0)", "1!", "Coeficiente", "Polinomio", "Sustitución", "Error absoluto"):
            self.assertIn(esperado, texto)

    def test_tabla_detalla_todos_los_terminos_incluidos(self):
        datos = calcular_maclaurin("sin(x)", 1, 4)
        texto = pantalla._texto_terminos_maclaurin(datos)
        self.assertEqual(texto.count("n = "), 4)
        self.assertIn("Coeficiente: 0 / 2 = 0", texto)
        self.assertIn("Derivada en 0", texto)

    def test_errores_de_valor_real_cero_y_dominio_se_explican(self):
        cero = calcular_maclaurin("x - 1", 1, 1)
        resumen = pantalla.ModuloMetodosNumericos._resumen_maclaurin(cero)
        self.assertIn("no definido porque el valor real es cero", resumen)
        dominio = calcular_maclaurin("log(1+x)", -2, 3)
        self.assertIn("no se pudo evaluar", pantalla.ModuloMetodosNumericos._resumen_maclaurin(dominio))

    def test_pestana_se_integra_al_modulo_y_formulario_tiene_acciones(self):
        fuente = inspect.getsource(pantalla.ModuloMetodosNumericos._construir_interfaz)
        formulario = inspect.getsource(pantalla.ModuloMetodosNumericos._crear_maclaurin)
        self.assertIn("Series de Maclaurin", fuente)
        for texto in ("Función f(x)", "Valor de x", "Cantidad de términos N", "Calcular", "Ejemplo", "Limpiar"):
            self.assertIn(texto, formulario)

    def test_calcular_conecta_campos_con_backend_y_presentacion(self):
        modulo = SimpleNamespace(
            mac_expr=SimpleNamespace(get=lambda: "exp(x)"),
            mac_x=SimpleNamespace(get=lambda: "1"),
            mac_n=SimpleNamespace(get=lambda: "4"),
            mac_estado=SimpleNamespace(configure=Mock()),
            _vaciar_resultado_maclaurin=Mock(),
            _mostrar_resultado_maclaurin=Mock(),
        )
        with patch.object(pantalla.ModuloMetodosNumericos, "_mostrar_error"):
            pantalla.ModuloMetodosNumericos.calcular_maclaurin(modulo)
        modulo._mostrar_resultado_maclaurin.assert_called_once()
        resultado = modulo._mostrar_resultado_maclaurin.call_args.args[0]
        self.assertEqual(resultado["numero_terminos"], 4)
        self.assertAlmostEqual(resultado["aproximacion"], 8/3)


if __name__ == "__main__":
    unittest.main()
