"""Pruebas pedagógicas de la regla de Cramer."""

import unittest
from fractions import Fraction
from unittest.mock import patch
from types import SimpleNamespace

from backend.matrices import resolver_cramer
from backend.matriz import formatear_valor
from modulos._comun import formatear_matriz
from modulos.modulo_sistemas import ModuloSistemas


class ExplicacionesCramer(unittest.TestCase):
    def presentar(self, A, b):
        with patch("modulos.modulo_sistemas.reemplazar_texto") as reemplazar:
            ModuloSistemas._mostrar_cramer(SimpleNamespace(resultado=object()), A, b)
        return reemplazar.call_args.args[1]

    def assert_traza_determinante_en_orden(self, texto, nombre, pasos, cursor=0):
        """Vincula cada operación presentada con sus estados reales consecutivos."""
        descripcion_inicial, estado_anterior = pasos[0]
        cursor = texto.index(f"{nombre}: {descripcion_inicial}", cursor)
        representacion = formatear_matriz(estado_anterior)
        cursor = texto.index(representacion, cursor) + len(representacion)

        for descripcion, estado in pasos[1:]:
            if descripcion.startswith("Intercambiar F"):
                cursor = texto.index(descripcion, cursor) + len(descripcion)
                cursor = texto.index("Antes del intercambio:", cursor)
                representacion = formatear_matriz(estado_anterior)
                cursor = texto.index(representacion, cursor) + len(representacion)
                cursor = texto.index("Después del intercambio:", cursor)
                representacion = formatear_matriz(estado)
                cursor = texto.index(representacion, cursor) + len(representacion)
            elif descripcion.startswith("Pivote "):
                columna = int(descripcion.split()[1].rstrip(":")) - 1
                pivote = estado[columna][columna]
                detalle_pivote = (
                    f"Pivote de la columna {columna + 1}: "
                    f"{formatear_valor(pivote)}."
                )
                cursor = texto.index(detalle_pivote, cursor) + len(detalle_pivote)
                representacion = formatear_matriz(estado)
                cursor = texto.index(representacion, cursor) + len(representacion)
            elif " <- " in descripcion:
                cursor = texto.index(
                    f"Operación por filas: {descripcion}", cursor
                ) + len(f"Operación por filas: {descripcion}")
                cursor = texto.index("Antes de la operación:", cursor)
                representacion = formatear_matriz(estado_anterior)
                cursor = texto.index(representacion, cursor) + len(representacion)

                destino, lado_derecho = descripcion.split(" <- ", 1)
                fila_destino = int(destino.removeprefix("F")) - 1
                fila_pivote = int(lado_derecho.rsplit("F", 1)[1].rstrip(".")) - 1
                columna_pivote = fila_pivote
                pivote = estado_anterior[fila_pivote][columna_pivote]
                factor = estado_anterior[fila_destino][columna_pivote] / pivote
                for columna in range(columna_pivote, len(estado[fila_destino])):
                    antes = estado_anterior[fila_destino][columna]
                    base = estado_anterior[fila_pivote][columna]
                    despues = estado[fila_destino][columna]
                    if antes != despues:
                        self.assertEqual(
                            antes - factor * base,
                            despues,
                            f"El estado del backend no corresponde a {descripcion}.",
                        )
                        sustitucion = (
                            f"Entrada ({fila_destino + 1},{columna + 1}): "
                            f"{formatear_valor(antes)} - "
                            f"({formatear_valor(factor)})({formatear_valor(base)}) "
                            f"= {formatear_valor(despues)}"
                        )
                        cursor = texto.index(sustitucion, cursor) + len(sustitucion)

                cursor = texto.index("Después de la operación:", cursor)
                representacion = formatear_matriz(estado)
                cursor = texto.index(representacion, cursor) + len(representacion)
            else:
                cursor = texto.index(descripcion, cursor) + len(descripcion)
                representacion = formatear_matriz(estado)
                cursor = texto.index(representacion, cursor) + len(representacion)

            estado_anterior = estado

        return cursor

    def test_fracciones_explican_determinantes_formulas_y_verificacion_exactas(self):
        A = [[2, 1], [1, 2]]
        b = [1, 0]
        datos = resolver_cramer(A, b)
        texto = self.presentar(A, b)

        self.assertEqual(datos["determinante"], Fraction(3))
        self.assertEqual([r["determinante"] for r in datos["reemplazos"]],
                         [Fraction(2), Fraction(-1)])
        self.assertEqual(datos["solucion"], [Fraction(2, 3), Fraction(-1, 3)])
        self.assertIn("D = det(A) ≠ 0", texto)
        self.assertIn("A debe ser cuadrada de orden 2", texto)
        self.assertIn("b=x₁a₁+⋯+xₙaₙ", texto)
        self.assertIn("linealidad del determinante", texto)
        self.assertIn("dos columnas iguales", texto)
        self.assertIn("Dᵢ=xᵢD", texto)
        self.assertIn("Esta sustitución produce D₁", texto)
        self.assertIn("x₁ = D₁/D = 2/3 = 2/3", texto)
        self.assertIn("x₂ = D₂/D = -1/3 = -1/3", texto)
        self.assertIn("Entrada (2,1): 1 - (1/2)(2) = 0", texto)
        self.assertIn("Entrada (2,2): 0 - (1/2)(1) = -1/2", texto)
        self.assertIn("(2)(2/3) + (1)(-1/3) = 1 = 1", texto)
        self.assertIn("(1)(2/3) + (2)(-1/3) = 0 = 0", texto)
        self.assertIn("Conclusión: la solución satisface todas las ecuaciones originales.", texto)

        cursor = self.assert_traza_determinante_en_orden(
            texto, "Cálculo de D", datos["pasos_determinante"]
        )
        cursor = texto.index("D = 3", cursor) + len("D = 3")
        for reemplazo in datos["reemplazos"]:
            indice = reemplazo["indice"] + 1
            subindice = str(indice).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))
            nombre = f"Cálculo de D{subindice}"
            cursor = self.assert_traza_determinante_en_orden(
                texto, nombre, reemplazo["pasos_determinante"], cursor
            )
            determinante = formatear_valor(reemplazo["determinante"])
            etiqueta = f"D{subindice} = {determinante}"
            cursor = texto.index(etiqueta, cursor) + len(etiqueta)

    def test_intercambio_de_filas_interpreta_cambio_de_signo(self):
        A = [[0, 1], [2, 3]]
        datos = resolver_cramer(A, [1, 5])
        texto = self.presentar(A, [1, 5])

        self.assertIn("Intercambiar F1 y F2; cambia el signo.", texto)
        self.assertIn("Intercambiar dos filas cambia el signo del determinante", texto)
        self.assertIn("D = -2", texto)
        self.assertEqual(datos["determinante"], Fraction(-2))
        cursor = self.assert_traza_determinante_en_orden(
            texto, "Cálculo de D", datos["pasos_determinante"]
        )
        expresion_determinante = (
            "det(A) = signo (-1) × producto diagonal (2) = -2."
        )
        self.assertIn(expresion_determinante, texto[cursor:])

    def test_singular_no_clasifica_si_no_tiene_o_tiene_infinitas_soluciones(self):
        texto = self.presentar([[1, 2], [2, 4]], [3, 6])

        self.assertIn("D = 0: la regla de Cramer no determina una solución única", texto)
        self.assertIn("El sistema puede ser incompatible o tener infinitas soluciones", texto)
        self.assertNotIn("El sistema es incompatible.", texto)
        self.assertNotIn("El sistema tiene infinitas soluciones.", texto)


if __name__ == "__main__":
    unittest.main()
