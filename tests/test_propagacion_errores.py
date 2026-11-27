"""Verificación matemática de propagación general de incertidumbres."""

import math
import unittest

from backend.funciones import compilar_funcion, compilar_funcion_multivariable, identificar_variables
from backend.propagacion_errores import propagar_errores


class PropagacionErroresGeneral(unittest.TestCase):
    def calcular(self, expresion, valores, incertidumbres, metodo="maximo"):
        return propagar_errores(expresion, valores, incertidumbres, metodo)

    def test_funcion_de_una_variable(self):
        datos = self.calcular("x**2 + 3*x + 2", {"x": 2}, {"x": 0.1})
        self.assertEqual(datos["valor_funcion"], 12)
        self.assertEqual(datos["contribuciones"][0]["derivada_evaluada"], 7)
        self.assertAlmostEqual(datos["error_maximo"], 0.7)

    def test_ejemplo_de_dos_variables_da_21_y_error_maximo_2_6(self):
        datos = self.calcular("x**2*y + 3*y", {"x": 2, "y": 3}, {"x": 0.1, "y": 0.2})
        self.assertEqual(datos["valor_funcion"], 21)
        self.assertEqual([fila["derivada_evaluada"] for fila in datos["contribuciones"]], [12, 7])
        self.assertAlmostEqual(datos["error_maximo"], 2.6)

    def test_ejemplo_de_referencia_da_incertidumbre_estadistica_esperada(self):
        datos = self.calcular("x**2*y + 3*y", {"x": 2, "y": 3}, {"x": 0.1, "y": 0.2}, "estadistico")
        self.assertAlmostEqual(datos["incertidumbre_estadistica"], math.sqrt(3.4))
        self.assertAlmostEqual(datos["incertidumbre_resultado"], 1.8439088915)

    def test_funcion_de_tres_variables(self):
        datos = self.calcular("x*y*z + x**2 + z**2", {"x": 1, "y": 2, "z": 3},
                              {"x": 0.1, "y": 0.2, "z": 0.3})
        self.assertEqual(datos["valor_funcion"], 16)
        self.assertEqual([fila["derivada_evaluada"] for fila in datos["contribuciones"]], [8, 3, 8])

    def test_funcion_polinomica(self):
        datos = self.calcular("x**3 - 2*x", {"x": 2}, {"x": 0.5})
        self.assertEqual(datos["valor_funcion"], 4)
        self.assertEqual(datos["contribuciones"][0]["derivada_evaluada"], 10)

    def test_funcion_racional(self):
        datos = self.calcular("x/y", {"x": 6, "y": 2}, {"x": 0.1, "y": 0.2})
        self.assertEqual(datos["valor_funcion"], 3)
        self.assertAlmostEqual(datos["contribuciones"][0]["derivada_evaluada"], 0.5)
        self.assertAlmostEqual(datos["contribuciones"][1]["derivada_evaluada"], -1.5)

    def test_funcion_exponencial(self):
        datos = self.calcular("exp(x)", {"x": 0}, {"x": 0.1})
        self.assertEqual(datos["valor_funcion"], 1)
        self.assertAlmostEqual(datos["contribuciones"][0]["derivada_evaluada"], 1)

    def test_funcion_trigonometrica(self):
        datos = self.calcular("sin(x)", {"x": 0}, {"x": 0.1})
        self.assertEqual(datos["valor_funcion"], 0)
        self.assertAlmostEqual(datos["contribuciones"][0]["derivada_evaluada"], 1)

    def test_funcion_constante_no_requiere_variables(self):
        datos = self.calcular("5", {}, {})
        self.assertEqual(datos["variables"], [])
        self.assertEqual(datos["error_maximo"], 0)
        self.assertEqual(datos["incertidumbre_estadistica"], 0)

    def test_derivada_parcial_nula_da_contribucion_cero(self):
        datos = self.calcular("x*y", {"x": 2, "y": 0}, {"x": 0.5, "y": 0.1})
        self.assertEqual(datos["contribuciones"][0]["derivada_evaluada"], 0)
        self.assertEqual(datos["contribuciones"][0]["contribucion_maxima"], 0)

    def test_incertidumbre_cero_da_contribucion_cero(self):
        datos = self.calcular("x**2", {"x": 3}, {"x": 0})
        self.assertEqual(datos["error_maximo"], 0)
        self.assertEqual(datos["incertidumbre_estadistica"], 0)

    def test_error_maximo_es_suma_de_contribuciones_absolutas(self):
        datos = self.calcular("x**2*y+3*y", {"x": 2, "y": 3}, {"x": 0.1, "y": 0.2})
        self.assertAlmostEqual(datos["error_maximo"], sum(f["contribucion_maxima"] for f in datos["contribuciones"]))

    def test_incertidumbre_estadistica_es_combinacion_cuadratica(self):
        datos = self.calcular("x**2*y+3*y", {"x": 2, "y": 3}, {"x": 0.1, "y": 0.2}, "estadistico")
        self.assertAlmostEqual(datos["incertidumbre_estadistica"]**2, 1.2**2 + 1.4**2)

    def test_los_dos_metodos_no_se_confunden(self):
        datos = self.calcular("x**2*y+3*y", {"x": 2, "y": 3}, {"x": 0.1, "y": 0.2})
        self.assertNotAlmostEqual(datos["error_maximo"], datos["incertidumbre_estadistica"])
        self.assertEqual(datos["nombre_metodo"], "Error máximo")

    def test_contribuciones_individuales(self):
        datos = self.calcular("x**2*y+3*y", {"x": 2, "y": 3}, {"x": 0.1, "y": 0.2})
        self.assertAlmostEqual(datos["contribuciones"][0]["contribucion_maxima"], 1.2)
        self.assertAlmostEqual(datos["contribuciones"][1]["contribucion_maxima"], 1.4)

    def test_derivadas_parciales_se_evalua_en_punto_indicado(self):
        datos = self.calcular("x**2*y+3*y", {"x": 2, "y": 3}, {"x": 0, "y": 0})
        derivadas = {f["variable"]: f["derivada_evaluada"] for f in datos["contribuciones"]}
        self.assertEqual(derivadas, {"x": 12, "y": 7})

    def test_error_relativo_porcentual(self):
        datos = self.calcular("x**2", {"x": 2}, {"x": 0.1})
        self.assertAlmostEqual(datos["error_relativo_porcentual"], 10)

    def test_error_relativo_indefinido_si_funcion_es_cero(self):
        datos = self.calcular("x", {"x": 0}, {"x": 0.1})
        self.assertIsNone(datos["error_relativo_porcentual"])

    def test_rechaza_incertidumbre_negativa(self):
        with self.assertRaisesRegex(ValueError, "mayor o igual que cero"):
            self.calcular("x", {"x": 1}, {"x": -0.1})

    def test_rechaza_funcion_no_permitida(self):
        with self.assertRaises(ValueError):
            self.calcular("__import__('os')", {"x": 1}, {"x": 0.1})

    def test_rechaza_variable_no_declarada_en_datos(self):
        with self.assertRaisesRegex(ValueError, "Variable no válida"):
            self.calcular("x+y", {"x": 1, "y": 2, "z": 3}, {"x": 0.1, "y": 0.1, "z": 0.1})

    def test_rechaza_funcion_no_definida_en_punto(self):
        with self.assertRaises(ValueError):
            self.calcular("log(x)", {"x": -1}, {"x": 0.1})

    def test_rechaza_division_entre_cero(self):
        with self.assertRaisesRegex(ValueError, "división entre cero"):
            self.calcular("1/x", {"x": 0}, {"x": 0.1})

    def test_fracciones_exactas_en_derivadas_simbólicas(self):
        datos = self.calcular("x/3 + y/2", {"x": 3, "y": 2}, {"x": 0.1, "y": 0.2})
        expresiones = {fila["variable"]: str(fila["derivada"]) for fila in datos["contribuciones"]}
        self.assertEqual(expresiones, {"x": "1/3", "y": "1/2"})

    def test_identifica_variables_y_funciones_permitidas(self):
        self.assertEqual(identificar_variables("x**2*y + sin(z)"), ("x", "y", "z"))
        self.assertEqual(compilar_funcion_multivariable("x+y").variables, ("x", "y"))

    def test_los_cambios_no_alteran_el_parser_univariable_existente(self):
        self.assertAlmostEqual(compilar_funcion("sin(x)+x**2")(0.5), math.sin(0.5) + 0.25)

    def test_rechaza_valor_o_incertidumbre_ausente(self):
        with self.assertRaisesRegex(ValueError, "Falta un valor"):
            self.calcular("x+y", {"x": 1}, {"x": 0.1, "y": 0.2})
        with self.assertRaisesRegex(ValueError, "Falta una incertidumbre"):
            self.calcular("x+y", {"x": 1, "y": 2}, {"x": 0.1})

    def test_rechaza_entradas_no_numericas(self):
        with self.assertRaisesRegex(ValueError, "número real finito"):
            self.calcular("x", {"x": "no"}, {"x": 0.1})
        with self.assertRaisesRegex(ValueError, "número real finito"):
            self.calcular("x", {"x": 1}, {"x": "no"})

    def test_limita_cantidad_de_variables(self):
        with self.assertRaisesRegex(ValueError, "como máximo 5 variables"):
            identificar_variables("a+b+c+d+f+g")

    def test_rechaza_derivada_parcial_no_existente_en_el_punto(self):
        with self.assertRaisesRegex(ValueError, "derivada parcial respecto de x no existe"):
            self.calcular("abs(x)", {"x": 0}, {"x": 0.1})


if __name__ == "__main__":
    unittest.main()
