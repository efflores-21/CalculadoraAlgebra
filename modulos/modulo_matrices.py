"""Ventana del módulo de operaciones con matrices."""

from fractions import Fraction
import customtkinter as ctk
from tkinter import messagebox

from backend.matriz import _a_fraction, formatear_valor
from backend.operaciones_matriciales import (
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    resta_matrices,
    suma_matrices,
)
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


def transponer_matriz(A):
    """Intercambia filas y columnas, equivalente a definir (A^T)[i,j]=A[j,i]."""
    if not A or not A[0]:
        raise ValueError("A debe ser una matriz no vacía.")
    columnas = len(A[0])
    if any(len(fila) != columnas for fila in A):
        raise ValueError("A debe ser rectangular.")
    return [[A[i][j] for i in range(len(A))] for j in range(columnas)]


def invertir_matriz(A):
    """
    Calcula A^-1 reduciendo [A|I] a [I|A^-1] por Gauss-Jordan.

    El procedimiento algebraico usa solo operaciones elementales de fila.
    Si no se puede obtener la identidad a la izquierda, A es singular y no
    tiene inversa.
    """
    if not A or not A[0]:
        raise ValueError("A debe ser una matriz no vacía.")
    n = len(A)
    if any(len(fila) != n for fila in A):
        raise ValueError("La inversa solo está definida para matrices cuadradas.")
    aumentada = [
        [_a_fraction(valor) for valor in A[i]]
        + [Fraction(1 if i == j else 0) for j in range(n)]
        for i in range(n)
    ]
    pasos = [("Matriz aumentada inicial [A|I]", [fila[:] for fila in aumentada])]

    for columna in range(n):
        fila_pivote = columna
        while fila_pivote < n and aumentada[fila_pivote][columna] == 0:
            fila_pivote += 1
        if fila_pivote == n:
            raise ValueError("La matriz es singular; su determinante es cero y no tiene inversa.")
        if fila_pivote != columna:
            aumentada[columna], aumentada[fila_pivote] = (
                aumentada[fila_pivote], aumentada[columna]
            )
            pasos.append((
                f"Intercambiar F{columna + 1} y F{fila_pivote + 1}",
                [fila[:] for fila in aumentada],
            ))
        pivote = aumentada[columna][columna]
        aumentada[columna] = [valor / pivote for valor in aumentada[columna]]
        pasos.append((
            f"Dividir F{columna + 1} entre {formatear_valor(pivote)}",
            [fila[:] for fila in aumentada],
        ))
        for fila in range(n):
            if fila == columna:
                continue
            factor = aumentada[fila][columna]
            if factor != 0:
                aumentada[fila] = [
                    aumentada[fila][j] - factor * aumentada[columna][j]
                    for j in range(2 * n)
                ]
                pasos.append((
                    f"F{fila + 1} <- F{fila + 1} - "
                    f"({formatear_valor(factor)})F{columna + 1}",
                    [fila_actual[:] for fila_actual in aumentada],
                ))
    inversa = [fila[n:] for fila in aumentada]
    return inversa, pasos


