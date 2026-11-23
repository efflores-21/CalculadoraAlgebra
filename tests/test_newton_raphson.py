"""Pruebas del backend Newton-Raphson y la derivación simbólica segura."""

import math
import unittest

from backend.newton_raphson import preparar_funcion, resolver_newton_raphson


class NewtonRaphson(unittest.TestCase):
    def test_deriva_y_evalua_la_funcion_y_su_derivada(self):
        preparada = preparar_funcion("sin(x) + x**2")
        self.assertEqual(preparada["derivada"], "2*x + cos(x)")
        self.assertAlmostEqual(preparada["funcion"](0), 0)
        self.assertAlmostEqual(preparada["evaluar_derivada"](0), 1)

    def test_converge_a_raiz_conocida_y_registra_iteraciones(self):
        datos = resolver_newton_raphson("x**2 - 2", 1, 1e-6, 100)
        self.assertTrue(datos["convergio"])
        self.assertEqual(datos["estado"], "convergido")
        self.assertAlmostEqual(datos["aproximacion"], math.sqrt(2), delta=1e-7)
        self.assertLess(datos["residuo_final"], 1e-7)
        self.assertLessEqual(datos["error_final"], 1e-6)
        self.assertEqual(datos["iteraciones"], len(datos["tabla"]))
        self.assertAlmostEqual(
            datos["tabla"][0]["xi_siguiente"],
            datos["tabla"][0]["xi"] - datos["tabla"][0]["fxi"] / datos["tabla"][0]["derivada"],
        )

    def test_casos_conocidos_y_cada_fila_se_verifican_independientemente(self):
        casos = [
            ("A", "x**2-4", 3.0, 2.0, lambda x: x**2 - 4, lambda x: 2*x),
            ("B", "x**2-9", -2.0, -3.0, lambda x: x**2 - 9, lambda x: 2*x),
            ("D", "cos(x)-x", 1.0, 0.7390851332,
             lambda x: math.cos(x)-x, lambda x: -math.sin(x)-1),
            ("E", "e**x-2", 1.0, math.log(2), lambda x: math.exp(x)-2, math.exp),
        ]
        for nombre, expresion, inicial, raiz, f, df in casos:
            with self.subTest(caso=nombre):
                datos = resolver_newton_raphson(expresion, inicial, 1e-8, 100)
                self.assertTrue(datos["convergio"])
                self.assertAlmostEqual(datos["aproximacion"], raiz, delta=1e-7)
                self.assertAlmostEqual(f(datos["aproximacion"]), 0, delta=1e-8)
                for fila in datos["tabla"]:
                    self.assertAlmostEqual(fila["fxi"], f(fila["xi"]), delta=1e-12)
                    self.assertAlmostEqual(fila["derivada"], df(fila["xi"]), delta=1e-12)
                    siguiente = fila["xi"] - fila["fxi"] / fila["derivada"]
                    self.assertAlmostEqual(fila["xi_siguiente"], siguiente, delta=1e-12)
                    if fila["xi_siguiente"] != 0:
                        error = abs((fila["xi_siguiente"] - fila["xi"]) / fila["xi_siguiente"]) * 100
                        self.assertAlmostEqual(fila["error_aproximado_porcentual"], error, delta=1e-12)
                    self.assertAlmostEqual(fila["residuo"], abs(f(fila["xi_siguiente"])), delta=1e-12)
        derivada_cos = preparar_funcion("cos(x)-x")["derivada"]
        self.assertEqual(derivada_cos, "-sin(x) - 1")

    def test_raiz_cero_y_la_inconsistencia_del_caso_x2_menos_uno(self):
        datos = resolver_newton_raphson("x", 1, 1e-8, 10)
        self.assertTrue(datos["convergio"])
        self.assertEqual(datos["aproximacion"], 0)
        self.assertIsNone(datos["error_final"])
        # x**2 - 1 tiene raíces -1 y 1; no tiene raíz cero.
        positivo = resolver_newton_raphson("x**2-1", 0.5, 1e-8, 100)
        negativo = resolver_newton_raphson("x**2-1", -0.5, 1e-8, 100)
        self.assertAlmostEqual(positivo["aproximacion"], 1, delta=1e-8)
        self.assertAlmostEqual(negativo["aproximacion"], -1, delta=1e-8)

    def test_raiz_multiple_converge_sin_rechazar_derivada_pequena_util(self):
        datos = resolver_newton_raphson("(x-1)**3", 2, 1e-6, 1000)
        self.assertTrue(datos["convergio"], datos["motivo"])
        self.assertAlmostEqual(datos["aproximacion"], 1, delta=1e-6)
        self.assertLess(abs(datos["aproximacion"] - 1) ** 3, 1e-12)
        self.assertGreater(datos["iteraciones"], 10)

    def test_no_declara_convergencia_si_el_error_es_pequeno_pero_residuo_no(self):
        # El escalamiento mantiene el residuo lejos de cero aunque el paso
        # porcentual sea diminuto al partir de un x0 grande.
        expresion = "1e20*(x-1000000000000)**3"
        datos = resolver_newton_raphson(expresion, 1000000000001, 1e-6, 1)
        self.assertFalse(datos["convergio"])
        self.assertEqual(datos["estado"], "maximo")
        self.assertLessEqual(datos["error_final"], 1e-6)
        self.assertGreater(datos["residuo_relativo_final"], 1e-6)
        self.assertIn("residuo relativo", datos["motivo"])

    def test_limite_en_caso_oscilatorio_y_convergencia_lenta(self):
        lento = resolver_newton_raphson("x**5-1", 10, 1e-8, 1000)
        self.assertTrue(lento["convergio"], lento["motivo"])
        self.assertAlmostEqual(lento["aproximacion"], 1, delta=1e-7)
        self.assertGreater(lento["iteraciones"], 10)
        oscilatorio = resolver_newton_raphson("x**3-2*x+2", 0, 1e-8, 12)
        self.assertFalse(oscilatorio["convergio"])
        self.assertEqual(oscilatorio["estado"], "maximo")
        self.assertEqual(oscilatorio["iteraciones"], 12)
        self.assertAlmostEqual(oscilatorio["residuo_final"], 2)
        self.assertEqual(len(oscilatorio["tabla"]), 12)

    def test_derivada_cero_detiene_sin_dividir(self):
        datos = resolver_newton_raphson("x**2 + 1", 0, 1e-6, 10)
        self.assertEqual(datos["estado"], "error")
        self.assertFalse(datos["convergio"])
        self.assertIn("derivada", datos["motivo"])
        self.assertEqual(datos["tabla"][0]["derivada"], 0)
        self.assertIsNone(datos["tabla"][0]["xi_siguiente"])

    def test_funcion_constante_sin_raiz_y_discontinuidad_se_detienen_con_estado(self):
        constante = resolver_newton_raphson("3", 2, 1e-8, 10)
        self.assertEqual(constante["estado"], "error")
        self.assertIn("derivada es cero", constante["motivo"])
        self.assertEqual(constante["residuo_final"], 3)
        discontinuidad = resolver_newton_raphson("1/x", 1, 1e-8, 1000)
        self.assertEqual(discontinuidad["estado"], "error")
        self.assertFalse(discontinuidad["convergio"])
        self.assertLessEqual(discontinuidad["iteraciones"], 1000)

    def test_derivada_constante(self):
        datos = resolver_newton_raphson("3*x - 9", 0, 1e-8, 5)
        self.assertTrue(datos["convergio"])
        self.assertEqual(datos["aproximacion"], 3)
        self.assertEqual(datos["derivada"], "3")

    def test_maximo_de_iteraciones_devuelve_parciales_sin_falsa_convergencia(self):
        datos = resolver_newton_raphson("x**2 - 2", 1, 1e-15, 1)
        self.assertEqual(datos["estado"], "maximo")
        self.assertFalse(datos["convergio"])
        self.assertEqual(datos["iteraciones"], 1)
        self.assertEqual(len(datos["tabla"]), 1)
        self.assertIsNotNone(datos["tabla"][0]["xi_siguiente"])

    def test_raiz_en_cero_no_inventa_error_porcentual(self):
        datos = resolver_newton_raphson("x", 1, 1e-6, 5)
        self.assertTrue(datos["convergio"])
        self.assertEqual(datos["aproximacion"], 0)
        self.assertIsNone(datos["error_final"])
        self.assertEqual(datos["residuo_final"], 0)

    def test_derivada_cercana_a_cero_se_informa(self):
        datos = resolver_newton_raphson("1e-300*x - 1", 0, 1e-6, 5)
        self.assertEqual(datos["estado"], "error")
        self.assertIn("cercana a cero", datos["motivo"])

    def test_funcion_fuera_de_dominio_se_devuelve_como_error(self):
        datos = resolver_newton_raphson("sqrt(x)", -1, 1e-6, 5)
        self.assertEqual(datos["estado"], "error")
        self.assertIn("dominio", datos["motivo"])

    def test_derivada_no_definida_y_resultado_no_finito_se_controlan(self):
        derivada = resolver_newton_raphson("asin(x)", 1, 1e-6, 5)
        self.assertEqual(derivada["estado"], "error")
        self.assertIn("derivada", derivada["motivo"])
        infinito = resolver_newton_raphson("exp(x)", 1000, 1e-6, 5)
        self.assertEqual(infinito["estado"], "error")
        self.assertIn("overflow", infinito["motivo"])

    def test_rechaza_expresiones_invalidas_o_inseguras(self):
        for expresion in ("x +", "__import__('os')", "x.__class__", "y + 1"):
            with self.subTest(expresion=expresion), self.assertRaises(ValueError):
                preparar_funcion(expresion)

    def test_valida_valor_inicial_tolerancia_y_maximo(self):
        casos = [("nan", 1e-6, 10), (True, 1e-6, 10), (0, 0, 10), (0, -1, 10), (0, 1e-6, 0),
                 (0, 1e-6, 1.5), (0, 1e-6, 10001)]
        for inicial, tolerancia, maximo in casos:
            with self.subTest(inicial=inicial, tolerancia=tolerancia, maximo=maximo), self.assertRaises(ValueError):
                resolver_newton_raphson("x-1", inicial, tolerancia, maximo)


if __name__ == "__main__":
    unittest.main()
