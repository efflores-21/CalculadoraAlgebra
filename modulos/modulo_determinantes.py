"""Ventana independiente para calcular determinantes de matrices cuadradas."""

from fractions import Fraction
import customtkinter as ctk
from tkinter import messagebox

from backend.matriz import _a_fraction, formatear_valor
from modulos._comun import (
    crear_logo,
    crear_resultado,
    entrada_numero,
    formatear_matriz,
    leer_entero,
    mensaje_error,
    mostrar_teoremas,
    reemplazar_texto,
)


def determinante_con_pasos(A):
    """
    Calcula det(A) mediante eliminación triangular y devuelve los pasos.

    Algebraicamente, det(A) es el producto de los pivotes de una matriz
    triangular, ajustado por el signo de cada intercambio de filas.
    Sumar un múltiplo de una fila a otra no cambia el determinante.
    """
    if not A or not A[0]:
        raise ValueError("La matriz debe ser no vacía.")
    n = len(A)
    if any(len(fila) != n for fila in A):
        raise ValueError("El determinante solo está definido para matrices cuadradas.")
    matriz = [[_a_fraction(valor) for valor in fila] for fila in A]
    pasos = [("Matriz inicial", [fila[:] for fila in matriz])]
    signo = 1
    producto_pivotes = Fraction(1, 1)

    for columna in range(n):
        fila_pivote = columna
        while fila_pivote < n and matriz[fila_pivote][columna] == 0:
            fila_pivote += 1
        if fila_pivote == n:
            pasos.append((
                f"No hay pivote en columna {columna + 1}; det(A)=0.",
                [fila[:] for fila in matriz],
            ))
            return Fraction(0, 1), pasos
        if fila_pivote != columna:
            matriz[columna], matriz[fila_pivote] = matriz[fila_pivote], matriz[columna]
            signo *= -1
            pasos.append((
                f"Intercambiar F{columna + 1} y F{fila_pivote + 1}; cambia el signo.",
                [fila[:] for fila in matriz],
            ))
        pivote = matriz[columna][columna]
        producto_pivotes *= pivote
        pasos.append((
            f"Pivote {columna + 1}: {formatear_valor(pivote)}.",
            [fila[:] for fila in matriz],
        ))
        for fila in range(columna + 1, n):
            if matriz[fila][columna] != 0:
                factor = matriz[fila][columna] / pivote
                for j in range(columna, n):
                    matriz[fila][j] -= factor * matriz[columna][j]
                pasos.append((
                    f"F{fila + 1} <- F{fila + 1} - "
                    f"({formatear_valor(factor)})F{columna + 1}.",
                    [fila_actual[:] for fila_actual in matriz],
                ))

    determinante = signo * producto_pivotes
    pasos.append((
        "det(A) = signo por producto de pivotes = "
        f"{signo} * {formatear_valor(producto_pivotes)} "
        f"= {formatear_valor(determinante)}.",
        [fila[:] for fila in matriz],
    ))
    return determinante, pasos


class ModuloDeterminantes(ctk.CTkFrame):
    """Permite ingresar una matriz cuadrada y analizar su determinante en el panel principal."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Crea la ventana, su logotipo, el control de orden y las acciones."""
        ctk.CTkButton(
            self,
            text="<- Volver al menu principal",
            fg_color="transparent",
            border_width=1,
            width=210,
            command=self.on_back,
        ).pack(anchor="w", padx=12, pady=(10, 0))
        crear_logo(
            self,
            "+---------+\n"
            "| det(A)  |  MODULO 4: DETERMINANTES\n"
            "+---------+  Pivotes, intercambios de fila y valor exacto",
        )
        controles = ctk.CTkFrame(self)
        controles.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(controles, text="Orden de la matriz n:").pack(
            side="left", padx=(10, 5), pady=8
        )
        self.entry_n = ctk.CTkEntry(controles, width=70, justify="center")
        self.entry_n.insert(0, "2")
        self.entry_n.pack(side="left", padx=5)
        ctk.CTkButton(
            controles, text="Crear matriz", command=self.actualizar_entradas
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            controles,
            text="0. Ver Teoremas Clave del Módulo",
            command=lambda: mostrar_teoremas(self, "determinantes", "Determinantes"),
        ).pack(side="left", padx=5)
        self.tabla = ctk.CTkScrollableFrame(self, label_text="Matriz cuadrada A")
        self.tabla.pack(fill="both", expand=True, padx=12, pady=8)
        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(fill="x", padx=12, pady=4)
        ctk.CTkButton(
            acciones, text="Calcular determinante", command=self.calcular, height=38
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(
            acciones,
            text="Limpiar",
            width=110,
            fg_color="transparent",
            border_width=1,
            command=self.limpiar,
        ).pack(side="left", padx=(5, 0))
        self.resultado = crear_resultado(self, height=280)

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
                [_a_fraction(entry.get().strip() or "0") for entry in fila]
                for fila in self.entradas
            ]
            determinante, pasos = determinante_con_pasos(matriz)
            lineas = [
                "MODULO 4 | CALCULO DEL DETERMINANTE",
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
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n")
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Error", str(error))

    def limpiar(self):
        """Reinicia a cero todas las entradas de la matriz."""
        for fila in self.entradas:
            for entry in fila:
                entry.delete(0, "end")
                entry.insert(0, "0")
        reemplazar_texto(self.resultado, "Matriz reiniciada a cero.\n")
