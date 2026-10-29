"""
Pantalla del Módulo III: Álgebra de matrices.

Unidad II, Álgebra de matrices [P3 · P5 · P6]:
opciones 1–4 (suma, resta, escalar, producto) [P3]; opciones 5–8 (transpuesta,
determinante, inversa por Gauss-Jordan y por adjunta) [P5]; opción 9 (verificador) [P6].
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import customtkinter as ctk

from backend.eliminacion import eliminacion_con_pasos
from backend.matrices import (
    determinante_cofactores,
    determinante_triangular,
    invertir_adjunta,
    invertir_gauss_jordan,
    sarrus_3x3,
    verificar_inversa,
)
from backend.matriz import formatear_valor, subindice
from backend.operaciones_matriciales import (
    LIMITE_COFACTORES,
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    resta_matrices,
    suma_matrices,
    transponer_matriz,
)
from backend.verificador import verificar_propiedades_matrices
from modulos._comun import (
    llenar,
    boton_primario, boton_secundario, copiar_entradas_al_portapapeles,
    copiar_matriz_al_portapapeles, crear_controles, crear_estructura, entrada_numero,
    formatear_matriz, leer_entero, leer_fraccion, matriz_en_linea, mensaje_error,
    mostrar_teoremas, pegar_matriz_en_entradas, reemplazar_texto, reiniciar_celdas, subtitulo,
)
from modulos.modulo_determinantes import _texto_sarrus, _texto_traza_triangular

LOGO = (
    "[ A ][ B ]  MÓDULO III: ÁLGEBRA DE MATRICES\n"
    "[ C ][ D ]  Operaciones, Traspuesta y Matriz Inversa"
)


def invertir_matriz(A):
    """Devuelve (A⁻¹, pasos) por Gauss-Jordan; se conserva el nombre usado en módulos anteriores."""
    return invertir_gauss_jordan(A)


def contar_pivotes(A):
    """Devuelve el número de posiciones pivote de A reduciendo [A | 0] por filas."""
    return eliminacion_con_pasos([fila[:] + [0] for fila in A], metodo="gauss")[1]


def diagnostico_invertibilidad(A, det_A):
    """Devuelve el diagnóstico del Teorema de la Matriz Invertible para A cuadrada."""
    n = len(A)
    if det_A != 0:
        return (f"La matriz es invertible: det(A) ≠ 0, tiene {n} posiciones pivote, "
                f"sus columnas son L.I. y generan ℝ{_superindice(n)}.")
    return (f"La matriz es singular (no tiene inversa): det(A) = 0 "
            f"(solo {contar_pivotes(A)} posiciones pivote de {n}).")


def _superindice(n):
    """Escribe n con dígitos superíndice (para ℝⁿ)."""
    return str(n).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))


def _detalle_entradas(A, B, C, operador):
    """Líneas «cᵢⱼ = a op b = resultado» para operaciones entrada a entrada."""
    return [f"c{subindice(i + 1)},{subindice(j + 1)} = {formatear_valor(A[i][j])} {operador} "
            f"{formatear_valor(B[i][j])} = {formatear_valor(C[i][j])}"
            for i in range(len(A)) for j in range(len(A[0]))]


class ModuloMatrices(ctk.CTkFrame):
    """Panel del Módulo III con las nueve operaciones del menú y los teoremas clave."""

    def __init__(self, master, on_back):
        """Construye la pantalla con A, B y C de 2 × 2."""
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A, self.entradas_B, self.entradas_C = [], [], []
        self.ultima_matriz_resultado = None
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Crea la guía, los tamaños, los datos del verificador, las tablas y los botones."""
        zonas = crear_estructura(
            self, self.on_back, numero=4, titulo="Operaciones con matrices",
            descripcion="Operaciones, determinante, inversa y verificador de propiedades.",
            logo=LOGO,
            pasos=[
                "Escribe el tamaño de A y de B (filas × columnas) y pulsa «Crear tablas». "
                "C tiene el mismo tamaño que B.",
                "Llena las matrices. k, Aᵀ, det(A) y A⁻¹ solo usan A; el verificador (9) usa "
                "A, B y C cuadradas del mismo orden, las filas i, j y el escalar k.",
                "Pulsa la operación. A + B y A − B piden el mismo tamaño; A · B pide que las "
                "columnas de A sean iguales a las filas de B.",
            ],
            clave_teoremas="matrices", ejemplo=self.cargar_ejemplo,
            indicacion="Verás la operación entrada por entrada, el diagnóstico de invertibilidad, "
                       "los pasos de cada método y la comprobación A · A⁻¹ = I.",
        )
        self.resultado = zonas.resultado
        self._crear_controles(zonas.contenido)
        self._crear_tablas(zonas.contenido)
        self._crear_portapapeles(zonas.contenido)
        self._crear_botones(zonas.acciones)

    def _crear_controles(self, contenido):
        """Campos de tamaño de A y B, del escalar k y de las filas i, j."""
        dimensiones, self.entries_dim = crear_controles(
            contenido,
            [("am", "Filas de A", "2", 80), ("an", "Columnas de A", "2", 100),
             ("bm", "Filas de B", "2", 80), ("bn", "Columnas de B", "2", 100)],
            self.actualizar_entradas, texto_boton="Crear tablas",
        )
        dimensiones.pack(anchor="w", padx=10, pady=(10, 0))
        datos, entradas = crear_controles(
            contenido,
            [("k", "Escalar k", "2", 80, False), ("fi", "Fila i", "1", 70, False),
             ("fj", "Fila j", "2", 70, False)],
            None, texto_boton=None,
        )
        datos.pack(anchor="w", padx=10, pady=(8, 0))
        self.entry_escalar, self.entry_fila_i, self.entry_fila_j = entradas["k"], entradas["fi"], entradas["fj"]

    def _crear_tablas(self, contenido):
        """Crea los marcos donde van las celdas de A, B y C."""
        self.tablas = ctk.CTkFrame(contenido, fg_color="transparent")
        self.tablas.pack(anchor="w", fill="x", pady=(2, 0))
        self.marcos = []
        for columna, titulo in enumerate(("Matriz A", "Matriz B", "Matriz C (verificador)")):
            subtitulo(self.tablas, titulo).grid(row=0, column=columna, sticky="w", padx=(10, 18), pady=(8, 4))
            marco = ctk.CTkFrame(self.tablas, fg_color="transparent")
            marco.grid(row=1, column=columna, sticky="nw", padx=(6, 18))
            self.marcos.append(marco)

    def _crear_portapapeles(self, contenido):
        """Botones para copiar y pegar matrices (compatibles con Excel)."""
        fila = ctk.CTkFrame(contenido, fg_color="transparent")
        fila.pack(anchor="w", padx=10, pady=(6, 0))
        for texto, accion, ancho in (
            ("Copiar A", lambda: copiar_entradas_al_portapapeles(self, self.entradas_A), 84),
            ("Pegar en A", lambda: pegar_matriz_en_entradas(self, self.entradas_A), 94),
            ("Copiar B", lambda: copiar_entradas_al_portapapeles(self, self.entradas_B), 84),
            ("Pegar en B", lambda: pegar_matriz_en_entradas(self, self.entradas_B), 94),
            ("Copiar resultado", lambda: copiar_matriz_al_portapapeles(self, self.ultima_matriz_resultado), 124),
        ):
            boton_secundario(fila, texto, accion, width=ancho, height=30).pack(side="left", padx=(0, 5))

    def _crear_botones(self, acciones):
        """Botones 1 a 9, 0 y Limpiar, en tres columnas para no tapar las tablas."""
        acciones.grid_columnconfigure((0, 1, 2), weight=1, uniform="ops")
        operaciones = [
            ("1. Suma", "suma"), ("2. Resta", "resta"), ("3. Escalar", "escalar"),
            ("4. Producto", "producto"), ("5. Transpuesta", "transpuesta"), ("6. Determinante", "determinante"),
            ("7. Inversa G-J", "inversa"), ("8. Inversa adjunta", "adjunta"), ("9. Verificador", "propiedades"),
        ]
        for indice, (texto, operacion) in enumerate(operaciones):
            boton_primario(acciones, texto, lambda op=operacion: self.calcular(op), height=32).grid(
                row=indice // 3, column=indice % 3, sticky="ew", padx=(0 if indice % 3 == 0 else 6, 0), pady=(0, 5)
            )
        boton_secundario(acciones, "0. Teoremas clave", self._ver_teoremas, height=30).grid(
            row=3, column=0, columnspan=2, sticky="ew")
        boton_secundario(acciones, "Limpiar", self.limpiar, height=30).grid(
            row=3, column=2, sticky="ew", padx=(6, 0))

    def _ver_teoremas(self):
        """Opción 0: abre los teoremas clave del módulo."""
        mostrar_teoremas(self, "matrices", "Álgebra de matrices")

    def actualizar_entradas(self):
        """Valida los tamaños y crea las celdas de A, B y C (C con el tamaño de B)."""
        nombres = {"am": "Las filas de A", "an": "Las columnas de A",
                   "bm": "Las filas de B", "bn": "Las columnas de B"}
        try:
            dim = {clave: leer_entero(entry, nombres[clave]) for clave, entry in self.entries_dim.items()}
        except ValueError as error:
            mensaje_error(error)
            return
        tamanos = [(dim["am"], dim["an"]), (dim["bm"], dim["bn"]), (dim["bm"], dim["bn"])]
        self.entradas_A, self.entradas_B, self.entradas_C = (
            self._construir_tabla(marco, filas, columnas) for marco, (filas, columnas) in zip(self.marcos, tamanos)
        )
        reemplazar_texto(self.resultado, "")

    def _construir_tabla(self, marco, filas, columnas):
        """Crea una cuadrícula de celdas filas × columnas dentro de `marco`."""
        for widget in marco.winfo_children():
            widget.destroy()
        entradas = []
        for i in range(filas):
            fila = [entrada_numero(marco, ancho=56) for _ in range(columnas)]
            for j, celda in enumerate(fila):
                celda.grid(row=i, column=j, padx=2, pady=2)
            entradas.append(fila)
        return entradas

    def _leer_matriz(self, entradas, nombre):
        """Convierte las celdas de una matriz a fracciones exactas."""
        return [[leer_fraccion(celda, f"La entrada ({i + 1},{j + 1}) de {nombre}") for j, celda in enumerate(fila)]
                for i, fila in enumerate(entradas)]

    def calcular(self, operacion):
        """Ejecuta la operación elegida y muestra el procedimiento y la respuesta."""
        metodos = {
            "suma": self._suma, "resta": self._resta, "escalar": self._escalar,
            "producto": self._producto, "transpuesta": self._transpuesta,
            "determinante": self._determinante, "inversa": self._inversa_gauss_jordan,
            "adjunta": self._inversa_adjunta, "propiedades": self._verificador,
        }
        self.ultima_matriz_resultado = None
        try:
            A = self._leer_matriz(self.entradas_A, "A")
            lineas, resumen = metodos[operacion](A)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)
            return
        reemplazar_texto(self.resultado, "\n".join(lineas) + "\n", resumen)

    def _suma(self, A):
        """Opción 1: A + B entrada a entrada."""
        B = self._leer_matriz(self.entradas_B, "B")
        C = suma_matrices(A, B)
        self.ultima_matriz_resultado = C
        return (_encabezado("SUMA DE MATRICES: A + B", A, B,
                            "Se suman las entradas que ocupan la misma posición: cᵢⱼ = aᵢⱼ + bᵢⱼ.",
                            f"A y B deben tener el mismo tamaño: A es {_tam(A)} y B es {_tam(B)} ✓")
                + ["Paso a paso:"] + _detalle_entradas(A, B, C, "+")
                + _resultado(f"A + B ({_tam(C)})", C), f"A + B = {matriz_en_linea(C)}")

    def _resta(self, A):
        """Opción 2: A − B entrada a entrada."""
        B = self._leer_matriz(self.entradas_B, "B")
        C = resta_matrices(A, B)
        self.ultima_matriz_resultado = C
        return (_encabezado("RESTA DE MATRICES: A − B", A, B,
                            "Se restan las entradas que ocupan la misma posición: cᵢⱼ = aᵢⱼ − bᵢⱼ.",
                            f"A y B deben tener el mismo tamaño: A es {_tam(A)} y B es {_tam(B)} ✓")
                + ["Paso a paso:"] + _detalle_entradas(A, B, C, "−")
                + _resultado(f"A − B ({_tam(C)})", C), f"A − B = {matriz_en_linea(C)}")

    def _escalar(self, A):
        """Opción 3: k · A, multiplicando cada entrada por k."""
        k = leer_fraccion(self.entry_escalar, "El escalar k")
        C = multiplicar_escalar_matriz(k, A)
        self.ultima_matriz_resultado = C
        detalle = [f"c{subindice(i + 1)},{subindice(j + 1)} = {formatear_valor(k)} · {formatear_valor(A[i][j])} "
                   f"= {formatear_valor(C[i][j])}" for i in range(len(A)) for j in range(len(A[0]))]
        return (_encabezado(f"MULTIPLICACIÓN POR ESCALAR: k · A   (k = {formatear_valor(k)})", A, None,
                            "Cada entrada de A se multiplica por el número k: cᵢⱼ = k · aᵢⱼ.",
                            "Se puede hacer con una matriz de cualquier tamaño; el resultado tiene el mismo tamaño que A.")
                + ["Paso a paso:"] + detalle + _resultado(f"k · A ({_tam(C)})", C), f"k · A = {matriz_en_linea(C)}")

    def _producto(self, A):
        """Opción 4: A · B, cada entrada es el producto punto de una fila de A por una columna de B."""
        B = self._leer_matriz(self.entradas_B, "B")
        C = multiplicar_matrices(A, B)
        self.ultima_matriz_resultado = C
        lineas = _encabezado(
            "PRODUCTO DE MATRICES: A · B", A, B,
            "Cada entrada cᵢⱼ se obtiene multiplicando la fila i de A por la columna j de B "
            "término a término y sumando los productos.",
            f"Las columnas de A ({len(A[0])}) deben ser iguales a las filas de B ({len(B)}) ✓; "
            f"el resultado tiene las filas de A y las columnas de B: {_tam(C)}.",
        ) + ["Paso a paso:"]
        for i in range(len(A)):
            for j in range(len(B[0])):
                productos = " + ".join(f"({formatear_valor(A[i][t])})({formatear_valor(B[t][j])})"
                                       for t in range(len(A[0])))
                lineas.append(f"c{subindice(i + 1)},{subindice(j + 1)} = fila {i + 1} de A · columna {j + 1} de B "
                              f"= {productos} = {formatear_valor(C[i][j])}")
        lineas += _resultado(f"A · B ({_tam(C)})", C)
        lineas.append("Ojo: en general A · B ≠ B · A; el orden de los factores importa.")
        return lineas, f"A · B = {matriz_en_linea(C)}"

    def _transpuesta(self, A):
        """Opción 5: Aᵀ, las filas de A pasan a ser columnas."""
        C = transponer_matriz(A)
        self.ultima_matriz_resultado = C
        detalle = [f"Fila {i + 1} de A {_vector_en_linea(A[i])}  →  columna {i + 1} de Aᵀ" for i in range(len(A))]
        return (_encabezado("TRANSPUESTA: Aᵀ", A, None,
                            "Las filas de A se escriben como columnas: (Aᵀ)ᵢⱼ = aⱼᵢ.",
                            f"Se puede hacer con cualquier matriz; si A es {_tam(A)}, Aᵀ es {_tam(C)}.")
                + ["Paso a paso:"] + detalle + _resultado(f"Aᵀ ({_tam(C)})", C), f"Aᵀ = {matriz_en_linea(C)}")

    def _determinante(self, A):
        """Opción 6: det(A) por triangularización, cofactores y (en 3 × 3) Sarrus."""
        det_A, pasos = determinante_triangular(A)
        lineas = ["DETERMINANTE", "", "Reducción a forma triangular (método eficiente):"]
        lineas.extend(_texto_traza_triangular(pasos))
        lineas.extend(["", f"det(A) por triangularización = {formatear_valor(det_A)}"])
        lineas.extend(self._otros_metodos_determinante(A, det_A))
        diagnostico = diagnostico_invertibilidad(A, det_A)
        lineas.extend(["", diagnostico])
        estado = "invertible" if det_A != 0 else "singular (no tiene inversa)"
        return lineas, f"det(A) = {formatear_valor(det_A)}   ·   A es {estado}"

    def _otros_metodos_determinante(self, A, det_A):
        """Líneas del determinante por cofactores (y Sarrus en 3 × 3), comparadas con el triangular."""
        if len(A) > LIMITE_COFACTORES:
            return [f"Expansión por cofactores omitida: con n = {len(A)} necesitaría cerca de "
                    f"{len(A)}! operaciones (se calcula hasta n = {LIMITE_COFACTORES})."]
        det_cofactores = determinante_cofactores(A)
        lineas = [f"det(A) por expansión de cofactores = {formatear_valor(det_cofactores)}"
                  f"   →   {'coincide' if det_cofactores == det_A else 'NO coincide'}"]
        if len(A) == 3:
            det_sarrus = sarrus_3x3(A)
            texto_sarrus, resultado_mostrado = _texto_sarrus(A)
            lineas.extend(texto_sarrus)
            lineas.append(
                f"Comprobación con Sarrus: {formatear_valor(det_sarrus)} "
                f"{'coincide' if resultado_mostrado == det_sarrus == det_A else 'NO coincide'} "
                "con la triangularización."
            )
        return lineas

    def _inversa_gauss_jordan(self, A):
        """Opción 7: A⁻¹ reduciendo [A | I] a [I | A⁻¹]."""
        return self._inversa(A, "gauss-jordan")

    def _inversa_adjunta(self, A):
        """Opción 8: A⁻¹ = (1/det(A)) · adj(A)."""
        if len(A) > LIMITE_COFACTORES:
            raise ValueError(f"La inversa por adjunta usa cofactores (cerca de n! operaciones) y se "
                             f"calcula hasta n = {LIMITE_COFACTORES}. Para matrices más grandes usa la opción 7.")
        return self._inversa(A, "adjunta")

    def _inversa(self, A, metodo):
        """Calcula A⁻¹ con el método indicado, la verifica y la compara con el otro método."""
        det_A, _ = determinante_triangular(A)
        if det_A == 0:
            diagnostico = diagnostico_invertibilidad(A, det_A)
            return ["MATRIZ INVERSA", "", diagnostico, "La inversa no se calcula."], "A es singular: no tiene inversa"
        if metodo == "adjunta":
            inversa, pasos = invertir_adjunta(A)
            titulo, otro = "INVERSA POR MATRIZ ADJUNTA: A⁻¹ = (1/det(A)) · adj(A)", "Gauss-Jordan"
            lineas = [titulo, "",
                      "Qué se hace: se calculan los menores, se les pone signo (cofactores), se transpone "
                      "esa matriz (adjunta) y se divide entre det(A).",
                      f"Condición: A debe ser cuadrada y det(A) ≠ 0. Aquí A es {_tam(A)} y "
                      f"det(A) = {formatear_valor(det_A)} ✓", ""]
            lineas.extend(_texto_menores(A))
            lineas.append("")
            for indice, (descripcion, matriz_paso) in enumerate(pasos, 1):
                lineas.extend([f"Paso {indice}: {descripcion}", formatear_matriz(matriz_paso)])
        else:
            inversa, pasos = invertir_gauss_jordan(A)
            titulo, otro = "INVERSA POR GAUSS-JORDAN: [A | I] → [I | A⁻¹]", "adjunta"
            lineas = [titulo, "",
                      "Qué se hace: se reduce [A | I] con operaciones de fila hasta que a la izquierda "
                      "quede la identidad; lo que queda a la derecha es A⁻¹.",
                      f"Condición: A debe ser cuadrada y tener {len(A)} pivotes (det(A) ≠ 0). "
                      f"Aquí det(A) = {formatear_valor(det_A)} ✓", ""]
            for indice, (descripcion, matriz_paso) in enumerate(pasos, 1):
                lineas.append(f"Paso {indice}: {descripcion}")
                por_que = _por_que_paso(descripcion)
                if por_que:
                    lineas.append(f"   Por qué: {por_que}")
                lineas.append(formatear_matriz(matriz_paso))
        self.ultima_matriz_resultado = inversa
        producto, identidad, cumple = verificar_inversa(A, inversa, multiplicar_matrices)
        lineas.extend(["", "A⁻¹ =", formatear_matriz(inversa), "", "Comprobación: A · A⁻¹ =",
                       formatear_matriz(producto), "A · A⁻¹ = I: " + ("Se cumple" if cumple else "No se cumple")])
        lineas.extend(self._comparar_metodos_inversa(A, inversa, otro))
        lineas.extend(["", diagnostico_invertibilidad(A, det_A)])
        return lineas, f"A⁻¹ = {matriz_en_linea(inversa)}"

    def _comparar_metodos_inversa(self, A, inversa, otro):
        """Compara la inversa con la del otro método (adjunta solo hasta el límite de cofactores)."""
        if otro == "adjunta" and len(A) > LIMITE_COFACTORES:
            return [f"Comparación con la adjunta omitida para n > {LIMITE_COFACTORES} (usa cofactores)."]
        otra = invertir_adjunta(A)[0] if otro == "adjunta" else invertir_gauss_jordan(A)[0]
        return [f"Comparación con el método por {otro}: "
                + ("las dos inversas coinciden" if otra == inversa else "las inversas NO coinciden")]

    def _verificador(self, A):
        """Opción 9: evalúa las propiedades de transposición, inversa y determinantes."""
        B = self._leer_matriz(self.entradas_B, "B")
        C = self._leer_matriz(self.entradas_C, "C")
        k = leer_fraccion(self.entry_escalar, "El escalar k")
        fila_i = leer_entero(self.entry_fila_i, "La fila i", 1, len(A)) - 1
        fila_j = leer_entero(self.entry_fila_j, "La fila j", 1, len(A)) - 1
        categorias, extra = verificar_propiedades_matrices(A, B, C, k, fila_i, fila_j)
        lineas = [f"VERIFICADOR DE PROPIEDADES   (k = {formatear_valor(k)}, i = {fila_i + 1}, j = {fila_j + 1})",
                  "",
                  "Qué se hace: para cada propiedad se calculan por separado sus dos lados con las "
                  "funciones de la calculadora y se comparan entrada por entrada.",
                  "Condición: A, B y C deben ser cuadradas y del mismo tamaño; las propiedades de la "
                  "inversa solo aplican si A (y B) tienen det ≠ 0.",
                  f"det(A) = {formatear_valor(extra['det_A'])}"]
        cumplen = evaluadas = 0
        for categoria, propiedades in categorias:
            lineas.extend(["", categoria])
            for propiedad in propiedades:
                lineas.extend(_texto_propiedad(propiedad))
                evaluadas += propiedad["cumple"] is not None
                cumplen += propiedad["cumple"] is True
        lineas.extend(["", "T (forma triangular de A, usada en la última propiedad) =", formatear_matriz(extra["T"])])
        no_aplican = sum(len(p) for _, p in categorias) - evaluadas
        resumen = f"Se cumplen {cumplen} de {evaluadas} propiedades evaluadas"
        return lineas, resumen + (f"   ·   {no_aplican} no aplican" if no_aplican else "")

    def cargar_ejemplo(self):
        """Carga A, B y C de 2 × 2 y calcula A · B; las demás opciones usan los mismos datos."""
        llenar([self.entries_dim[c] for c in ("am", "an", "bm", "bn")], [2, 2, 2, 2])
        self.actualizar_entradas()
        for matriz, valores in ((self.entradas_A, [[1, 2], [3, 4]]), (self.entradas_B, [[0, 1], [1, 1]]),
                                (self.entradas_C, [[2, 0], [1, 3]])):
            for fila, fila_valores in zip(matriz, valores):
                llenar(fila, fila_valores)
        llenar([self.entry_escalar, self.entry_fila_i, self.entry_fila_j], [3, 1, 2])
        self.calcular("producto")

    def limpiar(self):
        """Pone en cero A, B, C y el escalar, y vuelve a mostrar la guía."""
        reiniciar_celdas(self.entradas_A, self.entradas_B, self.entradas_C, [self.entry_escalar])
        self.ultima_matriz_resultado = None
        reemplazar_texto(self.resultado, "")


