"""Ventana independiente para resolver sistemas de ecuaciones lineales."""

import customtkinter as ctk

from backend.clasificador import clasificar_sistema, columnas_pivote
from backend.eliminacion import resolver_sistema
from backend.matriz import formatear_valor, subindice
from modulos._comun import (
    Selector,
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    entrada_numero,
    etiqueta,
    formatear_matriz,
    leer_entero,
    leer_fraccion,
    mensaje_error,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
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
        zonas = crear_estructura(
            self,
            self.on_back,
            numero=1,
            titulo="Sistemas de ecuaciones",
            descripcion="Resuelve Ax = b por Gauss o Gauss-Jordan, paso a paso.",
            logo=(
                "[ [1 2 | 3] ]  MÓDULO: SISTEMAS DE ECUACIONES (SEL)\n"
                "[ [0 1 | 5] ]  Métodos: Gauss, Gauss-Jordan"
            ),
            pasos=[
                "Escribe cuántas ecuaciones y cuántas variables tiene tu sistema "
                "y pulsa «Crear tabla».",
                "Cada fila es una ecuación: escribe los coeficientes de x₁, x₂, … "
                "y en la columna «= b» el número que va después del igual.",
                "Elige el método y pulsa «Resolver».",
            ],
            nota="Ejemplo: 2x₁ + x₂ = 5 se escribe 2 | 1 | 5.  "
                 "Acepta enteros, decimales y fracciones (1/3).",
            clave_teoremas="sistemas",
            indicacion="Aquí verás la matriz aumentada, cada operación entre filas, "
                       "las columnas pivote, la solución y su verificación.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido

        controles, entradas = crear_controles(
            contenido,
            [("m", "Ecuaciones", "2", 90), ("n", "Variables", "2", 90)],
            self.actualizar_entradas,
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_m, self.entry_n = entradas["m"], entradas["n"]

        etiqueta(contenido, "Método").pack(anchor="w", padx=10, pady=(16, 2))
        self.metodo = Selector(contenido, ["Gauss-Jordan", "Gauss"])
        self.metodo.pack(anchor="w", padx=10)

        subtitulo(contenido, "Tu sistema").pack(anchor="w", padx=10, pady=(20, 6))
        self.tabla = ctk.CTkFrame(contenido, fg_color="transparent")
        self.tabla.pack(anchor="w", padx=6)

        boton_primario(zonas.acciones, "Resolver", self.resolver).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(
            side="left"
        )

    def actualizar_entradas(self):
        """Valida m,n y construye las entradas que representan A y b."""
        try:
            m = leer_entero(self.entry_m, "El número de ecuaciones")
            n = leer_entero(self.entry_n, "El número de variables")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.tabla.winfo_children():
            widget.destroy()
        self.entradas_A = []
        self.entradas_b = []
        for j in range(n):
            etiqueta(self.tabla, f"x{subindice(j + 1)}", tamano=15).grid(
                row=0, column=j, pady=(0, 2)
            )
        etiqueta(self.tabla, "= b", color="texto", negrita=True).grid(
            row=0, column=n, padx=(18, 0), pady=(0, 2)
        )
        for i in range(m):
            fila = []
            for j in range(n):
                entry = entrada_numero(self.tabla)
                entry.grid(row=i + 1, column=j, padx=3, pady=3)
                fila.append(entry)
            entry_b = entrada_numero(self.tabla)
            entry_b.grid(row=i + 1, column=n, padx=(18, 3), pady=3)
            self.entradas_A.append(fila)
            self.entradas_b.append(entry_b)
        reemplazar_texto(self.resultado, "")

    def resolver(self):
        """Resuelve A*x=b y muestra las operaciones de fila y clasificación."""
        try:
            # Se usa el tamaño de la tabla visible, aunque los campos cambien.
            m = len(self.entradas_A)
            n = len(self.entradas_A[0])
            matriz_a = [
                [
                    leer_fraccion(celda, f"El coeficiente de x{subindice(j + 1)} en la ecuación {i + 1}")
                    for j, celda in enumerate(fila)
                ]
                for i, fila in enumerate(self.entradas_A)
            ]
            vector_b = [
                leer_fraccion(celda, f"El valor b de la ecuación {i + 1}")
                for i, celda in enumerate(self.entradas_b)
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
                    + (", ".join(f"x{subindice(j + 1)}" for j in pivotes) or "ninguna"),
                    "  Variables libres: "
                    + (", ".join(f"x{subindice(j + 1)}" for j in libres) or "ninguna"),
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
                            f"  x{subindice(variable + 1)} = t{subindice(variable + 1)} (variable libre, cualquier valor)"
                        )
                    elif constante is not None:
                        lineas.append(
                            f"  x{subindice(variable + 1)} = {self._formatear_expresion(constante, terminos)}"
                        )
                    else:
                        valor = datos["soluciones"].get(variable)
                        lineas.append(
                            f"  x{subindice(variable + 1)} = {formatear_valor(valor)}"
                        )
                lineas.extend(
                    self._verificar_solucion(matriz_a, vector_b, expresiones, libres)
                )
            if clase["tipo"] == "Inconsistente":
                resumen = "Sin solución: el sistema es inconsistente."
            elif libres:
                resumen = (
                    "Infinitas soluciones  ·  variables libres: "
                    + ", ".join(f"x{subindice(j + 1)}" for j in libres)
                )
            else:
                resumen = "Solución única:   " + ",   ".join(
                    f"x{subindice(j + 1)} = {formatear_valor(expresiones[j][0])}" for j in range(n)
                )
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n", resumen)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

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
                + ", ".join(f"t{subindice(j + 1)}" for j in libres) + " = 0:"
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
            texto += f" {signo} {factor}t{subindice(libre + 1)}"
        return texto

    def limpiar(self):
        """Reinicia a cero los coeficientes y términos independientes."""
        reiniciar_celdas(self.entradas_A, self.entradas_b)
        reemplazar_texto(self.resultado, "")