class ModuloMatrices(ctk.CTkFrame):
    """Proporciona un panel propio para operaciones matriciales."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A = []
        self.entradas_B = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Construye los controles, tablas y área de resultados del módulo."""
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
            "[ A ][ B ]  MODULO 3: ALGEBRA DE MATRICES\n"
            "[ C ][ D ]  Operaciones, traspuesta e inversa\n"
            "A+B | A-B | kA | A*B | A^T | A^-1",
        )
        controles = ctk.CTkFrame(self)
        controles.pack(fill="x", padx=12, pady=6)
        self.entries_dim = {}
        for columna, (clave, etiqueta, inicial) in enumerate((
            ("am", "A filas", "2"), ("an", "A columnas", "2"),
            ("bm", "B filas", "2"), ("bn", "B columnas", "2"),
        )):
            ctk.CTkLabel(controles, text=etiqueta).grid(
                row=0, column=columna * 2, padx=(6, 2), pady=8
            )
            entry = ctk.CTkEntry(controles, width=55, justify="center")
            entry.insert(0, inicial)
            entry.grid(row=0, column=columna * 2 + 1, padx=(0, 5))
            self.entries_dim[clave] = entry
        ctk.CTkButton(
            controles, text="Aplicar dimensiones", command=self.actualizar_entradas
        ).grid(row=0, column=8, padx=4)
        ctk.CTkButton(
            controles,
            text="0. Ver Teoremas Clave del Módulo",
            command=lambda: mostrar_teoremas(self, "matrices", "Matrices"),
        ).grid(row=0, column=9, padx=4)
        escalar_frame = ctk.CTkFrame(self, fg_color="transparent")
        escalar_frame.pack(fill="x", padx=12, pady=(0, 5))
        ctk.CTkLabel(escalar_frame, text="Escalar k:").pack(side="left", padx=(4, 6))
        self.entry_escalar = ctk.CTkEntry(escalar_frame, width=80, justify="center")
        self.entry_escalar.insert(0, "2")
        self.entry_escalar.pack(side="left")
        self.tablas = ctk.CTkFrame(self, fg_color="transparent")
        self.tablas.pack(fill="both", expand=True, padx=12, pady=6)
        self.tablas.grid_columnconfigure((0, 1), weight=1)
        self.tablas.grid_rowconfigure(0, weight=1)
        self.scroll_A = ctk.CTkScrollableFrame(self.tablas, label_text="Matriz A")
        self.scroll_A.grid(row=0, column=0, sticky="nsew", padx=5)
        self.scroll_B = ctk.CTkScrollableFrame(self.tablas, label_text="Matriz B")
        self.scroll_B.grid(row=0, column=1, sticky="nsew", padx=5)

        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(fill="x", padx=12, pady=4)
        operaciones = [
            ("A+B", lambda: self.calcular("suma")),
            ("A-B", lambda: self.calcular("resta")),
            ("kA", lambda: self.calcular("escalar")),
            ("A·B", lambda: self.calcular("producto")),
            ("Aᵀ", lambda: self.calcular("traspuesta")),
            ("A⁻¹", lambda: self.calcular("inversa")),
        ]
        for texto, comando in operaciones:
            ctk.CTkButton(acciones, text=texto, command=comando).pack(
                side="left", fill="x", expand=True, padx=3
            )
        ctk.CTkButton(
            acciones,
            text="Limpiar",
            width=100,
            fg_color="transparent",
            border_width=1,
            command=self.limpiar,
        ).pack(side="left", padx=3)
        self.resultado = crear_resultado(self, height=260)

    def actualizar_entradas(self):
        """Valida las dimensiones e inicializa las celdas de A y B."""
        try:
            dimensiones = {
                clave: leer_entero(entry, f"Dimensión {clave}")
                for clave, entry in self.entries_dim.items()
            }
        except ValueError as error:
            mensaje_error(error)
            return
        self.entradas_A = self._construir_tabla(
            self.scroll_A, dimensiones["am"], dimensiones["an"]
        )
        self.entradas_B = self._construir_tabla(
            self.scroll_B, dimensiones["bm"], dimensiones["bn"]
        )
        reemplazar_texto(self.resultado, "")

    def _construir_tabla(self, parent, filas, columnas):
        """Crea las entradas de una matriz, equivalente a preparar M_mxn."""
        for widget in parent.winfo_children():
            widget.destroy()
        entradas = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                celda = entrada_numero(parent)
                celda.grid(row=i, column=j, padx=3, pady=3)
                fila.append(celda)
            entradas.append(fila)
        return entradas

    def _leer_matriz(self, entradas, nombre):
        """Lee y convierte las celdas de una matriz a números racionales exactos."""
        try:
            return [
                [_a_fraction(celda.get().strip() or "0") for celda in fila]
                for fila in entradas
            ]
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError(f"Hay un valor inválido en la matriz {nombre}.") from error

    def calcular(self, operacion):
        """Ejecuta la operación seleccionada, equivalente a aplicar su definición matricial."""
        try:
            A = self._leer_matriz(self.entradas_A, "A")
            if operacion == "suma":
                B = self._leer_matriz(self.entradas_B, "B")
                C = suma_matrices(A, B)
                texto = "A+B, entrada a entrada:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += (
                            f"c{i + 1},{j + 1} = {formatear_valor(A[i][j])} + "
                            f"{formatear_valor(B[i][j])} = {formatear_valor(C[i][j])}\n"
                        )
                texto += "\nResultado A+B:\n" + formatear_matriz(C)
            elif operacion == "resta":
                B = self._leer_matriz(self.entradas_B, "B")
                C = resta_matrices(A, B)
                texto = "A-B, entrada a entrada:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += (
                            f"c{i + 1},{j + 1} = {formatear_valor(A[i][j])} - "
                            f"{formatear_valor(B[i][j])} = {formatear_valor(C[i][j])}\n"
                        )
                texto += "\nResultado A-B:\n" + formatear_matriz(C)
            elif operacion == "escalar":
                k = _a_fraction(self.entry_escalar.get().strip() or "0")
                C = multiplicar_escalar_matriz(k, A)
                texto = f"k={formatear_valor(k)}; cada entrada de A se multiplica por k:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += (
                            f"c{i + 1},{j + 1}: {formatear_valor(k)}*"
                            f"{formatear_valor(A[i][j])}={formatear_valor(C[i][j])}\n"
                        )
                texto += "\nResultado kA:\n" + formatear_matriz(C)
            elif operacion == "producto":
                B = self._leer_matriz(self.entradas_B, "B")
                C = multiplicar_matrices(A, B)
                lineas = ["A·B: cada entrada es el producto punto de fila por columna."]
                for i in range(len(A)):
                    for j in range(len(B[0])):
                        productos = [
                            f"({formatear_valor(A[i][k])}*{formatear_valor(B[k][j])})"
                            for k in range(len(A[0]))
                        ]
                        lineas.append(
                            f"c{i + 1},{j + 1} = " + " + ".join(productos)
                            + f" = {formatear_valor(C[i][j])}"
                        )
                lineas.extend(["", "Resultado A·B:", formatear_matriz(C)])
                texto = "\n".join(lineas)
            elif operacion == "traspuesta":
                C = transponer_matriz(A)
                texto = (
                    "Traspuesta: las filas de A pasan a ser columnas.\n"
                    "A =\n" + formatear_matriz(A)
                    + "\n\nA^T =\n" + formatear_matriz(C)
                )
            else:
                C, pasos = invertir_matriz(A)
                lineas = ["Inversa por Gauss-Jordan: transformar [A|I] en [I|A^-1]."]
                for indice, (descripcion, matriz_paso) in enumerate(pasos, 1):
                    lineas.extend([
                        f"Paso {indice}: {descripcion}",
                        formatear_matriz(matriz_paso),
                    ])
                lineas.extend(["", "A^-1 =", formatear_matriz(C)])
                texto = "\n".join(lineas)
            reemplazar_texto(self.resultado, texto + "\n")
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Error", str(error))

    def limpiar(self):
        """Restaura a cero todas las entradas de las matrices y el escalar."""
        for matriz in (self.entradas_A, self.entradas_B):
            for fila in matriz:
                for celda in fila:
                    celda.delete(0, "end")
                    celda.insert(0, "0")
        self.entry_escalar.delete(0, "end")
        self.entry_escalar.insert(0, "0")
        reemplazar_texto(self.resultado, "Matrices y escalar reiniciados a cero.\n")
