"""Pruebas de organización de las vistas de operaciones con matrices."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from modulos.modulo_matrices import (
    ModuloMatrices,
    _NOMBRES_OPERACION,
    _OPERACIONES_BOTON,
    _ajustar_wrap_tarjeta_clasificador,
    _nombres_datos_operacion,
)


class VistasOperacionesMatrices(unittest.TestCase):
    def test_las_diez_operaciones_tienen_nombre_de_presentacion(self):
        esperadas = {
            "suma", "resta", "escalar", "producto", "transpuesta",
            "determinante", "inversa", "adjunta", "propiedades", "clasificar",
        }
        self.assertEqual(set(_NOMBRES_OPERACION), esperadas)
        self.assertTrue(all(_NOMBRES_OPERACION.values()))
        self.assertEqual({operacion for _, operacion in _OPERACIONES_BOTON}, esperadas)

    def test_datos_muestran_solo_las_matrices_que_participan(self):
        self.assertEqual(_nombres_datos_operacion("suma"), ("A", "B"))
        self.assertEqual(_nombres_datos_operacion("producto"), ("A", "B"))
        self.assertEqual(_nombres_datos_operacion("transpuesta"), ("A",))
        self.assertEqual(_nombres_datos_operacion("determinante"), ("A",))
        self.assertEqual(_nombres_datos_operacion("propiedades"), ("A", "B", "C"))
        self.assertEqual(_nombres_datos_operacion("clasificar"), ("A",))

    def test_clasificador_presenta_condiciones_pivotes_y_conclusion_rref(self):
        lineas, resumen = ModuloMatrices._clasificar(None, [[1, 0, 2], [0, 1, -3]])
        texto = "\n".join(lineas)
        self.assertIn("A está en forma escalonada reducida por filas (RREF)", resumen)
        self.assertIn("Dimensiones: 2 × 3", texto)
        self.assertIn("Resultado REF: Sí", texto)
        self.assertIn("Resultado RREF: Sí", texto)
        self.assertIn("(1, 1) = 1", texto)
        self.assertIn("VERIFICACIÓN REF", texto)
        self.assertIn("VERIFICACIÓN RREF", texto)
        self.assertIn("Conclusión:", texto)

    def test_interfaz_no_presenta_rref_como_positiva_si_falla_ref(self):
        lineas, resumen = ModuloMatrices._clasificar(None, [[0, 1], [1, 0]])
        texto = "\n".join(lineas)
        self.assertIn("no está en REF", resumen)
        self.assertIn("tampoco está en RREF", resumen)
        self.assertIn("✗ No cumple: La matriz no cumple REF", texto)

    def test_textos_de_tarjeta_se_ajustan_al_ancho_util_disponible(self):
        tarjeta = SimpleNamespace(valor=Mock(), detalle=Mock())
        evento = SimpleNamespace(width=600)
        with patch("modulos.modulo_matrices.ctk.ScalingTracker.get_widget_scaling", return_value=1.5):
            _ajustar_wrap_tarjeta_clasificador(evento, tarjeta)
        tarjeta.valor.configure.assert_called_once_with(wraplength=368)
        tarjeta.detalle.configure.assert_called_once_with(wraplength=368)

    def test_boton_diez_ocupa_tres_columnas_y_conserva_callback(self):
        class BotonFalso:
            def __init__(self, texto, comando):
                self.texto = texto
                self.comando = comando
                self.opciones_grid = None

            def grid(self, **opciones):
                self.opciones_grid = opciones

        principales = []

        def crear_primario(_acciones, texto, comando, **_opciones):
            boton = BotonFalso(texto, comando)
            principales.append(boton)
            return boton

        def crear_secundario(_acciones, texto, comando, **_opciones):
            return BotonFalso(texto, comando)

        modulo = SimpleNamespace(calcular=Mock(), _ver_teoremas=Mock(), limpiar=Mock())
        acciones = SimpleNamespace(grid_columnconfigure=Mock())
        with patch("modulos.modulo_matrices.boton_primario", side_effect=crear_primario), patch(
            "modulos.modulo_matrices.boton_secundario", side_effect=crear_secundario
        ):
            ModuloMatrices._crear_botones(modulo, acciones)

        self.assertEqual(len(principales), 10)
        for indice, boton in enumerate(principales[:9]):
            self.assertEqual(boton.opciones_grid["row"], indice // 3)
            self.assertEqual(boton.opciones_grid["column"], indice % 3)
        boton_clasificar = principales[9]
        self.assertEqual(boton_clasificar.texto, "10. Clasificar matriz (REF / RREF)")
        self.assertEqual(boton_clasificar.opciones_grid["row"], 3)
        self.assertEqual(boton_clasificar.opciones_grid["column"], 0)
        self.assertEqual(boton_clasificar.opciones_grid["columnspan"], 3)
        boton_clasificar.comando()
        modulo.calcular.assert_called_once_with("clasificar")


if __name__ == "__main__":
    unittest.main()
