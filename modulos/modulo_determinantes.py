"""Ventana independiente para calcular determinantes de matrices cuadradas."""

import customtkinter as ctk

from backend.matriz import formatear_valor
from backend.matrices import determinante_triangular
from modulos._comun import (
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    entrada_numero,
    formatear_matriz,
    leer_entero,
    leer_fraccion,
    mensaje_error,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
)


def determinante_con_pasos(A):
    """
    Conserva la API de la interfaz y delega el algoritmo al backend.
    """
    return determinante_triangular(A)


class ModuloDeterminantes(ctk.CTkFrame):
    """Permite ingresar una matriz cuadrada y analizar su determinante en el panel principal."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Crea la pantalla, su logotipo, el control de orden y las acciones."""
        zonas = crear_estructura(
            self,
            self.on_back,
            numero=5,
            titulo="Determinantes",
            descripcion="Calcula det(A) paso a paso y dice si A tiene inversa.",
            logo=(
                "+---------+\n"
                "| det(A)  |  MÓDULO: DETERMINANTES\n"
                "+---------+  Pivotes, intercambios de fila y valor exacto"
            ),
            pasos=[
                "Escribe el tamaño n de tu matriz cuadrada (n × n) y pulsa "
                "«Crear tabla».",
                "Llena la matriz A fila por fila.",
                "Pulsa «Calcular determinante».",
            ],
            clave_teoremas="determinantes",
            indicacion="Aquí verás la eliminación hasta la forma triangular, "
                       "los pivotes, el valor de det(A) y si A es invertible.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido

        controles, entradas = crear_controles(
            contenido, [("n", "Tamaño n", "2", 90)], self.actualizar_entradas
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_n = entradas["n"]

        subtitulo(contenido, "Matriz A").pack(anchor="w", padx=10, pady=(20, 6))
        self.tabla = ctk.CTkFrame(contenido, fg_color="transparent")
        self.tabla.pack(anchor="w", padx=6)

        boton_primario(zonas.acciones, "Calcular determinante", self.calcular).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(
            side="left"
        )

    def actualizar_entradas(self):
        """Construye una cuadrícula n por n para representar una matriz cuadrada."""
        try:
            n = leer_entero(self.entry_n, "El orden n")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.tabla.winfo_children():
            widget.destroy()
        self.entradas = []
        for i in range(n):
            fila = []
            for j in range(n):
                entry = entrada_numero(self.tabla)
                entry.grid(row=i, column=j, padx=4, pady=4)
                fila.append(entry)
            self.entradas.append(fila)
        reemplazar_texto(self.resultado, "")

    def calcular(self):
        """Lee A y muestra pivotes, operaciones de fila y el valor de det(A)."""
        try:
            matriz = [
                [
                    leer_fraccion(entry, f"La entrada ({i + 1},{j + 1}) de A")
                    for j, entry in enumerate(fila)
                ]
                for i, fila in enumerate(self.entradas)
            ]
            determinante, pasos = determinante_con_pasos(matriz)
            lineas = [
                "MODULO 5 | CALCULO DEL DETERMINANTE",
                "=" * 56,
                "Matriz A:",
                formatear_matriz(matriz),
                "",
                "Eliminación hacia forma triangular:",
            ]
            for indice, (descripcion, estado) in enumerate(pasos, 1):
                lineas.extend([
                    f"Paso {indice}: {descripcion}",
                    formatear_matriz(estado),
                ])
            lineas.extend([
                "",
                f"det(A) = {formatear_valor(determinante)}",
                "A es invertible." if determinante != 0 else "A es singular; no tiene inversa.",
            ])
            resumen = f"det(A) = {formatear_valor(determinante)}   ·   " + (
                "A es invertible" if determinante != 0 else "A es singular (no tiene inversa)"
            )
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n", resumen)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        """Reinicia a cero todas las entradas de la matriz."""
        reiniciar_celdas(self.entradas)
        reemplazar_texto(self.resultado, "")
