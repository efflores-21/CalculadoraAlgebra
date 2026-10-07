"""Interfaz para factorizar A=LU y resolver Ax=b."""

import customtkinter as ctk

from backend.factorizacion_lu import resolver_lu
from modulos._comun import (
    boton_primario, boton_secundario, crear_controles, crear_estructura,
    entrada_numero, formatear_matriz, formatear_vector, leer_entero,
    leer_fraccion, mensaje_error, reemplazar_texto, reiniciar_celdas, subtitulo,
)


class ModuloLU(ctk.CTkFrame):
    """Factoriza una matriz cuadrada y resuelve un sistema mediante LU."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A = []
        self.entradas_b = []
        zonas = crear_estructura(
            self, on_back, numero=6, titulo="Factorización LU",
            descripcion="Factoriza A = LU y resuelve Ax = b por sustituciones.",
            logo="A = L U\nLy = b  →  Ux = y",
            pasos=[
                "Escribe el orden n de A y pulsa «Crear tabla».",
                "Llena A y el vector b.",
                "La matriz L es triangular inferior con diagonal unitaria; U es triangular superior.",
            ], clave_teoremas="lu",
            indicacion="Se muestran L, U, la sustitución hacia adelante y la sustitución hacia atrás.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido
        controles, entradas = crear_controles(
            contenido, [("n", "Orden n", "2", 90)], self.actualizar_entradas
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_n = entradas["n"]
        subtitulo(contenido, "Matriz A y vector b").pack(anchor="w", padx=10, pady=(18, 6))
        self.tabla = ctk.CTkFrame(contenido, fg_color="transparent")
        self.tabla.pack(anchor="w", padx=6)
        boton_primario(zonas.acciones, "Factorizar y resolver", self.calcular).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(side="left")
        self.actualizar_entradas()

    def actualizar_entradas(self):
        try:
            n = leer_entero(self.entry_n, "El orden n")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.tabla.winfo_children():
            widget.destroy()
        self.entradas_A, self.entradas_b = [], []
        for i in range(n):
            fila = []
            for j in range(n):
                campo = entrada_numero(self.tabla)
                campo.grid(row=i, column=j, padx=3, pady=3)
                fila.append(campo)
            b = entrada_numero(self.tabla)
            b.grid(row=i, column=n, padx=(14, 3), pady=3)
            self.entradas_A.append(fila)
            self.entradas_b.append(b)
        reemplazar_texto(self.resultado, "")

    def calcular(self):
        try:
            A = [[leer_fraccion(c, f"La entrada ({i + 1},{j + 1}) de A")
                  for j, c in enumerate(fila)] for i, fila in enumerate(self.entradas_A)]
            b = [leer_fraccion(c, f"La entrada {i + 1} de b") for i, c in enumerate(self.entradas_b)]
            L, U, y, x = resolver_lu(A, b)
            texto = "Factorización A = LU\nL =\n" + formatear_matriz(L)
            texto += "\n\nU =\n" + formatear_matriz(U)
            texto += "\n\nSustitución hacia adelante: Ly = b\ny = " + formatear_vector(y)
            texto += "\n\nSustitución hacia atrás: Ux = y\nx = " + formatear_vector(x)
            reemplazar_texto(self.resultado, texto + "\n", "Solución: x = " + formatear_vector(x))
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        reiniciar_celdas(self.entradas_A, self.entradas_b)
        reemplazar_texto(self.resultado, "")
