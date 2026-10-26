"""
Pantalla de operaciones con vectores y combinación lineal.

Unidad I, Vectores y ecuaciones matriciales [P3].
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import customtkinter as ctk
from fractions import Fraction

from backend.matriz import formatear_valor, subindice
from backend.vectores import (
    es_combinacion_lineal,
    multiplicar_escalar_vector,
    resta_vectores,
    suma_vectores,
)
from backend.eliminacion import resolver_sistema
from backend.clasificador import clasificar_sistema
from modulos._comun import (
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


def _texto_traza_combinacion(pasos, cantidad_variables):
    """Vincula cada operaciÃ³n de Gauss-Jordan con sus matrices registradas."""
    if not pasos:
        return []
    anterior = pasos[0]["matriz"]
    lineas = ["Estado inicial del sistema [V|b]:", formatear_matriz(anterior)]
    for indice, paso in enumerate(pasos[1:], 1):
        estado = paso["matriz"]
        descripcion = paso["descripcion"]
        lineas.extend([f"Paso {indice}: {descripcion}", "Antes:", formatear_matriz(anterior)])
        if descripcion.startswith("Intercambio F"):
            filas = descripcion.removeprefix("Intercambio F").split(" ↔ F")
            lineas.append(
                f"Se intercambian las filas completas de [V|b] para mantener un sistema equivalente "
                f"(F{filas[0]} ↔ F{filas[1]})."
            )
        elif descripcion.startswith("Normalizar F"):
            fila = int(descripcion.split("F", 1)[1].split()[0]) - 1
            columna = next(j for j in range(cantidad_variables) if anterior[fila][j] != 0)
            pivote = anterior[fila][columna]
            calculos = "; ".join(
                f"{formatear_valor(anterior[fila][j])}/{formatear_valor(pivote)}="
                f"{formatear_valor(estado[fila][j])}"
                for j in range(len(estado[fila]))
            )
            lineas.extend([
                f"El pivote de la columna {columna + 1} es {formatear_valor(pivote)}. "
                "Dividir la fila completa entre un valor no nulo conserva un sistema equivalente.",
                "Cálculos de la fila (incluido el término b): " + calculos + ".",
            ])
        elif " ← " in descripcion:
            izquierda, operacion = descripcion.split(" ← ")
            fila_objetivo = int(izquierda[1:]) - 1
            fila_pivote = int(operacion.split("·F")[1]) - 1
            columna = next(j for j in range(cantidad_variables) if anterior[fila_pivote][j] != 0)
            pivote = anterior[fila_pivote][columna]
            factor = anterior[fila_objetivo][columna] / pivote
            calculos = "; ".join(
                f"{formatear_valor(anterior[fila_objetivo][j])} - "
                f"({formatear_valor(factor)})({formatear_valor(anterior[fila_pivote][j])})="
                f"{formatear_valor(estado[fila_objetivo][j])}"
                for j in range(len(estado[fila_objetivo]))
            )
            lineas.extend([
                f"Pivote: {formatear_valor(pivote)} en la columna {columna + 1}; "
                f"se elimina la entrada de F{fila_objetivo + 1}.",
                "Restar un múltiplo de otra fila conserva las soluciones; se opera también "
                "sobre la columna aumentada b.",
                "Cálculos de la fila: " + calculos + ".",
            ])
        lineas.extend(["Después:", formatear_matriz(estado)])
        anterior = estado
    return lineas


def _texto_reconstruccion_combinacion(vectores, coeficientes, objetivo):
    """Desarrolla c₁v₁+…+cₖvₖ con operaciones exactas ya existentes."""
    lineas = ["Reconstrucción de la combinación con estos coeficientes:"]
    escalados = []
    for indice, (vector, coeficiente) in enumerate(zip(vectores, coeficientes), 1):
        escalado = multiplicar_escalar_vector(coeficiente, vector)
        escalados.append(escalado)
        etiqueta_coeficiente = f"c{subindice(indice)}"
        etiqueta_vector = f"v{subindice(indice)}"
        lineas.append(
            f"{etiqueta_coeficiente} = {formatear_valor(coeficiente)}; "
            f"{etiqueta_vector} = {formatear_vector(vector)}."
        )
        lineas.append(
            f"{etiqueta_coeficiente}·{etiqueta_vector}: " + "; ".join(
                f"componente {i + 1}: ({formatear_valor(coeficiente)})"
                f"({formatear_valor(componente)})={formatear_valor(escalado[i])}"
                for i, componente in enumerate(vector)
            ) + f"; vector escalado = {formatear_vector(escalado)}"
        )
    resultado = [sum((vector[i] for vector in escalados), Fraction(0))
                 for i in range(len(objetivo))]
    lineas.append("Suma componente por componente:")
    lineas.extend(
        f"Componente {i + 1}: " + " + ".join(
            formatear_valor(vector[i]) for vector in escalados
        ) + f" = {formatear_valor(resultado[i])} (objetivo b{i + 1} = "
        f"{formatear_valor(objetivo[i])})."
        for i in range(len(resultado))
    )
    lineas.append(f"Vector obtenido: {formatear_vector(resultado)}.")
    lineas.append(
        "La reconstrucción " + ("coincide" if resultado == objetivo else "NO coincide")
        + " con b; la igualdad verifica la representación."
    )
    return lineas


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
        zonas = crear_estructura(
            self,
            self.on_back,
            numero=2,
            titulo="Vectores y combinación lineal",
            descripcion="Suma, resta y escalar de vectores. ¿Es b combinación lineal?",
            logo=(
                " u + v   MÓDULO: OPERACIONES CON VECTORES\n"
                " c · v   Suma, resta, escalar y combinación lineal\n"
                " → R^n   c1·v1 + ... + ck·vk = b"
            ),
            pasos=[
                "Escribe cuántos componentes tiene cada vector, cuántos vectores "
                "vas a usar y pulsa «Crear tabla».",
                "Cada columna es un vector. Para sumar, restar o multiplicar por c "
                "se usan v₁ y v₂.",
                "Para saber si b es combinación lineal de los vectores, llena "
                "también la columna b y pulsa «¿b es combinación lineal?».",
            ],
            clave_teoremas="operaciones_vectores",
            indicacion="Aquí verás cada operación componente por componente, o el "
                       "sistema que decide si b es combinación lineal.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido

        controles, entradas = crear_controles(
            contenido,
            [("n", "Componentes", "3", 90), ("k", "Vectores", "2", 80),
             ("c", "Escalar c", "2", 80, False)],
            self.actualizar_entradas,
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_n, self.entry_k = entradas["n"], entradas["k"]
        self.entry_c = entradas["c"]

        subtitulo(contenido, "Tus vectores").pack(anchor="w", padx=10, pady=(20, 6))
        self.tabla = ctk.CTkFrame(contenido, fg_color="transparent")
        self.tabla.pack(anchor="w", padx=6)

        acciones = zonas.acciones
        acciones.grid_columnconfigure((0, 1, 2), weight=1, uniform="ops")
        for columna, (titulo, comando) in enumerate((
            ("v₁ + v₂", self.sumar),
            ("v₁ − v₂", self.restar),
            ("c · v₁", self.escalar),
        )):
            boton_secundario(acciones, titulo, comando, height=38).grid(
                row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 8, 0)
            )
        boton_primario(
            acciones, "¿b es combinación lineal?", self.combinacion_lineal
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        boton_secundario(acciones, "Limpiar", self.limpiar, height=40).grid(
            row=1, column=2, sticky="ew", padx=(8, 0), pady=(8, 0)
        )

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
            etiqueta(self.tabla, f"v{subindice(j + 1)}", color="texto", negrita=True).grid(
                row=0, column=j, pady=(0, 2)
            )
        etiqueta(self.tabla, "b", color="texto", negrita=True).grid(
            row=0, column=k, padx=(18, 0), pady=(0, 2)
        )
        for i in range(n):
            for j in range(k):
                celda = entrada_numero(self.tabla)
                celda.grid(row=i + 1, column=j, padx=3, pady=3)
                self.vectores_entries[j].append(celda)
            objetivo = entrada_numero(self.tabla)
            objetivo.grid(row=i + 1, column=k, padx=(18, 3), pady=3)
            self.b_entries.append(objetivo)
        reemplazar_texto(self.resultado, "")

    def leer_vectores(self):
        """Convierte las entradas a vectores exactos, equivalentes a elementos de R^n."""
        vectores = []
        for indice, fila in enumerate(self.vectores_entries):
            try:
                vectores.append([
                    leer_fraccion(celda, f"v{subindice(indice + 1)}") for celda in fila
                ])
            except ValueError as error:
                raise ValueError(f"Entrada inválida en v{subindice(indice + 1)}: {error}") from error
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
                f"v₁ = {formatear_vector(vectores[0])}\n"
                f"v₂ = {formatear_vector(vectores[1])}\n"
                "Se suman coordenadas de la misma posición:\n"
                + "\n".join(pasos)
                + f"\nResultado: v₁ + v₂ = {formatear_vector(resultado)}\n",
                f"v₁ + v₂ = {formatear_vector(resultado)}",
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

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
                f"v₁ = {formatear_vector(vectores[0])}\n"
                f"v₂ = {formatear_vector(vectores[1])}\n"
                "Se restan coordenadas de la misma posición:\n"
                + "\n".join(pasos)
                + f"\nResultado: v₁ − v₂ = {formatear_vector(resultado)}\n",
                f"v₁ − v₂ = {formatear_vector(resultado)}",
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

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
                f"c = {formatear_valor(escalar)}; v₁ = {formatear_vector(vectores[0])}\n"
                "Se multiplica c por cada coordenada:\n"
                + "\n".join(pasos)
                + f"\nResultado: c·v₁ = {formatear_vector(resultado)}\n",
                f"{formatear_valor(escalar)} · v₁ = {formatear_vector(resultado)}",
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

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
                f"Se buscan coeficientes para expresar b en R^{len(objetivo)} "
                f"como c₁·v₁ + … + cₖ·vₖ, usando k={len(vectores)} vectores:",
                *[
                    f"v{subindice(j + 1)} = {formatear_vector(vector)} "
                    f"(dimensión {len(vector)})."
                    for j, vector in enumerate(vectores)
                ],
                f"b = {formatear_vector(objetivo)}",
                "Matriz aumentada [V|b]:",
                formatear_matriz(aumentada),
                "El sistema Vc=b decide si b pertenece al espacio generado por estos vectores; "
                "aquí se buscan sus coeficientes.",
                "Reducción por filas de [V|b]:",
            ]
            lineas.extend(_texto_traza_combinacion(calculo["pasos"], len(vectores)))
            if clasificacion["tipo"] == "Inconsistente":
                lineas.extend([
                    "Conclusión: b NO es combinación lineal de los vectores.",
                    clasificacion["descripcion"],
                ])
            else:
                # Cada escalar cⱼ es una constante o, si hay variables libres,
                # una expresión en términos de los parámetros tⱼ.
                libres = calculo["variables_libres"]
                coeficientes = []
                for indice in range(len(vectores)):
                    nombre = f"c{subindice(indice + 1)}"
                    if indice in libres:
                        coeficientes.append(f"{nombre} = t{subindice(indice + 1)}")
                    else:
                        constante, terminos = calculo["soluciones_generales"][indice]
                        coeficientes.append(f"{nombre} = {formatear_expresion(constante, terminos)}")
                lineas.append("Conclusión: b SÍ es combinación lineal.")
                lineas.extend(
                    "  " + texto + ("  (libre, cualquier valor)" if j in libres else "")
                    for j, texto in enumerate(coeficientes)
                )
                if libres:
                    coeficientes_ejemplo = [
                        calculo["soluciones_generales"][j][0]
                        for j in range(len(vectores))
                    ]
                    lineas.extend([
                        "Existen infinitas representaciones de b: cada valor de "
                        + ", ".join(f"t{subindice(j + 1)}" for j in libres)
                        + " da una distinta.",
                        "Para obtener una representación concreta, se fija cada parámetro libre en 0.",
                        *_texto_reconstruccion_combinacion(
                            vectores, coeficientes_ejemplo, objetivo
                        ),
                    ])
                else:
                    coeficientes_unicos = [
                        calculo["soluciones"][j] for j in range(len(vectores))
                    ]
                    lineas.extend(_texto_reconstruccion_combinacion(
                        vectores, coeficientes_unicos, objetivo
                    ))
            if clasificacion["tipo"] == "Inconsistente":
                resumen = "b NO es combinación lineal de los vectores."
            elif calculo["variables_libres"]:
                resumen = "b SÍ es combinación lineal (infinitas formas):   " + ",   ".join(
                    coeficientes
                )
            else:
                resumen = "b SÍ es combinación lineal:   " + ",   ".join(coeficientes)
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n", resumen)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        """Reinicia los vectores, b, el escalar y el área de resultados."""
        reiniciar_celdas(self.vectores_entries, self.b_entries, [self.entry_c])
        reemplazar_texto(self.resultado, "")