def _tam(M):
    """Tamaño de una matriz como texto: «2 × 3»."""
    return f"{len(M)} × {len(M[0])}"


def _vector_en_linea(fila):
    """Escribe una fila como (a, b, c)."""
    return "(" + ", ".join(formatear_valor(v) for v in fila) + ")"


def _encabezado(titulo, A, B, que_se_hace, condicion):
    """Primeras líneas de cada operación: datos, qué se hace y la condición que debe cumplirse."""
    lineas = [titulo, "", "A =", formatear_matriz(A)]
    if B is not None:
        lineas += ["B =", formatear_matriz(B)]
    return lineas + ["", f"Qué se hace: {que_se_hace}", f"Condición: {condicion}", ""]


def _resultado(nombre, C):
    """Últimas líneas de cada operación: la matriz resultante."""
    return ["", f"Resultado: {nombre} =", formatear_matriz(C)]


# Para qué sirve cada tipo de paso de la inversa por Gauss-Jordan.
_POR_QUE_GAUSS_JORDAN = (
    ("Matriz aumentada", "Se escribe la identidad a la derecha de A: las mismas operaciones que "
                         "convierten A en I convierten I en A⁻¹."),
    ("Intercambiar", "Se cambia de fila para tener un pivote distinto de cero en la diagonal."),
    ("Dividir", "Se divide la fila entre su pivote para que la diagonal quede en 1."),
    ("<-", "Se resta un múltiplo de la fila del pivote para hacer cero esa entrada de la columna."),
    ("Forma reducida", "A la izquierda quedó la identidad: lo que está a la derecha es A⁻¹."),
)

