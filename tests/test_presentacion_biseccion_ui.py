"""Pruebas del procedimiento y contrato visual de Bisección."""

import inspect
import unittest

from backend.biseccion import resolver_biseccion
from modulos import modulo_metodos_numericos as pantalla


class PresentacionBiseccionUI(unittest.TestCase):
    def test_procedimiento_usa_valores_y_decisiones_de_la_traza(self):
        datos = resolver_biseccion("x**2 - 2", 1, 2, 1e-4, 10)
        texto = pantalla._texto_procedimiento_biseccion(datos, "x**2 - 2", (1, 2))
        paso = datos["tabla"][0]
        self.assertIn("Función: f(x) = x**2 - 2", texto)
        self.assertIn(f"f(a) = {pantalla._formatear_numero(paso['fa'])}", texto)
        self.assertIn(f"f(xr) = {pantalla._formatear_numero(paso['fr'])}", texto)
        self.assertIn(paso["decision"], texto)
        self.assertIn(datos["motivo"], texto)
        self.assertIn(f"f(x) = {pantalla._formatear_numero(datos['f_raiz'])}", texto)

    def test_raiz_exacta_en_extremo_indica_que_no_hubo_iteraciones(self):
        datos = resolver_biseccion("x - 1", 1, 2, 1e-5, 8)
        texto = pantalla._texto_procedimiento_biseccion(datos, "x - 1", (1, 2))
        self.assertEqual(datos["tabla"], [])
        self.assertIn("raíz exacta en un extremo", texto)

    def test_biseccion_tiene_vistas_y_seleccion_de_iteracion_locales(self):
        fuente_creacion = inspect.getsource(pantalla.ModuloMetodosNumericos._crear_biseccion)
        fuente_calculo = inspect.getsource(pantalla.ModuloMetodosNumericos.calcular_biseccion)
        fuente_grafica = inspect.getsource(pantalla.ModuloMetodosNumericos._dibujar_grafica_biseccion)
        for vista in ("Resumen", "Iteraciones", "Gráfica", "Procedimiento"):
            self.assertIn(vista, fuente_creacion)
        self.assertIn("_seleccionar_paso_biseccion", fuente_calculo)
        self.assertIn("intervalo_siguiente", fuente_grafica)


if __name__ == "__main__":
    unittest.main()
