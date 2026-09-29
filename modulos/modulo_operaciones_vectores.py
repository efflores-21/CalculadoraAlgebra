"""Panel para suma, resta, escalares y combinación lineal de vectores."""

import customtkinter as ctk
from tkinter import messagebox

from backend.matriz import formatear_valor
from backend.vectores import (
    es_combinacion_lineal,
    multiplicar_escalar_vector,
    resta_vectores,
    suma_vectores,
)
from backend.eliminacion import resolver_sistema
from backend.clasificador import clasificar_sistema
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


class ModuloOperacionesVectores(ctk.CTkFrame):
    """Reúne las operaciones vectoriales y de combinación lineal del programa."""

    def __init__(self, master, on_back):
        """Prepara el panel y las entradas iniciales para operar con vectores."""
        super().__init__(master)
        self.on_back = on_back
        self.vectores_entries = []
        self.b_entries = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Construye controles, tabla vectorial y área de resultados."""
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
            "MÓDULO 2: OPERACIONES CON VECTORES\n"
            "Suma, resta, producto por escalar y combinación lineal\n"
            "Vectores en R^n",
        )

        controles = ctk.CTkFrame(self)
        controles.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(controles, text="Dimensión n:").grid(row=0, column=0, padx=4)
        self.entry_n = ctk.CTkEntry(controles, width=62, justify="center")
        self.entry_n.insert(0, "3")
        self.entry_n.grid(row=0, column=1, padx=4)
        ctk.CTkLabel(controles, text="Vectores generadores k:").grid(
            row=0, column=2, padx=4
        )
        self.entry_k = ctk.CTkEntry(controles, width=62, justify="center")
        self.entry_k.insert(0, "2")
        self.entry_k.grid(row=0, column=3, padx=4)
        ctk.CTkLabel(controles, text="Escalar c:").grid(row=0, column=4, padx=4)
        self.entry_c = ctk.CTkEntry(controles, width=75, justify="center")
        self.entry_c.insert(0, "2")
        self.entry_c.grid(row=0, column=5, padx=4)
        ctk.CTkButton(
            controles, text="Aplicar dimensiones", command=self.actualizar_entradas
        ).grid(row=0, column=6, padx=4)
        ctk.CTkButton(
            controles,
            text="0. Ver teoremas",
            command=lambda: mostrar_teoremas(
                self, "operaciones_vectores", "Operaciones con vectores"
            ),
        ).grid(row=0, column=7, padx=4)

        ctk.CTkLabel(
            self,
            text="La suma, resta y el escalar usan v1 y v2; la combinación lineal usa todos los vectores y b.",
            text_color="#AAB7C4",
            wraplength=950,
        ).pack(anchor="w", padx=14, pady=(0, 4))
        self.tabla = ctk.CTkScrollableFrame(self, label_text="Componentes de los vectores")
        self.tabla.pack(fill="both", expand=True, padx=12, pady=6)

        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(fill="x", padx=12, pady=4)
        botones = (
            ("v1 + v2", self.sumar),
            ("v1 - v2", self.restar),
            ("c · v1", self.escalar),
            ("¿b combinación lineal?", self.combinacion_lineal),
        )
        for titulo, comando in botones:
            ctk.CTkButton(acciones, text=titulo, command=comando).pack(
                side="left", fill="x", expand=True, padx=3
            )
        ctk.CTkButton(
            acciones,
            text="Limpiar",
            width=90,
            fg_color="transparent",
            border_width=1,
            command=self.limpiar,
        ).pack(side="left", padx=3)
        self.resultado = crear_resultado(self, height=260)

    def actualizar_entradas(self):
        """Valida n,k y crea k vectores, además del vector objetivo b."""
        try:
            n = leer_entero(self.entry_n, "La dimensión n")
            k = leer_entero(self.entry_k, "La cantidad de vectores k")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.tabla.winfo_children():
            widget.destroy()
        self.vectores_entries = [[] for _ in range(k)]
        self.b_entries = []
        for j in range(k):
            ctk.CTkLabel(self.tabla, text=f"v{j + 1}").grid(row=0, column=j + 1, padx=4)
        ctk.CTkLabel(self.tabla, text="b (objetivo)").grid(row=0, column=k + 1, padx=8)
        for i in range(n):
            ctk.CTkLabel(self.tabla, text=f"Componente {i + 1}").grid(
                row=i + 1, column=0, sticky="w", padx=5
            )
            for j in range(k):
                celda = entrada_numero(self.tabla)
                celda.grid(row=i + 1, column=j + 1, padx=3, pady=3)
                self.vectores_entries[j].append(celda)
            objetivo = entrada_numero(self.tabla)
            objetivo.grid(row=i + 1, column=k + 1, padx=8, pady=3)
            self.b_entries.append(objetivo)
        reemplazar_texto(self.resultado, "")

    def leer_vectores(self):
        """Convierte las entradas a vectores exactos, equivalentes a elementos de R^n."""
        vectores = []
        for indice, fila in enumerate(self.vectores_entries):
            try:
                vectores.append([
                    leer_fraccion(celda, f"v{indice + 1}") for celda in fila
                ])
            except ValueError as error:
                raise ValueError(f"Entrada inválida en v{indice + 1}: {error}") from error
        return vectores

    def sumar(self):
        """Calcula v1+v2 sumando coordenadas homólogas y explica cada suma."""
        try:
            vectores = self.leer_vectores()
            if len(vectores) < 2:
                raise ValueError("Se requieren por lo menos dos vectores.")
            resultado = suma_vectores(vectores[0], vectores[1])
            pasos = [
                f"Componente {i + 1}: {formatear_valor(vectores[0][i])} + "
                f"{formatear_valor(vectores[1][i])} = {formatear_valor(resultado[i])}"
                for i in range(len(resultado))
            ]
            reemplazar_texto(
                self.resultado,
                "SUMA DE VECTORES\n"
                f"v1 = {formatear_vector(vectores[0])}\n"
                f"v2 = {formatear_vector(vectores[1])}\n"
                "Se suman coordenadas de la misma posición:\n"
                + "\n".join(pasos)
                + f"\nResultado: v1+v2 = {formatear_vector(resultado)}\n",
            )
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Error", str(error))

    def restar(self):
        """Calcula v1-v2 restando coordenadas homólogas."""
        try:
            vectores = self.leer_vectores()
            if len(vectores) < 2:
                raise ValueError("Se requieren por lo menos dos vectores.")
            resultado = resta_vectores(vectores[0], vectores[1])
            pasos = [
                f"Componente {i + 1}: {formatear_valor(vectores[0][i])} - "
                f"{formatear_valor(vectores[1][i])} = {formatear_valor(resultado[i])}"
                for i in range(len(resultado))
            ]
            reemplazar_texto(
                self.resultado,
                "RESTA DE VECTORES\n"
                f"v1 = {formatear_vector(vectores[0])}\n"
                f"v2 = {formatear_vector(vectores[1])}\n"
                "Se restan coordenadas de la misma posición:\n"
                + "\n".join(pasos)
                + f"\nResultado: v1-v2 = {formatear_vector(resultado)}\n",
            )
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Error", str(error))

    def escalar(self):
        """Multiplica c por cada componente de v1, equivalente a c*v1."""
        try:
            vectores = self.leer_vectores()
            escalar = leer_fraccion(self.entry_c, "El escalar")
            resultado = multiplicar_escalar_vector(escalar, vectores[0])
            pasos = [
                f"Componente {i + 1}: {formatear_valor(escalar)} * "
                f"{formatear_valor(vectores[0][i])} = {formatear_valor(resultado[i])}"
                for i in range(len(resultado))
            ]
            reemplazar_texto(
                self.resultado,
                "PRODUCTO DE UN VECTOR POR UN ESCALAR\n"
                f"c = {formatear_valor(escalar)}; v1 = {formatear_vector(vectores[0])}\n"
                "Se multiplica c por cada coordenada:\n"
                + "\n".join(pasos)
                + f"\nResultado: c*v1 = {formatear_vector(resultado)}\n",
            )
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Error", str(error))

    def combinacion_lineal(self):
        """Resuelve V*c=b y decide si b está en el span de los vectores ingresados."""
        try:
            vectores = self.leer_vectores()
            objetivo = [
                leer_fraccion(celda, "El vector objetivo b") for celda in self.b_entries
            ]
            aumentada = es_combinacion_lineal(objetivo, vectores)
            calculo = resolver_sistema(aumentada, metodo="gauss-jordan")
            clasificacion = clasificar_sistema(
                calculo["matriz_escalonada"], calculo["rango"]
            )
            lineas = [
                "COMBINACIÓN LINEAL",
                "Se buscan escalares c1,...,ck tales que c1*v1+...+ck*vk=b.",
                f"b = {formatear_vector(objetivo)}",
                "Matriz aumentada [V|b]:",
                formatear_matriz(aumentada),
                "Reducción por filas:",
            ]
            for indice, paso in enumerate(calculo["pasos"], 1):
                lineas.extend([
                    f"  Paso {indice}: {paso['descripcion']}",
                    formatear_matriz(paso["matriz"]),
                ])
            if clasificacion["tipo"] == "Inconsistente":
                lineas.extend([
                    "Conclusión: b NO es combinación lineal de los vectores.",
                    clasificacion["descripcion"],
                ])
            else:
                lineas.append("Conclusión: b SÍ es combinación lineal.")
                for indice, vector in enumerate(vectores):
                    expresion = calculo["soluciones_generales"].get(indice)
                    if expresion and not expresion[1]:
                        lineas.append(
                            f"  c{indice + 1} = {formatear_valor(expresion[0])}"
                        )
                    elif indice in calculo["variables_libres"]:
                        lineas.append(f"  c{indice + 1} es libre.")
                if calculo["variables_libres"]:
                    lineas.append("Existen infinitas representaciones de b.")
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n")
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Error", str(error))

    def limpiar(self):
        """Reinicia los vectores, b, el escalar y el área de resultados."""
        for fila in self.vectores_entries:
            for celda in fila:
                celda.delete(0, "end")
                celda.insert(0, "0")
        for celda in self.b_entries:
            celda.delete(0, "end")
            celda.insert(0, "0")
        self.entry_c.delete(0, "end")
        self.entry_c.insert(0, "0")
        reemplazar_texto(self.resultado, "Entradas reiniciadas a cero.\n")