# Qué significa cada propiedad del verificador, en una frase.
_SIGNIFICADO_PROPIEDAD = (
    ("(Aᵀ)ᵀ", "Transponer dos veces devuelve la matriz original."),
    ("(A + B)ᵀ", "Transponer una suma da lo mismo que sumar las transpuestas."),
    ("(kA)ᵀ", "Un número que multiplica a la matriz sale de la transpuesta."),
    ("(AB)ᵀ", "La transpuesta de un producto invierte el orden de los factores."),
    ("A(B + C)", "El producto se distribuye sobre la suma."),
    ("(AB)C", "El producto de matrices es asociativo: se puede agrupar de cualquier forma."),
    ("(A⁻¹)⁻¹", "La inversa de la inversa es la matriz original."),
    ("(AB)⁻¹", "La inversa de un producto invierte el orden de los factores."),
    ("(Aᵀ)⁻¹", "Transponer e invertir se pueden hacer en cualquier orden."),
    ("A · A⁻¹", "Multiplicar una matriz por su inversa da la identidad."),
    ("det(Aᵀ)", "Transponer no cambia el determinante."),
    ("det(AB)", "El determinante de un producto es el producto de los determinantes."),
    ("det(A⁻¹)", "El determinante de la inversa es el recíproco del determinante."),
    ("det(kA)", "Multiplicar las n filas por k multiplica el determinante por kⁿ."),
    ("↔", "Intercambiar dos filas cambia el signo del determinante."),
    ("+ k·", "Sumarle a una fila un múltiplo de otra no cambia el determinante."),
    ("← k·", "Multiplicar una fila por k multiplica el determinante por k."),
    ("det(T)", "En una matriz triangular, el determinante es el producto de la diagonal."),
)


