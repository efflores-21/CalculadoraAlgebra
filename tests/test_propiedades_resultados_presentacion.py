"""Comprueba la separación visual de los resultados de propiedades matriciales."""

import inspect
import unittest
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import Mock, patch

from modulos.modulo_propiedades import (
    ModuloPropiedades,
    TEOREMAS_INVERSA_DETERMINANTE,
    TEOREMAS_PRODUCTO,
    TEOREMAS_TRANSPOSICION,
)


class Celda:
    def __init__(self, valor):
        self.valor = str(valor)

    def get(self):
        return self.valor

    def delete(self, inicio, fin):
        self.valor = ""

    def insert(self, indice, valor):
        self.valor = str(valor)


class PresentacionResultadosPropiedades(unittest.TestCase):
    @staticmethod
    def matriz(entradas):
        return [[Celda(valor) for valor in fila] for fila in entradas]

    def test_entradas_se_organizan_por_familia_sin_perder_acciones(self):
        fuente = inspect.getsource(ModuloPropiedades._construir_interfaz)

        self.assertIn('("Linealidad", "Transposición", "Producto", "Criterios")', fuente)
        self.assertIn('crear_controles(\n            tab_linealidad', fuente)
        self.assertIn('crear_controles(\n            tab_transposicion', fuente)
        self.assertIn('crear_controles(\n            tab_producto', fuente)
        self.assertIn('crear_controles(\n            tab_criterios', fuente)
        for callback in (
            "self.verificar",
            "self.verificar_transposicion",
            "self.verificar_inversa_determinante",
            "self.verificar_producto",
            "self.verificar_invertibilidad",
            "self.cargar_ejemplo_no_conmutativo",
            "self.cargar_ejemplo_cancelacion",
            "self.cargar_ejemplo_producto_nulo",
            "self.limpiar",
        ):
            with self.subTest(callback=callback):
                self.assertIn(callback, fuente)
        self.assertIn('("Resumen", "Datos", "Procedimiento")', inspect.getsource(
            ModuloPropiedades._crear_vistas_resultado
        ))

    def test_altura_de_pestanas_se_adapta_a_las_matrices_dinamicas(self):
        class Tabview:
            def configure(self, **opciones):
                self.opciones = opciones

        modulo = SimpleNamespace(
            pestanas_entrada=Tabview(),
            entradas_A=[[None] * 2 for _ in range(3)],
            entradas_A_transposicion=[[None] * 2 for _ in range(4)],
            entradas_B_transposicion=[[None] * 2 for _ in range(5)],
            entradas_producto={
                nombre: [[None] * 2 for _ in range(filas)]
                for nombre, filas in (("A", 6), ("B", 7), ("C", 8))
            },
            entradas_invertibilidad=[[None] * 2 for _ in range(9)],
        )

        ModuloPropiedades._ajustar_altura_pestanas_entrada(modulo)

        self.assertEqual(modulo.pestanas_entrada.opciones["height"], 460 + 44 * 21)

    def test_limpiar_reinicia_todas_las_pestanas_y_reconstruye_tablas(self):
        campo = lambda valor="9": Celda(valor)
        selector_transposicion = SimpleNamespace(set=Mock())
        selector_inversa = SimpleNamespace(set=Mock())
        selector_producto = SimpleNamespace(set=Mock())
        pestanas_entrada = SimpleNamespace(set=Mock())
        pestanas_resultado = SimpleNamespace(set=Mock())
        modulo = SimpleNamespace(
            _ocultar_vistas_resultado=Mock(),
            resultado=object(),
            entry_m=campo(),
            entry_n=campo(),
            entradas_A=self.matriz([[9, 8], [7, 6]]),
            entradas_u=[campo(), campo()],
            entradas_v=[campo(), campo()],
            entry_c=campo(),
            entradas_A_transposicion=self.matriz([[9, 8]]),
            entradas_B_transposicion=self.matriz([[7], [6]]),
            entries_dim_transposicion={
                clave: campo() for clave in ("at_m", "at_n", "bt_m", "bt_n", "at_c")
            },
            entradas_producto={
                nombre: self.matriz([[9, 8], [7, 6]])
                for nombre in ("A", "B", "C")
            },
            entries_dim_producto={
                clave: campo() for clave in ("pa_m", "pa_n", "pb_m", "pb_n", "pc_m", "pc_n")
            },
            entradas_invertibilidad=self.matriz([[9, 8], [7, 6]]),
            entry_orden_invertibilidad=campo(),
            teorema_transposicion_var=selector_transposicion,
            teorema_inversa_determinante_var=selector_inversa,
            teorema_producto_var=selector_producto,
            pestanas_entrada=pestanas_entrada,
            pestanas_resultado=pestanas_resultado,
            actualizar_entradas=Mock(),
            _actualizar_matrices_transposicion=Mock(),
            _actualizar_matrices_producto=Mock(),
            _actualizar_matriz_invertibilidad=Mock(),
        )

        with patch("modulos.modulo_propiedades.reemplazar_texto") as reemplazar:
            ModuloPropiedades.limpiar(modulo)

        grupos = (
            modulo.entradas_A,
            modulo.entradas_u,
            modulo.entradas_v,
            modulo.entradas_A_transposicion,
            modulo.entradas_B_transposicion,
            *modulo.entradas_producto.values(),
            modulo.entradas_invertibilidad,
        )
        for grupo in grupos:
            for fila in grupo:
                celdas = fila if isinstance(fila, list) else [fila]
                for celda in celdas:
                    self.assertEqual(celda.get(), "0")

        campos = (
            modulo.entry_m,
            modulo.entry_n,
            modulo.entry_c,
        )
        for entrada in (
            *campos,
            *modulo.entries_dim_transposicion.values(),
            *modulo.entries_dim_producto.values(),
            modulo.entry_orden_invertibilidad,
        ):
            self.assertEqual(entrada.get(), "2")
        selector_transposicion.set.assert_called_once_with(TEOREMAS_TRANSPOSICION[0])
        selector_inversa.set.assert_called_once_with(TEOREMAS_INVERSA_DETERMINANTE[0])
        selector_producto.set.assert_called_once_with(TEOREMAS_PRODUCTO[0])
        pestanas_entrada.set.assert_called_once_with("Linealidad")
        pestanas_resultado.set.assert_called_once_with("Resumen")
        for nombre in (
            "actualizar_entradas",
            "_actualizar_matrices_transposicion",
            "_actualizar_matrices_producto",
            "_actualizar_matriz_invertibilidad",
        ):
            getattr(modulo, nombre).assert_called_once_with()
        modulo._ocultar_vistas_resultado.assert_called_once_with()
        reemplazar.assert_called_once_with(modulo.resultado, "")

    def test_no_conmutatividad_se_presenta_como_contraejemplo_y_conserva_matrices(self):
        A = [[1, 1], [0, 1]]
        B = [[1, 0], [1, 1]]
        modulo = SimpleNamespace(
            teorema_producto_var=SimpleNamespace(get=lambda: TEOREMAS_PRODUCTO[4]),
            entradas_producto={
                "A": self.matriz(A), "B": self.matriz(B), "C": [],
            },
            _leer_matriz_transposicion=ModuloPropiedades._leer_matriz_transposicion,
            resultado=object(),
        )

        with patch("modulos.modulo_propiedades.reemplazar_texto"), patch.object(
            ModuloPropiedades, "_actualizar_vistas_resultado"
        ) as presentar:
            ModuloPropiedades.verificar_producto(modulo)

        llamada = presentar.call_args.args
        self.assertIn("AB y BA", llamada[1])
        self.assertEqual(llamada[3], ("Contraejemplo confirmado", "success"))
        matrices = dict(llamada[4])
        self.assertEqual(matrices["Matriz A"], [[Fraction(v) for v in fila] for fila in A])
        self.assertIn("AB", matrices)
        self.assertIn("BA", matrices)
        self.assertIn("AB", llamada[2])
        self.assertIn("Criterio del ejercicio: confirmado", llamada[6])

    def test_transposicion_entrega_entradas_resultados_y_traza_a_las_vistas(self):
        A = [[Fraction(1, 2), 1, 0], [0, -1, 2]]
        B = [[1, 0, 1], [2, 1, 0]]
        modulo = SimpleNamespace(
            teorema_transposicion_var=SimpleNamespace(get=lambda: TEOREMAS_TRANSPOSICION[1]),
            entradas_A_transposicion=self.matriz(A),
            entradas_B_transposicion=self.matriz(B),
            _leer_matriz_transposicion=ModuloPropiedades._leer_matriz_transposicion,
            resultado=object(),
        )

        with patch("modulos.modulo_propiedades.reemplazar_texto"), patch.object(
            ModuloPropiedades, "_actualizar_vistas_resultado"
        ) as presentar:
            ModuloPropiedades.verificar_transposicion(modulo)

        llamada = presentar.call_args.args
        nombres = [nombre for nombre, _ in llamada[4]]
        self.assertIn("Matriz A", nombres)
        self.assertIn("Matriz B", nombres)
        self.assertIn("A + B", nombres)
        self.assertIn("(A + B)ᵀ", nombres)
        self.assertIn("Comparación entrada por entrada", llamada[6])
        self.assertEqual(llamada[3], ("Igualdad verificada", "success"))

    def test_criterios_singulares_no_se_muestran_como_error_de_calculo(self):
        modulo = SimpleNamespace(
            entradas_invertibilidad=self.matriz([[1, 2], [2, 4]]),
            _leer_matriz_transposicion=ModuloPropiedades._leer_matriz_transposicion,
            resultado=object(),
        )

        with patch("modulos.modulo_propiedades.reemplazar_texto"), patch.object(
            ModuloPropiedades, "_actualizar_vistas_resultado"
        ) as presentar:
            ModuloPropiedades.verificar_invertibilidad(modulo)

        llamada = presentar.call_args.args
        self.assertEqual(llamada[3], ("Singular", "warning"))
        self.assertEqual(llamada[4][0][0], "Matriz A")
        self.assertIn("A es singular", llamada[6])

    def test_error_de_inversa_se_distingue_de_una_comprobacion_fallida(self):
        modulo = SimpleNamespace(
            teorema_inversa_determinante_var=SimpleNamespace(
                get=lambda: TEOREMAS_INVERSA_DETERMINANTE[0]
            ),
            entradas_A_transposicion=self.matriz([[1, 2], [2, 4]]),
            entradas_B_transposicion=[],
            _leer_matriz_transposicion=ModuloPropiedades._leer_matriz_transposicion,
            vistas_resultado=True,
            resultado=object(),
        )

        with patch("modulos.modulo_propiedades.reemplazar_texto"), patch(
            "modulos.modulo_propiedades.mensaje_error"
        ), patch.object(ModuloPropiedades, "_actualizar_vistas_resultado") as presentar:
            ModuloPropiedades.verificar_inversa_determinante(modulo)

        llamada = presentar.call_args.args
        self.assertEqual(llamada[3], ("Error de entrada o cálculo", "error"))
        self.assertIn("singular", llamada[2])

    def test_catalogos_de_propiedades_conservan_todos_sus_elementos(self):
        from modulos.modulo_propiedades import TEOREMAS_PRODUCTO, TEOREMAS_TRANSPOSICION

        self.assertEqual(len(TEOREMAS_PRODUCTO), 7)
        self.assertEqual(len(TEOREMAS_TRANSPOSICION), 4)
        self.assertEqual(len(TEOREMAS_INVERSA_DETERMINANTE), 6)


if __name__ == "__main__":
    unittest.main()
