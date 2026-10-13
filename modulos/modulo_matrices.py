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
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    resta_matrices,
    suma_matrices,
    transponer_matriz,
)
from backend.verificador import LIMITE_COFACTORES, verificar_propiedades_matrices
from modulos._comun import (
    boton_primario, boton_secundario, copiar_entradas_al_portapapeles,
    copiar_matriz_al_portapapeles, crear_controles, crear_estructura, entrada_numero,
    formatear_matriz, leer_entero, leer_fraccion, matriz_en_linea, mensaje_error,
    mostrar_teoremas, pegar_matriz_en_entradas, reemplazar_texto, reiniciar_celdas, subtitulo,
)

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
            clave_teoremas="matrices",
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
        return (["A + B, entrada a entrada:"] + _detalle_entradas(A, B, C, "+")
                + ["", f"A + B ({len(C)} × {len(C[0])}) =", formatear_matriz(C)],
                f"A + B = {matriz_en_linea(C)}")

    def _resta(self, A):
        """Opción 2: A − B entrada a entrada."""
        B = self._leer_matriz(self.entradas_B, "B")
        C = resta_matrices(A, B)
        self.ultima_matriz_resultado = C
        return (["A − B, entrada a entrada:"] + _detalle_entradas(A, B, C, "−")
                + ["", f"A − B ({len(C)} × {len(C[0])}) =", formatear_matriz(C)],
                f"A − B = {matriz_en_linea(C)}")

    def _escalar(self, A):
        """Opción 3: k · A, multiplicando cada entrada por k."""
        k = leer_fraccion(self.entry_escalar, "El escalar k")
        C = multiplicar_escalar_matriz(k, A)
        self.ultima_matriz_resultado = C
        detalle = [f"c{subindice(i + 1)},{subindice(j + 1)} = {formatear_valor(k)} · {formatear_valor(A[i][j])} "
                   f"= {formatear_valor(C[i][j])}" for i in range(len(A)) for j in range(len(A[0]))]
        return ([f"k = {formatear_valor(k)}; cada entrada de A se multiplica por k:"] + detalle
                + ["", f"k · A ({len(C)} × {len(C[0])}) =", formatear_matriz(C)],
                f"k · A = {matriz_en_linea(C)}")

    def _producto(self, A):
        """Opción 4: A · B, cada entrada es el producto punto de una fila de A por una columna de B."""
        B = self._leer_matriz(self.entradas_B, "B")
        C = multiplicar_matrices(A, B)
        self.ultima_matriz_resultado = C
        lineas = ["A · B: cada entrada es el producto punto de una fila de A por una columna de B."]
        for i in range(len(A)):
            for j in range(len(B[0])):
                productos = " + ".join(f"({formatear_valor(A[i][t])})({formatear_valor(B[t][j])})"
                                       for t in range(len(A[0])))
                lineas.append(f"c{subindice(i + 1)},{subindice(j + 1)} = {productos} = {formatear_valor(C[i][j])}")
        lineas.extend(["", f"A · B ({len(C)} × {len(C[0])}) =", formatear_matriz(C)])
        return lineas, f"A · B = {matriz_en_linea(C)}"

    def _transpuesta(self, A):
        """Opción 5: Aᵀ, las filas de A pasan a ser columnas."""
        C = transponer_matriz(A)
        self.ultima_matriz_resultado = C
        return (["Transpuesta: las filas de A pasan a ser columnas.", "A =", formatear_matriz(A), "",
                 f"Aᵀ ({len(C)} × {len(C[0])}) =", formatear_matriz(C)], f"Aᵀ = {matriz_en_linea(C)}")

    def _determinante(self, A):
        """Opción 6: det(A) por triangularización, cofactores y (en 3 × 3) Sarrus."""
        det_A, pasos = determinante_triangular(A)
        lineas = ["DETERMINANTE", "", "Reducción a forma triangular (método eficiente):"]
        for descripcion, estado in pasos:
            lineas.extend([f"   {descripcion}", formatear_matriz(estado)])
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
            lineas.append(f"det(A) por Sarrus = {formatear_valor(det_sarrus)}"
                          f"   →   {'coincide' if det_sarrus == det_A else 'NO coincide'}")
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
            titulo, otro = "Inversa por matriz adjunta: A⁻¹ = (1/det(A)) · adj(A)", "Gauss-Jordan"
        else:
            inversa, pasos = invertir_gauss_jordan(A)
            titulo, otro = "Inversa por Gauss-Jordan: [A | I] → [I | A⁻¹]", "adjunta"
        lineas = [titulo]
        for indice, (descripcion, matriz_paso) in enumerate(pasos, 1):
            lineas.extend([f"Paso {indice}: {descripcion}", formatear_matriz(matriz_paso)])
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

    def limpiar(self):
        """Pone en cero A, B, C y el escalar, y vuelve a mostrar la guía."""
        reiniciar_celdas(self.entradas_A, self.entradas_B, self.entradas_C, [self.entry_escalar])
        self.ultima_matriz_resultado = None
        reemplazar_texto(self.resultado, "")


def _texto_valor(valor):
    """Escribe una matriz en varias líneas (sangradas) o un número en una sola."""
    if isinstance(valor, list):
        return ["", *("        " + linea for linea in formatear_matriz(valor).splitlines())]
    return [f" {formatear_valor(valor)}"]


def _texto_propiedad(propiedad):
    """Líneas de una propiedad: sus dos miembros y «Se cumple» / «No se cumple» / «No aplica»."""
    if propiedad["cumple"] is None:
        return [f"  • {propiedad['nombre']}:  No aplica. {propiedad['motivo']}"]
    izquierda, derecha = _texto_valor(propiedad["izquierda"]), _texto_valor(propiedad["derecha"])
    veredicto = "Se cumple" if propiedad["cumple"] else "No se cumple"
    return ([f"  • {propiedad['nombre']}", "      Lado izquierdo:" + izquierda[0], *izquierda[1:],
             "      Lado derecho: " + derecha[0], *derecha[1:], f"      → {veredicto}"])
