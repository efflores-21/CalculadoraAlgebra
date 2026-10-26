"""Pruebas pedagógicas de combinación e independencia lineal."""

import unittest
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch

from backend.vectores import es_combinacion_lineal
from modulos.modulo_operaciones_vectores import ModuloOperacionesVectores
from modulos.modulo_vectores import ModuloVectores


class Celda:
    def __init__(self, valor):
        self.valor = str(valor)

    def get(self):
        return self.valor


class ExplicacionesVectores(unittest.TestCase):
    def presentar_combinacion(self, vectores, objetivo):
        modulo = SimpleNamespace(
            leer_vectores=lambda: vectores,
            b_entries=[Celda(valor) for valor in objetivo],
            resultado=object(),
        )
        with patch("modulos.modulo_operaciones_vectores.reemplazar_texto") as reemplazar:
            ModuloOperacionesVectores.combinacion_lineal(modulo)
        return reemplazar.call_args.args[1]

    def presentar_independencia(self, vectores):
        modulo = SimpleNamespace(
            leer_datos=lambda: vectores,
            construir_matriz_columnas=lambda datos: ModuloVectores.construir_matriz_columnas(
                None, datos
            ),
            construir_sistema_homogeneo=lambda matriz: ModuloVectores.construir_sistema_homogeneo(
                None, matriz
            ),
            eliminar_gauss_jordan=lambda matriz: ModuloVectores.eliminar_gauss_jordan(
                None, matriz
            ),
            contar_pivotes=lambda matriz, cantidad: ModuloVectores.contar_pivotes(
                None, matriz, cantidad
            ),
            determinar_veredicto=lambda n, k, pivotes: ModuloVectores.determinar_veredicto(
                None, n, k, pivotes
            ),
            resultado=object(),
        )
        with patch("modulos.modulo_vectores.reemplazar_texto") as reemplazar:
            ModuloVectores.analizar(modulo)
        return reemplazar.call_args.args[1]

    def test_combinacion_exacta_escalado_suma_y_verificacion(self):
        vectores = [
            [Fraction(1, 2), Fraction(0), Fraction(1)],
            [Fraction(0), Fraction(1, 3), Fraction(1)],
            [Fraction(1), Fraction(1), Fraction(0)],
        ]
        objetivo = [Fraction(1), Fraction(-1), Fraction(-1)]
        texto = self.presentar_combinacion(vectores, objetivo)

        self.assertIn("dimensión 3", texto)
        self.assertIn("c₁ = 2", texto)
        self.assertIn("c₂ = -3", texto)
        self.assertIn("c₃ = 0", texto)
        self.assertIn("c₁·v₁: componente 1: (2)(1/2)=1", texto)
        self.assertIn("(-3)(1/3)=-1", texto)
        self.assertIn("Componente 1: 1 + 0 + 0 = 1 (objetivo b1 = 1)", texto)
        self.assertIn("Vector obtenido: (1, -1, -1)", texto)
        self.assertIn("La reconstrucción coincide con b", texto)

    def test_combinacion_con_coeficientes_libres_muestra_ejemplo_verificable(self):
        vectores = [[Fraction(1), Fraction(2)], [Fraction(2), Fraction(4)]]
        objetivo = [Fraction(2), Fraction(4)]
        texto = self.presentar_combinacion(vectores, objetivo)

        self.assertIn("infinitas representaciones", texto)
        self.assertIn("parámetro libre en 0", texto)
        self.assertIn("Vector obtenido: (2, 4)", texto)
        self.assertIn("La reconstrucción coincide con b", texto)
        self.assertIn("Después:", texto)

    def test_objetivo_fuera_del_espacio_generado_se_distingue(self):
        texto = self.presentar_combinacion([[Fraction(1), Fraction(0)]], [Fraction(0), Fraction(1)])
        self.assertIn("b NO es combinación lineal", texto)
        self.assertNotIn("Vector obtenido:", texto)

    def test_independencia_muestra_sistema_operaciones_estados_y_unica_solucion(self):
        vectores = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
        texto = self.presentar_independencia(vectores)

        self.assertIn("c₁·v₁ + … + cₖ·vₖ = 0", texto)
        self.assertIn("sistema homogéneo A·c=0", texto)
        self.assertIn("Estado inicial de [A|0]", texto)
        self.assertIn("Forma reducida final [R|0]", texto)
        self.assertIn("solo admite c₁=…=cₖ=0", texto)
        self.assertIn("linealmente independientes", texto)

    def test_dependencia_muestra_relacion_no_trivial_y_verifica_suma_cero(self):
        vectores = [
            [Fraction(1, 2), Fraction(1)],
            [Fraction(1), Fraction(2)],
            [Fraction(0), Fraction(0)],
        ]
        texto = self.presentar_independencia(vectores)

        self.assertIn("por eso los vectores son dependientes", texto)
        self.assertIn("solución no trivial", texto)
        self.assertIn("Coeficientes elegidos:", texto)
        self.assertIn("= (0, 0)", texto)
        self.assertIn("coincide con el vector cero", texto)
        self.assertIn("Intercambio F1", texto)
        self.assertIn("Antes:", texto)
        self.assertIn("Después:", texto)
        self.assertIn("Cálculo de la fila completa:", texto)

    def test_vectores_repetidos_y_mas_vectores_que_dimensiones_son_dependientes(self):
        repetidos = self.presentar_independencia([[Fraction(1), Fraction(2)], [Fraction(1), Fraction(2)]])
        demasiados = self.presentar_independencia([
            [Fraction(1), Fraction(0)],
            [Fraction(0), Fraction(1)],
            [Fraction(1), Fraction(1)],
        ])
        self.assertIn("dependientes", repetidos)
        self.assertIn("k=3", demasiados)
        self.assertIn("k>n", demasiados)
        self.assertIn("Coeficientes elegidos:", demasiados)

    def test_dimensiones_incompatibles_se_siguen_rechazando(self):
        with self.assertRaisesRegex(ValueError, "Dimensiones incompatibles"):
            es_combinacion_lineal([Fraction(1), Fraction(2)], [[Fraction(1)]])


if __name__ == "__main__":
    unittest.main()
