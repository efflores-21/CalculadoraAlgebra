"""Pruebas pedagógicas de las presentaciones de determinantes."""

import unittest
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch

from backend.matrices import determinante_cofactores_con_pasos, determinante_triangular
from modulos._comun import formatear_matriz
from modulos.modulo_determinantes import (
    LIMITE_COFACTORES,
    ModuloDeterminantes,
    _texto_pasos_cofactores,
    _texto_sarrus,
    _texto_traza_triangular,
)
from modulos.modulo_matrices import ModuloMatrices


class Celda:
    def __init__(self, valor):
        self.valor = str(valor)

    def get(self):
        return self.valor


class ExplicacionesDeterminantes(unittest.TestCase):
    def presentar_modulo_determinantes(self, matriz):
        modulo = SimpleNamespace(
            entradas=[[Celda(valor) for valor in fila] for fila in matriz],
            resultado=object(),
            ultima_matriz_resultado=None,
        )
        with patch("modulos.modulo_determinantes.reemplazar_texto") as reemplazar:
            ModuloDeterminantes.calcular(modulo)
        return reemplazar.call_args.args[1]

    def test_traza_triangular_vincula_intercambio_estados_y_sustituciones_exactas(self):
        A = [
            [Fraction(0), Fraction(1, 2), Fraction(1)],
            [Fraction(1), Fraction(0), Fraction(3)],
            [Fraction(4), Fraction(5), Fraction(6)],
        ]
        determinante, pasos = determinante_triangular(A)
        texto = "\n".join(_texto_traza_triangular(pasos))

        self.assertEqual(determinante, Fraction(8))
        self.assertIn("F1 y F2 intercambian todas sus entradas", texto)
        self.assertIn("signo acumulado = -1", texto)
        self.assertIn("Entrada (3,1): 4 - (4)(1) = 0", texto)
        self.assertIn("Entrada (3,3): 6 - (4)(3) = -6", texto)
        self.assertIn("Entrada (3,2): 5 - (10)(1/2) = 0", texto)
        self.assertIn("Entrada (3,3): -6 - (10)(1) = -16", texto)
        self.assertIn("producto de la diagonal: -8", texto)
        self.assertIn("signo acumulado (-1)", texto)

        cursor = 0
        for descripcion, estado in pasos:
            if " <- " in descripcion:
                posicion_operacion = texto.index(f"Operación: {descripcion}", cursor)
                posicion_antes = texto.index("Antes de la operación:", posicion_operacion)
                anterior = pasos[pasos.index((descripcion, estado)) - 1][1]
                posicion_estado_antes = texto.index(formatear_matriz(anterior), posicion_antes)
                posicion_despues = texto.index("Después de la operación:", posicion_estado_antes)
                posicion_estado_despues = texto.index(formatear_matriz(estado), posicion_despues)
                self.assertLess(posicion_operacion, posicion_estado_antes)
                self.assertLess(posicion_estado_antes, posicion_despues)
                self.assertLess(posicion_despues, posicion_estado_despues)
                cursor = posicion_estado_despues + len(formatear_matriz(estado))

        posicion_intercambio = texto.index("Operación: Intercambiar F1 y F2")
        posicion_antes_intercambio = texto.index(
            "Antes del intercambio:", posicion_intercambio
        )
        self.assertLess(
            posicion_antes_intercambio,
            texto.index(formatear_matriz(A), posicion_antes_intercambio),
        )
        estado_intercambiado = formatear_matriz(pasos[1][1])
        posicion_posterior_intercambio = texto.index("Después del intercambio:", posicion_intercambio)
        self.assertLess(
            posicion_posterior_intercambio,
            texto.index(estado_intercambiado, posicion_posterior_intercambio),
        )

    def test_matriz_triangular_y_caso_singular_se_interpretan(self):
        triangular = [[2, 1], [0, 3]]
        det_triangular, pasos_triangular = determinante_triangular(triangular)
        texto_triangular = "\n".join(_texto_traza_triangular(pasos_triangular))
        self.assertEqual(det_triangular, Fraction(6))
        self.assertIn("producto de la diagonal: 6", texto_triangular)
        self.assertIn("signo acumulado (+1)", texto_triangular)

        singular = [[1, 2], [2, 4]]
        det_singular, pasos_singulares = determinante_triangular(singular)
        texto_singular = "\n".join(_texto_traza_triangular(pasos_singulares))
        self.assertEqual(det_singular, Fraction(0))
        self.assertIn("No hay pivote en columna 2", texto_singular)
        self.assertIn("por ello det(A) = 0", texto_singular)

    def test_cofactores_conservan_menores_signos_terminos_y_orden(self):
        A = [
            [Fraction(0), Fraction(1, 2), Fraction(1)],
            [Fraction(1), Fraction(0), Fraction(3)],
            [Fraction(4), Fraction(5), Fraction(6)],
        ]
        determinante, pasos = determinante_cofactores_con_pasos(A)
        texto = "\n".join(_texto_pasos_cofactores(pasos))

        self.assertEqual(determinante, Fraction(8))
        self.assertIn("Menor M_1,2: eliminar la fila 1 y la columna 2 de A.", texto)
        self.assertIn("C_1,2 = (-1)^(1+2) · det(M_1,2(A)) = 6.", texto)
        self.assertIn("Término a_1,2·C_1,2 = 1/2·6 = 3.", texto)
        self.assertIn("det(A) = 0 + 3 + 5 = 8.", texto)

        cursor = 0
        for descripcion, estado in pasos:
            posicion = texto.index(descripcion, cursor)
            if estado is not None:
                posicion_estado = texto.index(formatear_matriz(estado), posicion)
                cursor = posicion_estado + len(formatear_matriz(estado))
            else:
                cursor = posicion + len(descripcion)

    def test_sarrus_desarrolla_seis_productos_y_coincide_en_ambas_pantallas(self):
        A = [
            [Fraction(0), Fraction(1, 2), Fraction(1)],
            [Fraction(1), Fraction(0), Fraction(3)],
            [Fraction(4), Fraction(5), Fraction(6)],
        ]
        lineas, resultado = _texto_sarrus(A)
        texto = "\n".join(lineas)

        self.assertEqual(resultado, Fraction(8))
        self.assertIn("a₁₁a₂₂a₃₃ = (0)(0)(6) = 0", texto)
        self.assertIn("a₁₂a₂₃a₃₁ = (1/2)(3)(4) = 6", texto)
        self.assertIn("a₁₃a₂₁a₃₂ = (1)(1)(5) = 5", texto)
        self.assertIn("Suma descendente = 0 + 6 + 5 = 11", texto)
        self.assertIn("a₁₃a₂₂a₃₁ = (1)(0)(4) = 0", texto)
        self.assertIn("a₁₂a₂₁a₃₃ = (1/2)(1)(6) = 3", texto)
        self.assertIn("a₁₁a₂₃a₃₂ = (0)(3)(5) = 0", texto)
        self.assertIn("Suma ascendente = 0 + 3 + 0 = 3", texto)
        self.assertIn("det(A) por Sarrus = 11 - 3 = 8", texto)
        cursor = 0
        for termino in (
            "a₁₁a₂₂a₃₃ =",
            "a₁₂a₂₃a₃₁ =",
            "a₁₃a₂₁a₃₂ =",
            "a₁₃a₂₂a₃₁ =",
            "a₁₂a₂₁a₃₃ =",
            "a₁₁a₂₃a₃₂ =",
        ):
            cursor = texto.index(termino, cursor) + len(termino)

        texto_modulo = self.presentar_modulo_determinantes(A)
        self.assertIn("Triangularización y cofactores: coinciden", texto_modulo)
        self.assertIn("Triangularización y Sarrus: coinciden", texto_modulo)

        modulo_matrices = SimpleNamespace(
            ultima_matriz_resultado=None,
            _otros_metodos_determinante=lambda matriz, det: (
                ModuloMatrices._otros_metodos_determinante(None, matriz, det)
            ),
        )
        lineas_matrices, resumen = ModuloMatrices._determinante(modulo_matrices, A)
        self.assertEqual(resumen, "det(A) = 8   ·   A es invertible")
        self.assertIn("det(A) por Sarrus = 11 - 3 = 8", "\n".join(lineas_matrices))

    def test_sarrus_rechaza_ordenes_distintos_de_tres(self):
        for matriz in ([[1, 2], [3, 4]], [[1, 2, 3, 4]] * 4):
            with self.subTest(orden=len(matriz)):
                with self.assertRaisesRegex(ValueError, "solo se aplica a matrices 3×3"):
                    _texto_sarrus(matriz)

    def test_cofactores_se_omiten_sobre_el_limite_sin_bloquear_triangularizacion(self):
        orden = LIMITE_COFACTORES + 1
        identidad = [
            [Fraction(int(i == j)) for j in range(orden)]
            for i in range(orden)
        ]
        modulo = SimpleNamespace(
            entradas=[[Celda(valor) for valor in fila] for fila in identidad],
            resultado=object(),
            ultima_matriz_resultado=None,
        )
        with patch(
            "modulos.modulo_determinantes.determinante_cofactores_con_pasos"
        ) as cofactores, patch(
            "modulos.modulo_determinantes.reemplazar_texto"
        ) as reemplazar:
            ModuloDeterminantes.calcular(modulo)

        cofactores.assert_not_called()
        texto = reemplazar.call_args.args[1]
        self.assertIn(f"límite de presentación es n = {LIMITE_COFACTORES}", texto)
        self.assertIn("Determinante por triangulación: 1", texto)


if __name__ == "__main__":
    unittest.main()