def _por_que_paso(descripcion):
    """Explicación breve del tipo de paso de la inversa por Gauss-Jordan."""
    if "entre 1" in descripcion and descripcion.startswith("Dividir"):
        return "El pivote ya es 1: la fila no cambia."
    return next((texto for clave, texto in _POR_QUE_GAUSS_JORDAN if clave in descripcion), "")


def _significado(nombre):
    """Frase que explica qué afirma una propiedad del verificador."""
    return next((texto for clave, texto in _SIGNIFICADO_PROPIEDAD if clave in nombre), "")


def _texto_menores(A):
    """Cómo sale cada menor Mᵢⱼ: se tacha la fila i y la columna j y se calcula el determinante que queda."""
    n = len(A)
    if n > 3:
        return ["Cada menor Mᵢⱼ es el determinante de la submatriz que queda al tachar la fila i y la columna j."]
    lineas = ["Cómo sale cada menor (se tacha la fila i y la columna j de A):"]
    for i in range(n):
        for j in range(n):
            sub = [[A[f][c] for c in range(n) if c != j] for f in range(n) if f != i]
            nombre = f"M{subindice(i + 1)}{subindice(j + 1)}"
            if len(sub) == 1:
                lineas.append(f"  {nombre} = {formatear_valor(sub[0][0])}")
            else:
                (a, b), (c, d) = sub
                valor = a * d - b * c
                lineas.append(f"  {nombre} = |{formatear_valor(a)} {formatear_valor(b)}; {formatear_valor(c)} "
                              f"{formatear_valor(d)}| = ({formatear_valor(a)})({formatear_valor(d)}) − "
                              f"({formatear_valor(b)})({formatear_valor(c)}) = {formatear_valor(valor)}")
    lineas.append("Cofactor: Cᵢⱼ = (−1)^(i+j) · Mᵢⱼ, es decir, se cambia el signo en las posiciones "
                  "donde i + j es impar (tablero + − +).")
    return lineas


def _texto_valor(valor):
    """Escribe una matriz en varias líneas (sangradas) o un número en una sola."""
    if isinstance(valor, list):
        return ["", *("        " + linea for linea in formatear_matriz(valor).splitlines())]
    return [f" {formatear_valor(valor)}"]


def _texto_propiedad(propiedad):
    """Líneas de una propiedad: sus dos miembros y «Se cumple» / «No se cumple» / «No aplica»."""
    significado = _significado(propiedad["nombre"])
    explicacion = [f"      Significa: {significado}"] if significado else []
    if propiedad["cumple"] is None:
        return [f"  • {propiedad['nombre']}:  No aplica. {propiedad['motivo']}", *explicacion]
    izquierda, derecha = _texto_valor(propiedad["izquierda"]), _texto_valor(propiedad["derecha"])
    veredicto = "Se cumple" if propiedad["cumple"] else "No se cumple"
    return ([f"  • {propiedad['nombre']}", *explicacion,
             "      Lado izquierdo:" + izquierda[0], *izquierda[1:],
             "      Lado derecho: " + derecha[0], *derecha[1:], f"      → {veredicto}"])
