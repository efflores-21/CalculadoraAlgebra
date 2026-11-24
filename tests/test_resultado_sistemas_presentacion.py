"""Pruebas del agrupado visual del resultado de Sistemas."""

import unittest

from modulos.modulo_sistemas import (
    ESTADOS_PRESENTACION,
    _organizar_secciones_resultado,
)


class PresentacionResultadoSistemasTests(unittest.TestCase):
    def test_clasificaciones_distinguen_tres_resultados_y_metodo_no_concluyente(self):
        self.assertEqual(ESTADOS_PRESENTACION["unica"][0], "Solución única")
        self.assertEqual(ESTADOS_PRESENTACION["infinitas"][0], "Infinitas soluciones")
        self.assertIn("incompatible", ESTADOS_PRESENTACION["incompatible"][0])
        self.assertIn("no concluyente", ESTADOS_PRESENTACION["no_concluyente"][0].lower())

    def test_organizacion_conserva_todas_las_lineas_y_su_orden(self):
        texto = (
            "MÓDULO 1 | SISTEMAS\n"
            "\n"
            "Paso 1: matriz aumentada\n"
            "[ 1  2 | 3 ]\n"
            "\n"
            "VERIFICACIÓN EN LAS ECUACIONES ORIGINALES:\n"
            "Ecuación 1: 1(3) = 3\n"
        )

        secciones = _organizar_secciones_resultado(texto)

        self.assertEqual("\n".join(linea for seccion in secciones for linea in seccion), texto)
        self.assertGreaterEqual(len(secciones), 3)
        self.assertIn("Paso 1: matriz aumentada", secciones[1])
        self.assertIn("VERIFICACIÓN EN LAS ECUACIONES ORIGINALES:", secciones[2])

    def test_separa_soluciones_generales_y_conclusiones(self):
        secciones = _organizar_secciones_resultado(
            "Desarrollo\n"
            "Solución:\n"
            "x₁ = 2\n"
            "Conclusión: la solución satisface el sistema.\n"
        )

        encabezados = [seccion[0] for seccion in secciones]
        self.assertEqual(encabezados, ["Desarrollo", "Solución:", "Conclusión: la solución satisface el sistema."])


if __name__ == "__main__":
    unittest.main()
