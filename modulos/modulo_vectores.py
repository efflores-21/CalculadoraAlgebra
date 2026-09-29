"""Ventana del Módulo 2: vectores, combinaciones e independencia lineal."""

from fractions import Fraction
import customtkinter as ctk
from tkinter import messagebox

from backend.eliminacion import eliminacion_con_pasos
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


class ModuloVectores(ctk.CTkFrame):
    """Panel para estudiar independencia lineal sin abrir otra ventana."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_vectores = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Construye la interfaz del módulo y su flujo de entrada y resultado."""
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
            "MÓDULO 2: VECTORES E INDEPENDENCIA LINEAL\n"
            "Combinaciones lineales, vectores L.I. y L.D.\n"
            "Sistema homogéneo: c1*v1 + ... + ck*vk = 0",
        )

        controles = ctk.CTkFrame(self)
        controles.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(controles, text="Cantidad de vectores k:").grid(
            row=0, column=0, padx=(10, 4), pady=10
        )
        self.entry_k = ctk.CTkEntry(controles, width=70, justify="center")
        self.entry_k.insert(0, "2")
        self.entry_k.grid(row=0, column=1, padx=(0, 14), pady=10)
        ctk.CTkLabel(controles, text="Dimensión n:").grid(
            row=0, column=2, padx=(0, 4), pady=10
        )
        self.entry_n = ctk.CTkEntry(controles, width=70, justify="center")
        self.entry_n.insert(0, "2")
        self.entry_n.grid(row=0, column=3, padx=(0, 14), pady=10)
        ctk.CTkButton(
            controles, text="Aplicar dimensiones", command=self.actualizar_entradas
        ).grid(row=0, column=4, padx=5, pady=10)
        ctk.CTkButton(
            controles,
            text="0. Ver Teoremas Clave del Módulo",
            command=lambda: mostrar_teoremas(self, "vectores", "Vectores"),
        ).grid(row=0, column=5, padx=5, pady=10)

        ctk.CTkLabel(
            self,
            text=(
                "Cada columna de la matriz de entrada representa un vector. "
                "La independencia se decide resolviendo el sistema homogéneo."
            ),
            text_color="#AAB7C4",
            wraplength=960,
        ).pack(anchor="w", padx=14, pady=(0, 4))

        self.marco_entradas = ctk.CTkScrollableFrame(self, label_text="Vectores de entrada")
        self.marco_entradas.pack(fill="both", expand=True, padx=12, pady=8)
        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(fill="x", padx=12, pady=4)
        ctk.CTkButton(
            acciones,
            text="Analizar independencia lineal",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.analizar,
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(
            acciones,
            text="Limpiar",
            width=120,
            fg_color="transparent",
            border_width=1,
            command=self.limpiar,
        ).pack(side="left", padx=(5, 0))
        self.resultado = crear_resultado(self, height=280)

    def actualizar_entradas(self):
        """Lee k y n y construye campos para k vectores con n componentes."""
        try:
            k = leer_entero(self.entry_k, "La cantidad k")
            n = leer_entero(self.entry_n, "La dimensión n")
        except ValueError as error:
            mensaje_error(error)
            return

        for widget in self.marco_entradas.winfo_children():
            widget.destroy()
        self.entradas_vectores = []
        ctk.CTkLabel(
            self.marco_entradas,
            text="Cada columna corresponde a un vector vⱼ.",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, columnspan=k + 1, sticky="w", padx=6, pady=6)
        for j in range(k):
            ctk.CTkLabel(
                self.marco_entradas, text=f"v{j + 1}", font=ctk.CTkFont(weight="bold")
            ).grid(row=1, column=j + 1, padx=4, pady=4)
        for i in range(n):
            ctk.CTkLabel(self.marco_entradas, text=f"Componente {i + 1}").grid(
                row=i + 2, column=0, sticky="w", padx=6, pady=3
            )
            for j in range(k):
                entry = entrada_numero(self.marco_entradas)
                entry.grid(row=i + 2, column=j + 1, padx=3, pady=3)
                if len(self.entradas_vectores) <= j:
                    self.entradas_vectores.append([])
                self.entradas_vectores[j].append(entry)
        self.resultado.delete("1.0", "end")

    def leer_datos(self):
        """Lee los vectores de la tabla, equivalente a definir elementos de R^n."""
        if not self.entradas_vectores:
            raise ValueError("Primero aplica dimensiones válidas.")
        vectores = []
        for j, entradas in enumerate(self.entradas_vectores):
            vector = []
            for i, entry in enumerate(entradas):
                try:
                    vector.append(_a_fraction(entry.get().strip() or "0"))
                except (ValueError, ZeroDivisionError) as error:
                    raise ValueError(
                        f"El componente {i + 1} del vector v{j + 1} no es válido."
                    ) from error
            vectores.append(vector)
        return vectores

    def construir_matriz_columnas(self, vectores):
        """Forma A con los vectores como columnas: A[i,j] es componente i de vj."""
        dimension = len(vectores[0])
        return [
            [vectores[j][i] for j in range(len(vectores))]
            for i in range(dimension)
        ]

    def construir_sistema_homogeneo(self, matriz_columnas):
        """Construye [A|0], equivalente a resolver A*c=0 para independencia."""
        return [fila[:] + [Fraction(0, 1)] for fila in matriz_columnas]

    def eliminar_gauss_jordan(self, matriz_aumentada):
        """Reduce [A|0] con operaciones elementales, equivalente a resolver el homogéneo."""
        matriz_reducida, rango, pasos = eliminacion_con_pasos(
            matriz_aumentada, metodo="gauss-jordan", verbose=False
        )
        return matriz_reducida, rango, pasos

    def contar_pivotes(self, matriz_reducida, cantidad_vectores):
        """Cuenta columnas pivote, equivalente al rango de la matriz de columnas."""
        pivotes = []
        for fila in matriz_reducida:
            for columna in range(cantidad_vectores):
                if fila[columna] != 0:
                    pivotes.append(columna)
                    break
        return pivotes

    def determinar_veredicto(self, n, k, pivotes):
        """Decide L.I. si cada vector aporta pivote; en otro caso, decide L.D."""
        if k > n:
            return False
        return len(pivotes) == k

    def analizar(self):
        """Construye y resuelve A*c=0, mostrando reducción, rango y veredicto."""
        try:
            k = leer_entero(self.entry_k, "La cantidad k")
            n = leer_entero(self.entry_n, "La dimensión n")
            vectores = self.leer_datos()
            matriz = self.construir_matriz_columnas(vectores)
            aumentada = self.construir_sistema_homogeneo(matriz)
            reducida, rango, pasos = self.eliminar_gauss_jordan(aumentada)
            pivotes = self.contar_pivotes(reducida, k)
            independiente = self.determinar_veredicto(n, k, pivotes)
            libres = k - len(pivotes)

            lineas = [
                "VEREDICTO: LOS VECTORES SON "
                + ("L.I." if independiente else "L.D."),
                f"En R^{n}: k={k}, pivotes={len(pivotes)}, variables libres={libres}.",
                "",
                "Matriz de columnas A:",
                formatear_matriz(matriz),
                "Sistema homogéneo: A*c=0.",
                "Forma reducida [R|0]:",
                formatear_matriz(reducida),
                "",
                "Pasos principales de Gauss-Jordan:",
            ]
            operaciones = pasos[1:]
            if operaciones:
                for indice, paso in enumerate(operaciones, 1):
                    lineas.append(f"  {indice}) {paso['descripcion']}")
            else:
                lineas.append("  No se requieren operaciones de fila.")
            if k > n:
                lineas.append(f"Como k={k} > n={n}, el conjunto es dependiente.")
            if independiente:
                lineas.append("A*c=0 solo tiene la solución trivial c=0.")
            else:
                lineas.append("Hay una variable libre y existe una solución no trivial.")
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n")
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        """Reinicia todas las componentes ingresadas a cero y limpia el resultado."""
        for vector in self.entradas_vectores:
            for entry in vector:
                entry.delete(0, "end")
                entry.insert(0, "0")
        reemplazar_texto(self.resultado, "Entradas reiniciadas a cero.\n")
