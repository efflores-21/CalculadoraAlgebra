"""
Pantalla del módulo de sistemas de ecuaciones (Gauss y Gauss-Jordan).

Unidad I, Sistemas de ecuaciones lineales [P1 · P2].
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

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


def _explicar_pasos_determinante(pasos, nombre):
    """Presenta los estados del determinante y calcula solo las sustituciones visibles."""
    if not pasos:
        return []
    descripcion_inicial, estado = pasos[0]
    lineas = [f"{nombre}: {descripcion_inicial}", formatear_matriz(estado)]
    estado_anterior = estado
    for descripcion, estado in pasos[1:]:
        if descripcion.startswith("Intercambiar F"):
            lineas.extend([
                descripcion,
                "Antes del intercambio:",
                formatear_matriz(estado_anterior),
                "Intercambiar dos filas cambia el signo del determinante; "
                "el algoritmo acumula ese cambio.",
                "Después del intercambio:",
                formatear_matriz(estado),
            ])
        elif descripcion.startswith("Pivote "):
            columna = int(descripcion.split()[1].rstrip(":")) - 1
            pivote = estado[columna][columna]
            lineas.extend([
                f"Pivote de la columna {columna + 1}: {formatear_valor(pivote)}.",
                formatear_matriz(estado),
            ])
        elif " <- " in descripcion:
            destino = descripcion.split(" <- ", 1)[0]
            fila_destino = int(destino.removeprefix("F")) - 1
            lado_derecho = descripcion.split(" <- ", 1)[1]
            fila_pivote = int(lado_derecho.rsplit("F", 1)[1].rstrip(".")) - 1
            columna_pivote = fila_pivote
            pivote = estado_anterior[fila_pivote][columna_pivote]
            factor = estado_anterior[fila_destino][columna_pivote] / pivote
            lineas.extend([
                f"Operación por filas: {descripcion}",
                "Antes de la operación:",
                formatear_matriz(estado_anterior),
                "Sumar un múltiplo de otra fila conserva el determinante. "
                "Se sustituye cada entrada modificada de la fila:",
            ])
            for columna in range(columna_pivote, len(estado[fila_destino])):
                antes = estado_anterior[fila_destino][columna]
                base = estado_anterior[fila_pivote][columna]
                despues = estado[fila_destino][columna]
                if antes != despues:
                    lineas.append(
                        f"  Entrada ({fila_destino + 1},{columna + 1}): "
                        f"{formatear_valor(antes)} - "
                        f"({formatear_valor(factor)})({formatear_valor(base)}) "
                        f"= {formatear_valor(despues)}"
                    )
            lineas.extend(["Después de la operación:", formatear_matriz(estado)])
        else:
            lineas.extend([descripcion, formatear_matriz(estado)])
        estado_anterior = estado
    return lineas


def _texto_pasos_gauss(pasos, matriz_final, n_variables):
    """Explica operaciones de Gauss con cálculos de fila y una sola matriz final."""
    estado_anterior = pasos[0]["matriz"]
    lineas = ["PASOS DE ELIMINACIÓN DE GAUSS:"]
    eliminadas = set()
    pivotes_explicados = set()
    for indice_paso, paso in enumerate(pasos[1:], 1):
        descripcion, estado = paso["descripcion"], paso["matriz"]
        if descripcion.startswith("Intercambio F"):
            izquierda, derecha = descripcion.removeprefix("Intercambio F").split(" ↔ F")
            fila_activa, fila_candidata = int(izquierda) - 1, int(derecha) - 1
            columna = next((j for j in range(n_variables) if estado[fila_activa][j] != 0), 0)
            lineas.extend([
                f"Paso {indice_paso}: selección e intercambio de pivote.",
                f"Objetivo: colocar en la fila activa el candidato de mayor valor absoluto en la columna {columna + 1}.",
                "Fundamento: el pivoteo parcial reduce el tamaño de los multiplicadores y evita dividir por cero.",
                "Candidatos en la columna: " + ", ".join(formatear_valor(estado_anterior[i][columna])
                    for i in range(fila_activa, len(estado))) + ".",
                f"Operación: F{fila_activa + 1} ↔ F{fila_candidata + 1}; se intercambian las filas completas de [A|b].",
            ])
        elif descripcion.startswith("Normalizar F"):
            fila = int(descripcion.split("F", 1)[1].split()[0]) - 1
            columna = next(j for j in range(n_variables) if estado_anterior[fila][j] != 0)
            pivote = estado_anterior[fila][columna]
            pivotes_explicados.add(columna)
            lineas.extend([
                f"Paso {indice_paso}: normalizar el pivote de la fila {fila + 1}, columna {columna + 1}.",
                f"Objetivo: convertir el pivote {formatear_valor(pivote)} en 1 para facilitar la sustitución.",
                "Fundamento: dividir una fila completa por un escalar no nulo conserva las soluciones.",
                f"Cálculo: F{fila + 1} ← F{fila + 1} / ({formatear_valor(pivote)}); fila resultante = "
                + "(" + ", ".join(formatear_valor(v) for v in estado[fila]) + ").",
            ])
        elif " ← " in descripcion:
            izquierda, operacion = descripcion.split(" ← ")
            fila_objetivo = int(izquierda[1:]) - 1
            parte_filas = operacion.split("·F")
            fila_pivote = int(parte_filas[1]) - 1
            columna = next(j for j in range(n_variables) if estado_anterior[fila_pivote][j] != 0)
            pivote = estado_anterior[fila_pivote][columna]
            factor = estado_anterior[fila_objetivo][columna] / pivote
            pivotes_explicados.add(columna)
            lineas.extend([
                f"Paso {indice_paso}: eliminar la entrada de la fila {fila_objetivo + 1}, columna {columna + 1}.",
                f"Objetivo: hacer cero la entrada {formatear_valor(estado_anterior[fila_objetivo][columna])} debajo del pivote.",
                "Fundamento: reemplazar una fila por ella menos un múltiplo de otra conserva un sistema equivalente.",
                f"Pivote: a{fila_pivote + 1},{columna + 1} = {formatear_valor(pivote)}.",
                f"Multiplicador: m = {formatear_valor(estado_anterior[fila_objetivo][columna])} / "
                f"{formatear_valor(pivote)} = {formatear_valor(factor)}.",
                f"Operación: F{fila_objetivo + 1} ← F{fila_objetivo + 1} − ({formatear_valor(factor)})·F{fila_pivote + 1}.",
                "Cálculo de la fila: " + "; ".join(
                    f"{formatear_valor(estado_anterior[fila_objetivo][j])} − "
                    f"({formatear_valor(factor)})({formatear_valor(estado_anterior[fila_pivote][j])})"
                    f" = {formatear_valor(estado[fila_objetivo][j])}"
                    for j in range(columna, n_variables + 1)
                ) + ".",
            ])
            eliminadas.add(columna)
        estado_anterior = estado

    lineas.extend(["", "Matriz final en forma escalonada:", formatear_matriz(matriz_final)])
    for fila in range(len(matriz_final)):
        columna = next((j for j in range(n_variables) if matriz_final[fila][j] != 0), None)
        if columna is not None:
            if columna not in pivotes_explicados:
                lineas.append(f"Pivote seleccionado: a{fila + 1},{columna + 1} = "
                              f"{formatear_valor(matriz_final[fila][columna])}.")
            if columna not in eliminadas and all(
                matriz_final[i][columna] == 0 for i in range(fila + 1, len(matriz_final))
            ):
                lineas.append(f"Columna {columna + 1}: no requiere eliminación; las entradas inferiores ya son cero.")
    return lineas


def _texto_sustitucion_gauss(datos, n_variables):
    """Presenta sustitución hacia atrás sin asignar valores a variables libres."""
    matriz = datos["matriz_escalonada"]
    expresiones = datos["soluciones_generales"]
    libres = datos["variables_libres"]
    lineas = ["", "SUSTITUCIÓN HACIA ATRÁS:"]
    if libres:
        lineas.append("Las variables libres permanecen como parámetros; se expresan las variables básicas en función de ellas.")
    for fila in range(datos["rango"] - 1, -1, -1):
        pivote = next((j for j in range(n_variables) if matriz[fila][j] != 0), None)
        if pivote is None:
            continue
        lhs = " + ".join(f"({formatear_valor(matriz[fila][j])})·x{subindice(j + 1)}"
                          for j in range(pivote, n_variables) if matriz[fila][j] != 0)
        constante, terminos = expresiones[pivote]
        resultado = formatear_expresion(constante, terminos)
        if libres:
            lineas.append(f"Fila {fila + 1}: {lhs} = {formatear_valor(matriz[fila][-1])}; "
                          f"x{subindice(pivote + 1)} = {resultado}.")
        else:
            sustituidos = [f"({formatear_valor(matriz[fila][j])})({formatear_valor(expresiones[j][0])})"
                           for j in range(pivote + 1, n_variables) if matriz[fila][j] != 0]
            suma = sum(matriz[fila][j] * expresiones[j][0]
                       for j in range(pivote + 1, n_variables))
            numerador = matriz[fila][-1] - suma
            lineas.append(f"Fila {fila + 1}: {lhs} = {formatear_valor(matriz[fila][-1])}; "
                          f"x{subindice(pivote + 1)} = ({formatear_valor(matriz[fila][-1])} − "
                          f"({' + '.join(sustituidos) or '0'})) / {formatear_valor(matriz[fila][pivote])} "
                          f"= {formatear_valor(numerador / matriz[fila][pivote])}.")
    return lineas


def _texto_pasos_gauss_jordan(pasos, n_variables):
    """Explica las operaciones de Gauss-Jordan usando los estados registrados."""
    estado_anterior = pasos[0]["matriz"]
    lineas = ["PASOS DE REDUCCIÓN DE GAUSS-JORDAN:"]
    for indice, paso in enumerate(pasos[1:], 1):
        descripcion, estado = paso["descripcion"], paso["matriz"]
        if descripcion.startswith("Intercambio F"):
            filas = descripcion.removeprefix("Intercambio F").split(" ↔ F")
            fila_pivote, fila_candidata = int(filas[0]) - 1, int(filas[1]) - 1
            columna = next((j for j in range(n_variables) if estado[fila_pivote][j] != 0), 0)
            candidatos = [estado_anterior[i][columna] for i in range(fila_pivote, len(estado))]
            lineas.extend([
                f"Paso {indice}: intercambio para colocar el pivote en la fila activa.",
                f"Objetivo: elegir en la columna {columna + 1} un pivote no nulo de mayor valor absoluto.",
                "Fundamento: el pivoteo parcial evita dividir entre cero y limita el tamaño de los factores.",
                "Candidatos: " + ", ".join(formatear_valor(v) for v in candidatos) + ".",
                "Magnitudes comparadas: " + ", ".join(f"|{formatear_valor(v)}|" for v in candidatos) + ".",
                f"Operación: F{fila_pivote + 1} ↔ F{fila_candidata + 1}; se intercambian las filas completas de [A|b].",
            ])
        elif descripcion.startswith("Normalizar F"):
            fila = int(descripcion.split("F", 1)[1].split()[0]) - 1
            columna = next(j for j in range(n_variables) if estado_anterior[fila][j] != 0)
            pivote = estado_anterior[fila][columna]
            calculos = "; ".join(
                f"{formatear_valor(estado_anterior[fila][j])} / {formatear_valor(pivote)}"
                f" = {formatear_valor(estado[fila][j])}"
                for j in range(n_variables + 1)
            )
            lineas.extend([
                f"Paso {indice}: normalización de la fila {fila + 1}, columna pivote {columna + 1}.",
                f"Objetivo: convertir el pivote {formatear_valor(pivote)} en 1.",
                "Fundamento: dividir toda la fila por el mismo escalar no nulo conserva el sistema equivalente.",
                f"Pivote: a{fila + 1},{columna + 1} = {formatear_valor(pivote)}.",
                f"Cálculo de la fila: {calculos}.",
            ])
        elif " ← " in descripcion:
            izquierda, operacion = descripcion.split(" ← ")
            fila_objetivo = int(izquierda[1:]) - 1
            fila_pivote = int(operacion.split("·F")[1]) - 1
            columna = next(j for j in range(n_variables) if estado_anterior[fila_pivote][j] != 0)
            pivote = estado_anterior[fila_pivote][columna]
            entrada = estado_anterior[fila_objetivo][columna]
            factor = entrada / pivote
            ubicacion = "debajo" if fila_objetivo > fila_pivote else "encima"
            calculos = "; ".join(
                f"{formatear_valor(estado_anterior[fila_objetivo][j])} − "
                f"({formatear_valor(factor)})({formatear_valor(estado_anterior[fila_pivote][j])})"
                f" = {formatear_valor(estado[fila_objetivo][j])}"
                for j in range(columna, n_variables + 1)
            )
            lineas.extend([
                f"Paso {indice}: eliminación {ubicacion} del pivote en la fila {fila_pivote + 1}, columna {columna + 1}.",
                f"Objetivo: anular la entrada {formatear_valor(entrada)} de la fila {fila_objetivo + 1}.",
                "Fundamento: reemplazar una fila por ella menos un múltiplo de otra preserva el conjunto de soluciones.",
                f"Pivote: a{fila_pivote + 1},{columna + 1} = {formatear_valor(pivote)}.",
                f"Multiplicador: m = {formatear_valor(entrada)} / {formatear_valor(pivote)} = {formatear_valor(factor)}.",
                f"Operación: F{fila_objetivo + 1} ← F{fila_objetivo + 1} − ({formatear_valor(factor)})·F{fila_pivote + 1}.",
                f"Cálculo de la fila: {calculos}.",
            ])
        estado_anterior = estado
    return lineas


def _texto_lectura_rref(datos, tipo, n_variables):
    """Explica cómo leer pivotes, variables libres y contradicciones en la RREF."""
    matriz = datos["matriz_escalonada"]
    lineas = ["", "CÓMO LEER LA RREF:"]
    if tipo == "Inconsistente":
        fila = next((i for i in range(datos["rango"], len(matriz))
                     if all(matriz[i][j] == 0 for j in range(n_variables))), None)
        if fila is not None:
            lineas.append(f"La fila {fila + 1} representa 0 = {formatear_valor(matriz[fila][-1])}; el sistema es incompatible.")
        return lineas
    pivotes = columnas_pivote(matriz, datos["rango"])
    libres = [j for j in range(n_variables) if j not in pivotes]
    lineas.append("Cada columna pivote tiene un 1 líder y ceros en las demás filas; su ecuación permite leer la variable básica.")
    if libres:
        lineas.append("Las columnas sin pivote corresponden a variables libres, que se conservan como parámetros en la solución general.")
    else:
        lineas.append("No hay variables libres; los términos independientes de las filas pivote dan directamente la solución única.")
    return lineas


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
            ]
            if metodo == "gauss":
                lineas.extend(_texto_pasos_gauss(datos["pasos"], datos["matriz_escalonada"], n))
            elif metodo == "gauss-jordan":
                lineas.extend(_texto_pasos_gauss_jordan(datos["pasos"], n))
            else:
                lineas.append("PASOS DE ELIMINACION:")
                for i, paso in enumerate(datos["pasos"], 1):
                    lineas.extend([f"Paso {i}: {paso['descripcion']}", formatear_matriz(paso["matriz"])])
            nombre_final = (
                "forma escalonada reducida (RREF)"
                if metodo == "gauss-jordan" else "forma escalonada"
            )
            if metodo != "gauss":
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
            if metodo == "gauss-jordan":
                lineas.extend(_texto_lectura_rref(datos, clase["tipo"], n))
            if clase["tipo"] != "Inconsistente":
                if metodo == "gauss":
                    lineas.extend(_texto_sustitucion_gauss(datos, n))
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
        try:
            inversa, pasos, solucion, producto_ax = _resolver_por_matriz_inversa(
                matriz_a, vector_b
            )
        except ValueError as error:
            if "singular" not in str(error).lower():
                raise
            lineas = [
                "MODULO 1 | RESOLUCIÓN POR MATRIZ INVERSA",
                "=" * 58,
                "Para una matriz cuadrada, A⁻¹ existe exactamente cuando det(A) ≠ 0.",
                "Si det(A) = 0, A es singular: sus filas o columnas son dependientes y no existe A⁻¹.",
                "Por tanto, x = A⁻¹b no se puede usar para resolver este sistema.",
            ]
            reemplazar_texto(
                self.resultado,
                "\n".join(lineas) + "\n",
                "A es singular: no tiene inversa.",
            )
            return
        lineas = [
            "MODULO 1 | RESOLUCIÓN POR MATRIZ INVERSA",
            "=" * 58,
            "Para una matriz cuadrada, A⁻¹ existe exactamente cuando det(A) ≠ 0.",
            "Si det(A) = 0, A es singular y este método no puede calcular x = A⁻¹b.",
            "Construimos [A|I], donde I es la identidad del mismo orden que A.",
            "El objetivo de Gauss-Jordan es transformar [A|I] → [I|A⁻¹].",
            "Cada operación elemental es reversible y se aplica a la fila aumentada completa.",
            "Las operaciones componen una transformación invertible E aplicada a ambos bloques: [A|I] → [EA|E].",
            "Al llegar a [I|B], EA=I y B=E. Como A es cuadrada, E=A⁻¹; por eso el bloque derecho B es A⁻¹.",
            "Matriz aumentada inicial [A|I]:",
            formatear_matriz(pasos[0][1]),
        ]
        estado_anterior = pasos[0][1]
        for indice, (descripcion, estado) in enumerate(pasos[1:], 1):
            if descripcion.startswith("Forma reducida final"):
                lineas.extend([
                    f"\n{descripcion}:",
                    "Resultado final de Gauss-Jordan (no es una operación adicional):",
                    formatear_matriz(estado),
                ])
                estado_anterior = estado
                continue
            lineas.extend([
                f"\nPaso {indice}: {descripcion}.",
                "Matriz aumentada antes de la operación:",
                formatear_matriz(estado_anterior),
            ])
            if descripcion.startswith("Intercambiar F"):
                partes = descripcion.removeprefix("Intercambiar F").split(" y F")
                fila_1, fila_2 = int(partes[0]) - 1, int(partes[1]) - 1
                valor_pivote = estado[fila_1][fila_1]
                interpretacion = (
                    f"Se busca llevar a la fila {fila_1 + 1} un pivote no nulo; "
                    f"la fila {fila_2 + 1} aporta {formatear_valor(valor_pivote)} "
                    "en esa columna. Intercambiar filas es reversible y se aplica "
                    "a todas las entradas de ambas filas, en los dos bloques."
                )
                lineas.extend([interpretacion, "Matriz aumentada después del intercambio:"])
            elif descripcion.startswith("Dividir F"):
                partes = descripcion.removeprefix("Dividir F").split(" entre ")
                fila = int(partes[0]) - 1
                pivote = estado_anterior[fila][fila]
                interpretacion = (
                    f"El pivote de F{fila + 1} es {formatear_valor(pivote)}. "
                    "Se divide cada entrada de la fila aumentada completa por ese "
                    "valor para convertir el pivote en 1. Como el pivote no es "
                    "cero, la operación es reversible."
                )
                lineas.extend([interpretacion, "Cálculo de cada entrada de la fila:"])
                for columna, (antes, despues) in enumerate(
                    zip(estado_anterior[fila], estado[fila]), 1
                ):
                    lineas.append(
                        f"  columna {columna}: {formatear_valor(antes)} / "
                        f"{formatear_valor(pivote)} = {formatear_valor(despues)}"
                    )
                lineas.append("Matriz aumentada después de dividir la fila:")
            elif " <- " in descripcion:
                partes = descripcion.split(" <- ", 1)[0]
                fila_destino = int(partes.removeprefix("F")) - 1
                fila_pivote = int(descripcion.rsplit("F", 1)[1]) - 1
                columna_pivote = fila_pivote
                factor = estado_anterior[fila_destino][columna_pivote]
                valor_pivote = estado_anterior[fila_pivote][columna_pivote]
                interpretacion = (
                    f"Se usa el pivote {formatear_valor(valor_pivote)} de "
                    f"F{fila_pivote + 1} para hacer cero la entrada "
                    f"{formatear_valor(factor)} de F{fila_destino + 1}. "
                    f"La operación reversible es F{fila_destino + 1} ← "
                    f"F{fila_destino + 1} − ({formatear_valor(factor)})"
                    f"F{fila_pivote + 1}; transforma la fila aumentada completa."
                )
                lineas.extend([interpretacion, "Cálculo de cada entrada de la fila:"])
                for columna, (antes, base, despues) in enumerate(zip(
                    estado_anterior[fila_destino],
                    estado_anterior[fila_pivote],
                    estado[fila_destino],
                ), 1):
                    lineas.append(
                        f"  columna {columna}: {formatear_valor(antes)} - "
                        f"({formatear_valor(factor)})({formatear_valor(base)}) "
                        f"= {formatear_valor(despues)}"
                    )
                lineas.append("Matriz aumentada después de eliminar la entrada:")
            else:
                lineas.extend(["Estado final alcanzado:", formatear_matriz(estado)])
                estado_anterior = estado
                continue
            lineas.append(formatear_matriz(estado))
            estado_anterior = estado
        lineas.extend([
            "\nEl bloque izquierdo es I; por la equivalencia conservada, el derecho es A⁻¹.",
            "Inversa final A⁻¹:",
            formatear_matriz(inversa),
            "\nVector b:",
            formatear_vector(vector_b),
            "\nProducto x = A⁻¹b:",
        ])
        for i, fila in enumerate(inversa):
            productos = [fila[j] * vector_b[j] for j in range(len(vector_b))]
            terminos = " + ".join(
                f"({formatear_valor(fila[j])})({formatear_valor(vector_b[j])})"
                for j in range(len(vector_b))
            )
            lineas.append(
                f"x{subindice(i + 1)} = {terminos}"
            )
            lineas.append(
                "  Productos: " + " + ".join(formatear_valor(v) for v in productos)
                + " = " + formatear_valor(solucion[i])
            )
            lineas.append(
                f"  Por tanto, x{subindice(i + 1)} = "
                f"{formatear_valor(solucion[i])}"
            )
        lineas.extend([
            "Solución x = (" + ", ".join(formatear_valor(v) for v in solucion) + ")",
            "\nVerificación exacta de Ax = b:",
            "Sustituimos x en cada ecuación original: el resultado de la fila i debe coincidir con bᵢ.",
            "Ax = (" + ", ".join(formatear_valor(v) for v in producto_ax) + ")",
        ])
        cumple = producto_ax == vector_b
        for i, fila in enumerate(matriz_a):
            productos = [fila[j] * solucion[j] for j in range(len(solucion))]
            terminos = " + ".join(
                f"({formatear_valor(fila[j])})({formatear_valor(solucion[j])})"
                for j in range(len(solucion))
            )
            lineas.append(
                f"Ecuación {i + 1}: {terminos}"
            )
            lineas.append(
                "  Productos: " + " + ".join(formatear_valor(v) for v in productos)
                + f" = {formatear_valor(producto_ax[i])}; "
                f"{'=' if producto_ax[i] == vector_b[i] else '≠'} "
                f"{formatear_valor(vector_b[i])}"
            )
        lineas.append("Ax = b: " + ("Se cumple" if cumple else "No se cumple"))
        if cumple:
            lineas.append(
                "Como cada componente calculado coincide con el de b, "
                "la solución satisface todas las ecuaciones del sistema."
            )
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
            "Objetivo: obtener la solución única de Ax=b mediante determinantes.",
            f"A debe ser cuadrada de orden {len(matriz_a)} para que det(A) esté definido.",
            "Si D = det(A) ≠ 0, las columnas de A son independientes, A es invertible "
            "y Ax=b tiene una solución única.",
            "Fundamento de los determinantes sustituidos:",
            "Escribimos las columnas de A como a₁,…,aₙ. Como b=Ax, "
            "b=x₁a₁+⋯+xₙaₙ.",
            "Al sustituir la columna i por b y usar la linealidad del determinante "
            "en esa columna, cada término con aⱼ para j≠i tiene dos columnas "
            "iguales y vale cero; queda Dᵢ=xᵢD.",
            "Cuando D≠0, dividimos Dᵢ entre D para obtener xᵢ=Dᵢ/D.",
            "Paso 1: calcular D = det(A).",
            "Matriz A:",
            formatear_matriz(matriz_a),
            "Vector b = (" + ", ".join(formatear_valor(valor) for valor in vector_b) + ")",
        ]
        lineas.extend(
            _explicar_pasos_determinante(datos["pasos_determinante"], "Cálculo de D")
        )
        determinante = datos["determinante"]
        lineas.append(f"D = {formatear_valor(determinante)}")
        if datos["solucion"] is None:
            lineas.extend([
                "",
                "D = 0: la regla de Cramer no determina una solución única y no se puede dividir entre D.",
                "El sistema puede ser incompatible o tener infinitas soluciones; este cálculo no distingue esos casos.",
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
                f"Esta sustitución produce D{subindice(indice + 1)} y, por el fundamento anterior, "
                f"D{subindice(indice + 1)} = x{subindice(indice + 1)}D.",
                formatear_matriz(reemplazo["matriz"]),
                f"Paso 3: calcular D{subindice(indice + 1)} = det(A{subindice(indice + 1)}).",
            ])
            lineas.extend(
                _explicar_pasos_determinante(
                    reemplazo["pasos_determinante"],
                    f"Cálculo de D{subindice(indice + 1)}",
                )
            )
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
            "",
            "VERIFICACIÓN EN LAS ECUACIONES ORIGINALES:",
        ])
        cumple = True
        for i, fila in enumerate(matriz_a):
            productos = " + ".join(
                f"({formatear_valor(fila[j])})({formatear_valor(datos['solucion'][j])})"
                for j in range(len(fila))
            )
            total = sum(fila[j] * datos["solucion"][j] for j in range(len(fila)))
            coincide = total == vector_b[i]
            cumple = cumple and coincide
            lineas.append(
                f"Ecuación {i + 1}: {productos} = {formatear_valor(total)} "
                f"{'=' if coincide else '≠'} {formatear_valor(vector_b[i])}"
            )
        lineas.append(
            "Conclusión: la solución satisface todas las ecuaciones originales."
            if cumple else "Conclusión: la solución no satisface todas las ecuaciones originales."
        )
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
