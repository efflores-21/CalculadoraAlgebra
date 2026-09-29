"""Ventana independiente para resolver sistemas de ecuaciones lineales."""

import customtkinter as ctk
from tkinter import messagebox

from backend.clasificador import clasificar_sistema, columnas_pivote
from backend.eliminacion import resolver_sistema
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


class ModuloSistemas(ctk.CTkFrame):
    """Presenta un panel propio para el sistema matricial A*x=b."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A = []
        self.entradas_b = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Construye campos, controles y resultados propios del módulo."""
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
            "[ [1 2 | 3] ]  MODULO 1: SISTEMAS DE ECUACIONES (SEL)\n"
            "[ [0 1 | 5] ]  Metodos: Gauss y Gauss-Jordan\n"
            "Sistema matricial A*x=b",
        )
        controles = ctk.CTkFrame(self)
        controles.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(controles, text="Ecuaciones m:").grid(row=0, column=0, padx=5, pady=8)
        self.entry_m = ctk.CTkEntry(controles, width=60, justify="center")
        self.entry_m.insert(0, "2")
        self.entry_m.grid(row=0, column=1, padx=5)
        ctk.CTkLabel(controles, text="Variables n:").grid(row=0, column=2, padx=5)
        self.entry_n = ctk.CTkEntry(controles, width=60, justify="center")
        self.entry_n.insert(0, "2")
        self.entry_n.grid(row=0, column=3, padx=5)
        ctk.CTkButton(
            controles, text="Aplicar dimensiones", command=self.actualizar_entradas
        ).grid(row=0, column=4, padx=5)
        self.metodo = ctk.CTkOptionMenu(
            controles, values=["Gauss-Jordan", "Gauss"], width=140
        )
        self.metodo.set("Gauss-Jordan")
        self.metodo.grid(row=0, column=5, padx=5)
        ctk.CTkButton(
            controles,
            text="0. Ver Teoremas Clave del Módulo",
            command=lambda: mostrar_teoremas(self, "sistemas", "Sistemas"),
        ).grid(row=0, column=6, padx=5)

        self.tabla = ctk.CTkScrollableFrame(self, label_text="Coeficientes A y términos independientes b")
        self.tabla.pack(fill="both", expand=True, padx=12, pady=6)
        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(fill="x", padx=12, pady=4)
        ctk.CTkButton(
            acciones, text="Resolver sistema", command=self.resolver, height=38
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(
            acciones,
            text="Limpiar",
            width=110,
            fg_color="transparent",
            border_width=1,
            command=self.limpiar,
        ).pack(side="left", padx=(5, 0))
        self.resultado = crear_resultado(self, 260)

    def actualizar_entradas(self):
        """Valida m,n y construye las entradas que representan A y b."""
        try:
            m = leer_entero(self.entry_m, "El número de ecuaciones m")
            n = leer_entero(self.entry_n, "El número de variables n")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.tabla.winfo_children():
            widget.destroy()
        self.entradas_A = []
        self.entradas_b = []
        for j in range(n):
            ctk.CTkLabel(self.tabla, text=f"x{j + 1}").grid(row=0, column=j, padx=3)
        ctk.CTkLabel(self.tabla, text="| b").grid(row=0, column=n, padx=8)
        for i in range(m):
            fila = []
            for j in range(n):
                entry = entrada_numero(self.tabla)
                entry.grid(row=i + 1, column=j, padx=3, pady=3)
                fila.append(entry)
            entry_b = entrada_numero(self.tabla)
            entry_b.grid(row=i + 1, column=n, padx=8, pady=3)
            self.entradas_A.append(fila)
            self.entradas_b.append(entry_b)

    def resolver(self):
        """Resuelve A*x=b y muestra las operaciones de fila y clasificación."""
        try:
            m = leer_entero(self.entry_m, "El número de ecuaciones m")
            n = leer_entero(self.entry_n, "El número de variables n")
            matriz_a = [
                [_a_fraction(celda.get().strip() or "0") for celda in fila]
                for fila in self.entradas_A
            ]
            vector_b = [
                _a_fraction(celda.get().strip() or "0") for celda in self.entradas_b
            ]
            matriz_aumentada = [
                matriz_a[i][:] + [vector_b[i]] for i in range(m)
            ]
            metodo = self.metodo.get().lower()
            datos = resolver_sistema(matriz_aumentada, metodo=metodo)
            clase = clasificar_sistema(datos["matriz_escalonada"], datos["rango"])

            lineas = [
                "MODULO 1 | RESOLUCION DE Ax=b",
                "=" * 58,
                f"A es {m}x{n}; x tiene {n} variables; b tiene {m} entradas.",
                "Matriz aumentada inicial [A|b]:",
                formatear_matriz(matriz_aumentada),
                "",
                "PASOS DE ELIMINACION:",
            ]
            for i, paso in enumerate(datos["pasos"], 1):
                lineas.extend([
                    f"Paso {i}: {paso['descripcion']}",
                    formatear_matriz(paso["matriz"]),
                ])
            nombre_final = (
                "forma escalonada reducida (RREF)"
                if metodo == "gauss-jordan" else "forma escalonada"
            )
            lineas.extend([
                "",
                f"Matriz final en {nombre_final}:",
                formatear_matriz(datos["matriz_escalonada"]),
            ])

            # Una columna es pivote si contiene el primer valor no nulo de
            # alguna fila; sus variables son básicas y las demás son libres.
            pivotes = columnas_pivote(datos["matriz_escalonada"], datos["rango"])
            libres = [j for j in range(n) if j not in pivotes]
            lineas.extend([
                "",
                "COLUMNAS PIVOTE Y VARIABLES:",
                "  Columnas pivote: "
                + (", ".join(f"columna {j + 1}" for j in pivotes) or "ninguna"),
            ])
            if clase["tipo"] == "Inconsistente":
                lineas.append(
                    "  Variables básicas y libres: no aplica, porque el sistema no tiene solución."
                )
            else:
                lineas.extend([
                    "  Variables básicas: "
                    + (", ".join(f"x{j + 1}" for j in pivotes) or "ninguna"),
                    "  Variables libres: "
                    + (", ".join(f"x{j + 1}" for j in libres) or "ninguna"),
                ])

            lineas.extend([
                "",
                f"Clasificacion: {clase['tipo']}.",
                clase["descripcion"],
            ])
            if clase["tipo"] != "Inconsistente":
                lineas.append("Solución:")
                expresiones = datos["soluciones_generales"]
                for variable in range(n):
                    constante, terminos = expresiones.get((variable), (None, None))
                    if variable in libres:
                        lineas.append(
                            f"  x{variable + 1} = t{variable + 1} (variable libre, cualquier valor)"
                        )
                    elif constante is not None:
                        lineas.append(
                            f"  x{variable + 1} = {self._formatear_expresion(constante, terminos)}"
                        )
                    else:
                        valor = datos["soluciones"].get(variable)
                        lineas.append(
                            f"  x{variable + 1} = {formatear_valor(valor)}"
                        )
                lineas.extend(
                    self._verificar_solucion(matriz_a, vector_b, expresiones, libres)
                )
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n")
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Error", str(error))

    def _verificar_solucion(self, matriz_a, vector_b, expresiones, libres):
        """
        Sustituye la solución en cada ecuación original y compara con b.

        Equivale a comprobar A*x = b fila por fila: la ecuación i se cumple si
        a_i1*x1 + ... + a_in*xn da exactamente b_i. Con variables libres se
        verifica la solución particular que resulta de tomar todos los t = 0.
        """
        n = len(matriz_a[0])
        x = [expresiones[j][0] for j in range(n)]
        lineas = ["", "VERIFICACIÓN (sustitución en el sistema original):"]
        if libres:
            lineas.append(
                "  Se usa la solución particular con "
                + ", ".join(f"t{j + 1}" for j in libres) + " = 0:"
            )
        lineas.append(
            "  x = (" + ", ".join(formatear_valor(valor) for valor in x) + ")"
        )
        todas_cumplen = True
        for i, fila in enumerate(matriz_a):
            productos = " + ".join(
                f"({formatear_valor(fila[j])})({formatear_valor(x[j])})"
                for j in range(n)
            )
            total = sum(fila[j] * x[j] for j in range(n))
            cumple = total == vector_b[i]
            todas_cumplen = todas_cumplen and cumple
            lineas.append(
                f"  Ec. {i + 1}: {productos} = {formatear_valor(total)}"
                f"  {'=' if cumple else '≠'} {formatear_valor(vector_b[i])}"
                f"  {'✓' if cumple else '✗'}"
            )
        lineas.append(
            "  Resultado: la solución satisface todas las ecuaciones."
            if todas_cumplen
            else "  Resultado: la solución NO satisface todas las ecuaciones."
        )
        return lineas

    def _formatear_expresion(self, constante, terminos):
        """Escribe una solución afín, equivalente a expresar variables con parámetros libres."""
        texto = formatear_valor(constante)
        for libre, coeficiente in sorted(terminos.items()):
            signo = "+" if coeficiente >= 0 else "-"
            magnitud = abs(coeficiente)
            factor = "" if magnitud == 1 else formatear_valor(magnitud) + "*"
            texto += f" {signo} {factor}t{libre + 1}"
        return texto

    def limpiar(self):
        """Reinicia a cero los coeficientes y términos independientes."""
        for fila in self.entradas_A:
            for entry in fila:
                entry.delete(0, "end")
                entry.insert(0, "0")
        for entry in self.entradas_b:
            entry.delete(0, "end")
            entry.insert(0, "0")
        reemplazar_texto(self.resultado, "Entradas reiniciadas a cero.\n")
