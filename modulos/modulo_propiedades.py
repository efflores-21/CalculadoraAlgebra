"""Panel que verifica la linealidad del producto matriz-vector."""

import customtkinter as ctk
from tkinter import messagebox

from backend.matriz import formatear_valor
from backend.propiedades import verificar_propiedades
from modulos._comun import (
    crear_logo,
    crear_resultado,
    entrada_numero,
    formatear_matriz,
    formatear_vector,
    leer_entero,
    leer_fraccion,
    mensaje_error,
    mostrar_teoremas,
    reemplazar_texto,
)


class ModuloPropiedades(ctk.CTkFrame):
    """Presenta A(u+v)=Au+Av y A(cu)=c(Au) en una pantalla separada."""

    def __init__(self, master, on_back):
        """Inicializa el panel con una matriz 2x2 y vectores de dimensión 2."""
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A = []
        self.entradas_u = []
        self.entradas_v = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Construye los controles para A,u,v,c y el área de pasos."""
        ctk.CTkButton(
            self,
            text="<- Volver al menú principal",
            fg_color="transparent",
            border_width=1,
            width=220,
            command=self.on_back,
        ).pack(anchor="w", padx=12, pady=(10, 0))
        crear_logo(
            self,
            "MÓDULO 6: PROPIEDADES DEL PRODUCTO MATRIZ-VECTOR\n"
            "A(u+v) = Au + Av\n"
            "A(cu) = c(Au)",
        )
        controles = ctk.CTkFrame(self)
        controles.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(controles, text="Filas m:").grid(row=0, column=0, padx=4)
        self.entry_m = ctk.CTkEntry(controles, width=58, justify="center")
        self.entry_m.insert(0, "2")
        self.entry_m.grid(row=0, column=1, padx=4)
        ctk.CTkLabel(controles, text="Columnas n:").grid(row=0, column=2, padx=4)
        self.entry_n = ctk.CTkEntry(controles, width=58, justify="center")
        self.entry_n.insert(0, "2")
        self.entry_n.grid(row=0, column=3, padx=4)
        ctk.CTkLabel(controles, text="Escalar c:").grid(row=0, column=4, padx=4)
        self.entry_c = ctk.CTkEntry(controles, width=70, justify="center")
        self.entry_c.insert(0, "2")
        self.entry_c.grid(row=0, column=5, padx=4)
        ctk.CTkButton(
            controles, text="Crear entradas", command=self.actualizar_entradas
        ).grid(row=0, column=6, padx=4)
        ctk.CTkButton(
            controles,
            text="0. Ver teoremas",
            command=lambda: mostrar_teoremas(
                self, "matrices", "Producto matriz-vector"
            ),
        ).grid(row=0, column=7, padx=4)

        self.panel_entradas = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_entradas.pack(fill="x", padx=12, pady=6)
        self.panel_entradas.grid_columnconfigure((0, 1, 2), weight=1)
        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(fill="x", padx=12, pady=4)
        ctk.CTkButton(
            acciones,
            text="Verificar ambas propiedades",
            height=40,
            command=self.verificar,
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(
            acciones,
            text="Limpiar",
            width=100,
            fg_color="transparent",
            border_width=1,
            command=self.limpiar,
        ).pack(side="left", padx=(5, 0))
        self.resultado = crear_resultado(self, height=280)

    def _crear_vector(self, parent, nombre, columnas):
        """Crea una fila de n entradas que representa un vector de R^n."""
        marco = ctk.CTkFrame(parent)
        marco.grid(sticky="nw", padx=5, pady=5)
        ctk.CTkLabel(marco, text=nombre, font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=4
        )
        entradas = []
        for j in range(columnas):
            celda = entrada_numero(marco, ancho=58)
            celda.grid(row=0, column=j + 1, padx=2, pady=4)
            entradas.append(celda)
        return entradas

    def actualizar_entradas(self):
        """Reconstruye la matriz A y los vectores con las dimensiones indicadas."""
        try:
            m = leer_entero(self.entry_m, "Filas m")
            n = leer_entero(self.entry_n, "Columnas n")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.panel_entradas.winfo_children():
            widget.destroy()

        marco_matriz = ctk.CTkFrame(self.panel_entradas)
        marco_matriz.grid(row=0, column=0, sticky="nsew", padx=5)
        ctk.CTkLabel(
            marco_matriz,
            text=f"Matriz A ({m}x{n})",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, columnspan=n, padx=5, pady=5)
        self.entradas_A = []
        for i in range(m):
            fila = []
            for j in range(n):
                celda = entrada_numero(marco_matriz, ancho=58)
                celda.grid(row=i + 1, column=j, padx=2, pady=2)
                fila.append(celda)
            self.entradas_A.append(fila)

        self.entradas_u = self._crear_vector(self.panel_entradas, "u =", n)
        self.entradas_u[0].master.grid_configure(row=0, column=1, sticky="nw")
        self.entradas_v = self._crear_vector(self.panel_entradas, "v =", n)
        self.entradas_v[0].master.grid_configure(row=1, column=1, sticky="nw")
        reemplazar_texto(self.resultado, "")

    def _leer_vector(self, entradas, nombre):
        """Convierte un conjunto de celdas a un vector de Fraction."""
        return [leer_fraccion(celda, nombre) for celda in entradas]

    def verificar(self):
        """Calcula y presenta las dos igualdades mediante pasos agrupados."""
        try:
            A = [
                [leer_fraccion(celda, "Una entrada de A") for celda in fila]
                for fila in self.entradas_A
            ]
            u = self._leer_vector(self.entradas_u, "u")
            v = self._leer_vector(self.entradas_v, "v")
            c = leer_fraccion(self.entry_c, "El escalar c")
            datos = verificar_propiedades(A, u, v, c)

            def vector(clave):
                return formatear_vector(datos[clave])

            estado_a = "SE CUMPLE" if datos["a_se_cumple"] else "NO SE CUMPLE"
            estado_b = "SE CUMPLE" if datos["b_se_cumple"] else "NO SE CUMPLE"
            texto = (
                "MÓDULO 6: PROPIEDADES DEL PRODUCTO MATRIZ-VECTOR\n"
                f"Datos: A={formatear_matriz(A)}; u={formatear_vector(u)}; "
                f"v={formatear_vector(v)}; c={formatear_valor(c)}\n\n"
                "A) A(u+v) = Au+Av\n"
                f"  1. u+v = {vector('a_u_mas_v')}\n"
                f"  2. A(u+v) = {vector('a_A_por_u_mas_v')}\n"
                f"  3. Au = {vector('a_Au')}; Av = {vector('a_Av')}\n"
                f"  4. Au+Av = {vector('a_Au_mas_Av')}\n"
                f"  Comparación: {vector('a_A_por_u_mas_v')} = "
                f"{vector('a_Au_mas_Av')} -> {estado_a}\n\n"
                "B) A(cu) = c(Au)\n"
                f"  1. cu = {vector('b_c_por_u')}\n"
                f"  2. A(cu) = {vector('b_A_por_cu')}\n"
                f"  3. Au = {vector('b_Au')}\n"
                f"  4. c(Au) = {vector('b_c_por_Au')}\n"
                f"  Comparación: {vector('b_A_por_cu')} = "
                f"{vector('b_c_por_Au')} -> {estado_b}\n"
            )
            reemplazar_texto(self.resultado, texto)
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Error", str(error))

    def limpiar(self):
        """Reinicia a cero la matriz, los vectores, el escalar y el resultado."""
        for fila in self.entradas_A:
            for celda in fila:
                celda.delete(0, "end")
                celda.insert(0, "0")
        for celda in self.entradas_u + self.entradas_v:
            celda.delete(0, "end")
            celda.insert(0, "0")
        self.entry_c.delete(0, "end")
        self.entry_c.insert(0, "0")
        reemplazar_texto(self.resultado, "Entradas reiniciadas a cero.\n")
