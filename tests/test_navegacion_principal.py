"""Pruebas del catálogo y la búsqueda del shell principal."""

import unittest

from main import CATEGORIAS, CLASES_MODULOS, MODULOS, buscar_modulos


class NavegacionPrincipal(unittest.TestCase):
    def test_cada_modulo_aparece_una_vez_y_tiene_una_clase(self):
        claves_catalogo = [modulo[0] for modulo in MODULOS]
        claves_categorias = [clave for _, claves in CATEGORIAS for clave in claves]

        self.assertEqual(len(claves_catalogo), 10)
        self.assertEqual(set(claves_catalogo), set(claves_categorias))
        self.assertEqual(len(claves_categorias), len(set(claves_categorias)))
        self.assertEqual(set(claves_catalogo), set(CLASES_MODULOS))

    def test_busqueda_coincide_sin_distinguir_tildes_ni_mayusculas(self):
        resultados = buscar_modulos("TRANSFORMACION")

        self.assertIn("transformaciones", {modulo[0] for modulo in resultados})

    def test_busqueda_por_categoria_y_descripcion(self):
        por_categoria = {modulo[0] for modulo in buscar_modulos("matrices")}
        por_descripcion = {modulo[0] for modulo in buscar_modulos("bisección")}

        self.assertTrue({"matrices", "determinantes", "propiedades"}.issubset(por_categoria))
        self.assertIn("metodos_numericos", por_descripcion)

    def test_busqueda_vacia_muestra_todas_las_herramientas(self):
        self.assertEqual(buscar_modulos("  "), MODULOS)


if __name__ == "__main__":
    unittest.main()
