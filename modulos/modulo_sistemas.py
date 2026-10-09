"""Ventana independiente para resolver sistemas de ecuaciones lineales."""

import customtkinter as ctk

from backend.clasificador import clasificar_sistema, columnas_pivote
from backend.eliminacion import resolver_sistema
from backend.matriz import formatear_valor, subindice
from backend.matrices import invertir_gauss_jordan, resolver_cramer
from backend.operaciones_matriciales import multiplicar_matriz_vector
from modulos._comun import (
    Selector,
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    entrada_numero,
    etiqueta,
    formatear_expresion,
    formatear_matriz,
    formatear_vector,
    leer_entero,
    leer_fraccion,
    mensaje_error,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
)


def _resolver_por_matriz_inversa(matriz_a, vector_b):
    """Resuelve x=A⁻¹b y devuelve inversa, pasos y verificación exacta."""
    if not matriz_a or any(len(fila) != len(matriz_a) for fila in matriz_a):
        raise ValueError(
            "El método de matriz inversa requiere que A sea cuadrada."
        )
    if vector_b is None or len(vector_b) != len(matriz_a):
        raise ValueError(
            "El vector b debe tener una entrada por cada fila de la matriz cuadrada A."
        )
    inversa, pasos = invertir_gauss_jordan(matriz_a)
    solucion = multiplicar_matriz_vector(inversa, vector_b)
    producto_ax = multiplicar_matriz_vector(matriz_a, solucion)
    return inversa, pasos, solucion, producto_ax


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
            descripcion="Resuelve Ax = b por Gauss, Gauss-Jordan, Cramer o matriz inversa.",
            logo=(
                "[ [1 2 | 3] ]  MÓDULO: SISTEMAS DE ECUACIONES (SEL)\n"
                "[ [0 1 | 5] ]  Métodos: Gauss, Gauss-Jordan, Cramer, A⁻¹b"
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
        self.metodo = Selector(
            contenido,
            ["Gauss-Jordan", "Gauss", "Cramer", "Matriz inversa"],
        )
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
            if metodo == "cramer":
                if m != n:
                    raise ValueError(
                        "La regla de Cramer requiere un sistema cuadrado: "
                        "el número de ecuaciones debe igualar al de variables."
                    )
                self._mostrar_cramer(matriz_a, vector_b)
                return
            if metodo == "matriz inversa":
                if m != n:
                    raise ValueError(
                        "El método de matriz inversa requiere un sistema cuadrado: "
                        "el número de ecuaciones debe igualar al de variables."
                    )
                self._mostrar_inversa(matriz_a, vector_b)
                return
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
                            f"  x{subindice(variable + 1)} = {formatear_expresion(constante, terminos)}"
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

    def _mostrar_inversa(self, matriz_a, vector_b):
        """Muestra x=A⁻¹b, los pasos de inversión y la comprobación Ax=b."""
        inversa, pasos, solucion, producto_ax = _resolver_por_matriz_inversa(
            matriz_a, vector_b
        )
        lineas = [
            "MODULO 1 | RESOLUCIÓN POR MATRIZ INVERSA",
            "=" * 58,
            "Matriz A:",
            formatear_matriz(matriz_a),
            "\nCálculo de A⁻¹ por Gauss-Jordan:",
        ]
        for indice, (descripcion, estado) in enumerate(pasos, 1):
            lineas.extend([f"Paso {indice}: {descripcion}", formatear_matriz(estado)])
        lineas.extend([
            "\nInversa final A⁻¹:",
            formatear_matriz(inversa),
            "\nVector b:",
            formatear_vector(vector_b),
            "\nProducto x = A⁻¹b:",
        ])
        for i, fila in enumerate(inversa):
            terminos = " + ".join(
                f"({formatear_valor(fila[j])})({formatear_valor(vector_b[j])})"
                for j in range(len(vector_b))
            )
            lineas.append(
                f"x{subindice(i + 1)} = {terminos} = "
                f"{formatear_valor(solucion[i])}"
            )
        lineas.extend([
            "Solución x = (" + ", ".join(formatear_valor(v) for v in solucion) + ")",
            "\nVerificación exacta de Ax = b:",
            "Ax = (" + ", ".join(formatear_valor(v) for v in producto_ax) + ")",
        ])
        cumple = producto_ax == vector_b
        for i, fila in enumerate(matriz_a):
            terminos = " + ".join(
                f"({formatear_valor(fila[j])})({formatear_valor(solucion[j])})"
                for j in range(len(solucion))
            )
            lineas.append(
                f"Ecuación {i + 1}: {terminos} = {formatear_valor(producto_ax[i])} "
                f"{'=' if producto_ax[i] == vector_b[i] else '≠'} "
                f"{formatear_valor(vector_b[i])}"
            )
        lineas.append("Ax = b: " + ("Se cumple" if cumple else "No se cumple"))
        reemplazar_texto(
            self.resultado,
            "\n".join(lineas) + "\n",
            "Solución por matriz inversa: ("
            + ", ".join(formatear_valor(v) for v in solucion) + ")",
        )

    def _mostrar_cramer(self, matriz_a, vector_b):
        """Presenta D, cada determinante Dᵢ y la solución por Cramer."""
        datos = resolver_cramer(matriz_a, vector_b)
        lineas = [
            "MODULO 1 | REGLA DE CRAMER PARA Ax=b",
            "=" * 58,
            "Paso 1: calcular D = det(A).",
            "Matriz A:",
            formatear_matriz(matriz_a),
            "Vector b = (" + ", ".join(formatear_valor(valor) for valor in vector_b) + ")",
            "Cálculo de D:",
        ]
        for descripcion, estado in datos["pasos_determinante"]:
            lineas.extend([descripcion, formatear_matriz(estado)])
        determinante = datos["determinante"]
        lineas.append(f"D = {formatear_valor(determinante)}")
        if datos["solucion"] is None:
            lineas.extend([
                "",
                "D = 0: la regla de Cramer no permite obtener una solución única.",
                "El sistema puede no tener solución o tener infinitas soluciones.",
            ])
            reemplazar_texto(
                self.resultado,
                "\n".join(lineas) + "\n",
                "D = 0: Cramer no determina una solución única.",
            )
            return

        valores_x = []
        for reemplazo in datos["reemplazos"]:
            indice = reemplazo["indice"]
            determinante_i = reemplazo["determinante"]
            valor = reemplazo["valor"]
            lineas.extend([
                "",
                f"Paso 2: construir A{subindice(indice + 1)} "
                f"(reemplazar la columna {indice + 1} de A por b):",
                formatear_matriz(reemplazo["matriz"]),
                f"Paso 3: calcular D{subindice(indice + 1)} = det(A{subindice(indice + 1)}).",
            ])
            for descripcion, estado in reemplazo["pasos_determinante"]:
                lineas.extend([descripcion, formatear_matriz(estado)])
            lineas.extend([
                f"D{subindice(indice + 1)} = {formatear_valor(determinante_i)}",
                f"Paso 4: x{subindice(indice + 1)} = "
                f"D{subindice(indice + 1)}/D = "
                f"{formatear_valor(determinante_i)}/{formatear_valor(determinante)} "
                f"= {formatear_valor(valor)}",
            ])
            valores_x.append(f"x{subindice(indice + 1)} = {formatear_valor(valor)}")
        lineas.extend([
            "",
            "Solución final: (" + ", ".join(formatear_valor(valor) for valor in datos["solucion"]) + ")",
        ])
        reemplazar_texto(
            self.resultado,
            "\n".join(lineas) + "\n",
            "Solución única por Cramer: " + ",  ".join(valores_x),
        )

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

    def limpiar(self):
        """Reinicia a cero los coeficientes y términos independientes."""
        reiniciar_celdas(self.entradas_A, self.entradas_b)
        reemplazar_texto(self.resultado, "")
