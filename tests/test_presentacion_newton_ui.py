"""Pruebas de formato y clasificación visual de Newton-Raphson."""

import unittest

from modulos.modulo_metodos_numericos import (
    _estado_visual_newton,
    _texto_procedimiento_newton,
)


class PresentacionNewtonUITests(unittest.TestCase):
    def test_distingue_convergencia_aproximacion_y_detenimientos(self):
        casos = (
            ({"convergio": True, "estado": "convergido", "motivo": "Tolerancia."},
             "Convergencia satisfactoria", "success"),
            ({"convergio": False, "estado": "maximo", "motivo": "Máximo."},
             "Aproximación obtenida", "warning"),
            ({"convergio": False, "estado": "error", "motivo": "La derivada es cero."},
             "derivada inválida", "warning"),
            ({"convergio": False, "estado": "error", "motivo": "Evaluación no finita."},
             "Error de evaluación", "error"),
        )
        for datos, texto, variante in casos:
            with self.subTest(estado=datos["estado"], motivo=datos["motivo"]):
                resultado = _estado_visual_newton(datos)
                self.assertIn(texto.lower(), resultado[0].lower())
                self.assertEqual(resultado[1], variante)

    def test_procedimiento_usa_los_valores_registrados_en_la_iteracion(self):
        datos = {
            "expresion": "x**2 - 2",
            "derivada": "2*x",
            "valor_inicial": 1.0,
            "motivo": "Se alcanzó la tolerancia.",
            "convergio": True,
            "tabla": [{
                "k": 1, "xi": 1.0, "fxi": -1.0, "derivada": 2.0,
                "xi_siguiente": 1.5, "error_aproximado_porcentual": 33.3,
                "residuo": 0.25,
            }],
        }

        texto = _texto_procedimiento_newton(datos, 0)

        self.assertIn("f′(x) = 2*x", texto)
        self.assertIn("xₙ₊₁ = 1 − (-1) / (2) = 1.5", texto)
        self.assertIn("Residuo |f(xₙ₊₁)|: 0.25", texto)
        self.assertIn("Criterio de terminación: Se alcanzó la tolerancia.", texto)

    def test_procedimiento_no_inventa_siguiente_paso_si_falla_la_derivada(self):
        datos = {
            "expresion": "x**2 + 1",
            "derivada": "2*x",
            "valor_inicial": 0.0,
            "motivo": "La derivada es cero.",
            "convergio": False,
            "tabla": [{
                "k": 1, "xi": 0.0, "fxi": 1.0, "derivada": 0.0,
                "xi_siguiente": None, "motivo": "La derivada es cero; no se puede continuar.",
            }],
        }

        texto = _texto_procedimiento_newton(datos, 0)

        self.assertIn("No se calculó xₙ₊₁.", texto)
        self.assertIn("La derivada es cero; no se puede continuar.", texto)
        self.assertNotIn("Sustitución: xₙ₊₁", texto)


if __name__ == "__main__":
    unittest.main()
