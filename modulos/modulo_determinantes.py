"""
Pantalla del módulo de determinantes por eliminación triangular.

Unidad II, Determinantes [P5].
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import customtkinter as ctk
from fractions import Fraction

from backend.matriz import formatear_valor
from backend.matrices import determinante_cofactores_con_pasos, determinante_triangular
from backend.operaciones_matriciales import LIMITE_COFACTORES, suma_matrices
from modulos._comun import (
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    copiar_entradas_al_portapapeles,
    copiar_matriz_al_portapapeles,
    entrada_numero,
    formatear_matriz,
    leer_entero,
    leer_fraccion,
    mensaje_error,
    pegar_matriz_en_entradas,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
)


def _texto_pasos_cofactores(pasos):
    """Presenta en orden los menores, cofactores y términos registrados."""
    lineas = []
    for indice, (descripcion, estado) in enumerate(pasos, 1):
        lineas.append(f"Paso {indice}: {descripcion}")
        if estado is not None:
            lineas.append(formatear_matriz(estado))
    return lineas


def _texto_traza_triangular(pasos):
    """Explica cada estado de la triangularización sin inventar operaciones."""
    if not pasos:
        return []

    descripcion_inicial, estado_anterior = pasos[0]
    lineas = [
        "Reducimos A a forma triangular para obtener el determinante desde su diagonal.",
        "Restar a una fila un múltiplo de otra conserva el determinante; "
        "cada intercambio de filas cambia su signo.",
        f"Estado inicial: {descripcion_inicial}",
        formatear_matriz(estado_anterior),
    ]
    signo = 1

    for descripcion, estado in pasos[1:]:
        if descripcion.startswith("Intercambiar F"):
            intercambio = descripcion.removeprefix("Intercambiar F").split(";", 1)[0]
            partes = intercambio.split(" y F")
            fila_1, fila_2 = int(partes[0]) - 1, int(partes[1]) - 1
            signo *= -1
            lineas.extend([
                f"Operación: {descripcion}",
                "Antes del intercambio:",
                formatear_matriz(estado_anterior),
                f"F{fila_1 + 1} y F{fila_2 + 1} intercambian todas sus entradas. "
                f"Este intercambio invierte el signo; signo acumulado = {signo:+d}.",
                "Después del intercambio:",
                formatear_matriz(estado),
            ])
        elif descripcion.startswith("Pivote "):
            columna = int(descripcion.split()[1].rstrip(":")) - 1
            pivote = estado[columna][columna]
            lineas.extend([
                f"{descripcion} Se usa para anular las entradas inferiores de "
                "esta columna; no altera la matriz ni el determinante.",
                formatear_matriz(estado),
            ])
        elif " <- " in descripcion:
            destino, lado_derecho = descripcion.split(" <- ", 1)
            fila_destino = int(destino.removeprefix("F")) - 1
            fila_pivote = int(lado_derecho.rsplit("F", 1)[1].rstrip(".")) - 1
            columna_pivote = fila_pivote
            pivote = estado_anterior[fila_pivote][columna_pivote]
            factor = estado_anterior[fila_destino][columna_pivote] / pivote
            lineas.extend([
                f"Operación: {descripcion}",
                f"El pivote es {formatear_valor(pivote)} en F{fila_pivote + 1}; "
                f"el multiplicador es {formatear_valor(factor)}. "
                "Se busca hacer cero la entrada bajo el pivote.",
                "Antes de la operación:",
                formatear_matriz(estado_anterior),
            ])
            for columna in range(columna_pivote, len(estado[fila_destino])):
                antes = estado_anterior[fila_destino][columna]
                base = estado_anterior[fila_pivote][columna]
                despues = estado[fila_destino][columna]
                if antes != despues:
                    calculado = antes - factor * base
                    lineas.append(
                        f"  Entrada ({fila_destino + 1},{columna + 1}): "
                        f"{formatear_valor(antes)} - "
                        f"({formatear_valor(factor)})({formatear_valor(base)}) "
                        f"= {formatear_valor(calculado)}"
                    )
                    if calculado != despues:
                        lineas.append(
                            "  Aviso: este cálculo no coincide con el estado "
                            f"registrado ({formatear_valor(despues)})."
                        )
            lineas.extend([
                "Después de la operación:",
                formatear_matriz(estado),
                "Esta operación conserva el determinante.",
            ])
        elif descripcion.startswith("No hay pivote"):
            lineas.extend([
                descripcion,
                "La matriz queda con una columna sin pivote y es singular; "
                "por ello det(A) = 0.",
                formatear_matriz(estado),
            ])
        elif descripcion.startswith("Diagonal final"):
            diagonal = [estado[i][i] for i in range(len(estado))]
            producto = Fraction(1)
            for valor in diagonal:
                producto *= valor
            lineas.extend([
                descripcion,
                formatear_matriz(estado),
                "En una matriz triangular, el determinante es el producto de "
                f"la diagonal: {formatear_valor(producto)}; se aplica el signo "
                f"acumulado ({signo:+d}) de los intercambios.",
            ])
        else:
            lineas.extend([descripcion, formatear_matriz(estado)])
        estado_anterior = estado

    return lineas


def _texto_sarrus(A):
    """Desarrolla los seis productos y las dos sumas de Sarrus para una 3×3."""
    if len(A) != 3 or any(len(fila) != 3 for fila in A):
        raise ValueError("La regla de Sarrus solo se aplica a matrices 3×3.")

    a, b, c = A[0]
    d, e, f = A[1]
    g, h, i = A[2]
    descendentes = [a * e * i, b * f * g, c * d * h]
    ascendentes = [c * e * g, b * d * i, a * f * h]
    suma_descendente = sum(descendentes, Fraction(0))
    suma_ascendente = sum(ascendentes, Fraction(0))
    resultado = suma_descendente - suma_ascendente
    descendentes_texto = [
        f"a₁₁a₂₂a₃₃ = ({formatear_valor(a)})({formatear_valor(e)})"
        f"({formatear_valor(i)}) = {formatear_valor(descendentes[0])}",
        f"a₁₂a₂₃a₃₁ = ({formatear_valor(b)})({formatear_valor(f)})"
        f"({formatear_valor(g)}) = {formatear_valor(descendentes[1])}",
        f"a₁₃a₂₁a₃₂ = ({formatear_valor(c)})({formatear_valor(d)})"
        f"({formatear_valor(h)}) = {formatear_valor(descendentes[2])}",
    ]
    ascendentes_texto = [
        f"a₁₃a₂₂a₃₁ = ({formatear_valor(c)})({formatear_valor(e)})"
        f"({formatear_valor(g)}) = {formatear_valor(ascendentes[0])}",
        f"a₁₂a₂₁a₃₃ = ({formatear_valor(b)})({formatear_valor(d)})"
        f"({formatear_valor(i)}) = {formatear_valor(ascendentes[1])}",
        f"a₁₁a₂₃a₃₂ = ({formatear_valor(a)})({formatear_valor(f)})"
        f"({formatear_valor(h)}) = {formatear_valor(ascendentes[2])}",
    ]
    return [
        "Regla de Sarrus (solo para matrices de orden 3):",
        "Diagonales descendentes:",
        *descendentes_texto,
        "Suma descendente = "
        + " + ".join(formatear_valor(valor) for valor in descendentes)
        + f" = {formatear_valor(suma_descendente)}",
        "Diagonales ascendentes:",
        *ascendentes_texto,
        "Suma ascendente = "
        + " + ".join(formatear_valor(valor) for valor in ascendentes)
        + f" = {formatear_valor(suma_ascendente)}",
        f"det(A) por Sarrus = {formatear_valor(suma_descendente)} - "
        f"{formatear_valor(suma_ascendente)} = {formatear_valor(resultado)}",
    ], resultado


def determinante_con_pasos(A):
    """
    Conserva la API de la interfaz y delega el algoritmo al backend.
    """
    return determinante_triangular(A)


def comparar_determinante_suma(A, B):
    """Compara det(A+B) con det(A)+det(B) usando aritmética exacta."""
    suma = suma_matrices(A, B)
    determinante_a, _ = determinante_triangular(A)
    determinante_b, _ = determinante_triangular(B)
    determinante_suma, _ = determinante_triangular(suma)
    suma_determinantes = determinante_a + determinante_b
    return {
        "suma": suma,
        "det_a": determinante_a,
        "det_b": determinante_b,
        "det_suma": determinante_suma,
        "suma_determinantes": suma_determinantes,
        "coinciden": determinante_suma == suma_determinantes,
    }


class ModuloDeterminantes(ctk.CTkFrame):
    """Permite ingresar una matriz cuadrada y analizar su determinante en el panel principal."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas = []
        self.ultima_matriz_resultado = None
        self.entradas_A_suma = []
        self.entradas_B_suma = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Crea la pantalla, su logotipo, el control de orden y las acciones."""
        zonas = crear_estructura(
            self,
            self.on_back,
            numero=5,
            titulo="Determinantes",
            descripcion="Calcula det(A) paso a paso y dice si A tiene inversa.",
            logo=(
                "+---------+\n"
                "| det(A)  |  MÓDULO: DETERMINANTES\n"
                "+---------+  Pivotes, intercambios de fila y valor exacto"
            ),
            pasos=[
                "Escribe el tamaño n de tu matriz cuadrada (n × n) y pulsa "
                "«Crear tabla».",
                "Llena la matriz A fila por fila.",
                "Pulsa «Calcular determinante».",
            ],
            clave_teoremas="determinantes",
            indicacion="Aquí verás la eliminación hasta la forma triangular, "
                       "los pivotes, el valor de det(A) y si A es invertible.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido

        controles, entradas = crear_controles(
            contenido, [("n", "Tamaño n", "2", 90)], self.actualizar_entradas
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_n = entradas["n"]

        subtitulo(contenido, "Matriz A").pack(anchor="w", padx=10, pady=(20, 6))
        self.tabla = ctk.CTkFrame(contenido, fg_color="transparent")
        self.tabla.pack(anchor="w", padx=6)
        portapapeles = ctk.CTkFrame(contenido, fg_color="transparent")
        portapapeles.pack(anchor="w", padx=10, pady=(8, 0))
        boton_secundario(
            portapapeles, "Copiar A", self.copiar_entrada, width=90
        ).pack(side="left", padx=(0, 6))
        boton_secundario(
            portapapeles, "Pegar en A", self.pegar_entrada, width=100
        ).pack(side="left", padx=(0, 6))
        boton_secundario(
            portapapeles, "Copiar triangular", self.copiar_resultado, width=140
        ).pack(side="left")

        subtitulo(contenido, "Contraejemplo: det(A+B) y det(A)+det(B)").pack(
            anchor="w", padx=10, pady=(22, 6)
        )
        etiqueta_ejemplo = ctk.CTkLabel(
            contenido,
            text="Compara ambos valores; el ejemplo inicial muestra que no son iguales en general.",
            anchor="w",
        )
        etiqueta_ejemplo.pack(anchor="w", padx=10, pady=(0, 6))
        panel_ejemplo = ctk.CTkFrame(contenido, fg_color="transparent")
        panel_ejemplo.pack(anchor="w", padx=6)
        panel_a = ctk.CTkFrame(panel_ejemplo, fg_color="transparent")
        panel_b = ctk.CTkFrame(panel_ejemplo, fg_color="transparent")
        panel_a.pack(side="left", anchor="nw", padx=4)
        panel_b.pack(side="left", anchor="nw", padx=12)
        subtitulo(panel_a, "Matriz A (2 × 2)").pack(anchor="w", padx=4, pady=(4, 2))
        subtitulo(panel_b, "Matriz B (2 × 2)").pack(anchor="w", padx=4, pady=(4, 2))
        self.entradas_A_suma = self._crear_entradas_2x2(
            panel_a, [[1, 0], [0, 0]]
        )
        self.entradas_B_suma = self._crear_entradas_2x2(
            panel_b, [[0, 0], [0, 1]]
        )
        acciones_ejemplo = ctk.CTkFrame(contenido, fg_color="transparent")
        acciones_ejemplo.pack(anchor="w", padx=10, pady=(6, 0))
        boton_primario(
            acciones_ejemplo, "Comparar determinantes", self.comparar_suma, width=190
        ).pack(side="left", padx=(0, 6))
        boton_secundario(
            acciones_ejemplo, "Restaurar ejemplo", self.restaurar_ejemplo, width=150
        ).pack(side="left")

        boton_primario(zonas.acciones, "Calcular determinante", self.calcular).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(
            side="left"
        )

    def actualizar_entradas(self):
        """Construye una cuadrícula n por n para representar una matriz cuadrada."""
        try:
            n = leer_entero(self.entry_n, "El orden n")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.tabla.winfo_children():
            widget.destroy()
        self.entradas = []
        self.ultima_matriz_resultado = None
        for i in range(n):
            fila = []
            for j in range(n):
                entry = entrada_numero(self.tabla)
                entry.grid(row=i, column=j, padx=4, pady=4)
                fila.append(entry)
            self.entradas.append(fila)
        reemplazar_texto(self.resultado, "")

    def calcular(self):
        """Lee A y muestra pivotes, operaciones de fila y el valor de det(A)."""
        self.ultima_matriz_resultado = None
        try:
            matriz = [
                [
                    leer_fraccion(entry, f"La entrada ({i + 1},{j + 1}) de A")
                    for j, entry in enumerate(fila)
                ]
                for i, fila in enumerate(self.entradas)
            ]
            determinante_cofactores = None
            pasos_cofactores = []
            if len(matriz) <= LIMITE_COFACTORES:
                determinante_cofactores, pasos_cofactores = (
                    determinante_cofactores_con_pasos(matriz)
                )
            determinante, pasos = determinante_con_pasos(matriz)
            self.ultima_matriz_resultado = pasos[-1][1]
            lineas = [
                "MODULO 5 | CALCULO DEL DETERMINANTE",
                "=" * 56,
                "Matriz A:",
                formatear_matriz(matriz),
                "",
            ]
            if determinante_cofactores is None:
                lineas.extend([
                    f"Expansión por cofactores omitida: el límite de presentación "
                    f"es n = {LIMITE_COFACTORES} por su costo recursivo.",
                ])
            else:
                lineas.append("Expansión recursiva por cofactores:")
                lineas.extend(_texto_pasos_cofactores(pasos_cofactores))
                lineas.append(
                    "Determinante por cofactores: "
                    f"{formatear_valor(determinante_cofactores)}"
                )
            lineas.extend([
                "",
                "Eliminación hacia forma triangular:",
                *_texto_traza_triangular(pasos),
            ])
            sarrus = None
            if len(matriz) == 3:
                texto_sarrus, sarrus = _texto_sarrus(matriz)
                lineas.extend(["", *texto_sarrus])
            lineas.extend([
                "",
                f"Determinante por triangulación: {formatear_valor(determinante)}",
            ])
            if determinante_cofactores is not None:
                lineas.append("Triangularización y cofactores: " + (
                    "coinciden" if determinante_cofactores == determinante
                    else "NO coinciden"
                ))
            if sarrus is not None:
                lineas.append("Triangularización y Sarrus: " + (
                    "coinciden" if sarrus == determinante
                    else "NO coinciden"
                ))
            lineas.extend([
                "A es invertible." if determinante != 0 else "A es singular; no tiene inversa.",
            ])
            resumen = f"det(A) = {formatear_valor(determinante)}   ·   " + (
                "A es invertible" if determinante != 0 else "A es singular (no tiene inversa)"
            )
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n", resumen)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    @staticmethod
    def _crear_entradas_2x2(parent, valores):
        """Crea una cuadrícula 2×2 inicializada con valores editables."""
        tabla = ctk.CTkFrame(parent, fg_color="transparent")
        tabla.pack(anchor="w")
        entradas = []
        for i, fila_valores in enumerate(valores):
            fila = []
            for j, valor in enumerate(fila_valores):
                celda = entrada_numero(tabla)
                celda.grid(row=i, column=j, padx=3, pady=3)
                celda.insert(0, str(valor))
                fila.append(celda)
            entradas.append(fila)
        return entradas

    def restaurar_ejemplo(self):
        """Restaura las matrices 2×2 del contraejemplo solicitado."""
        for entradas, valores in (
            (self.entradas_A_suma, [[1, 0], [0, 0]]),
            (self.entradas_B_suma, [[0, 0], [0, 1]]),
        ):
            for i, fila in enumerate(entradas):
                for j, celda in enumerate(fila):
                    celda.delete(0, "end")
                    celda.insert(0, str(valores[i][j]))

    def comparar_suma(self):
        """Muestra A, B, A+B y compara los determinantes exactos."""
        try:
            matriz_a = [
                [leer_fraccion(celda, f"La entrada ({i + 1},{j + 1}) de A")
                 for j, celda in enumerate(fila)]
                for i, fila in enumerate(self.entradas_A_suma)
            ]
            matriz_b = [
                [leer_fraccion(celda, f"La entrada ({i + 1},{j + 1}) de B")
                 for j, celda in enumerate(fila)]
                for i, fila in enumerate(self.entradas_B_suma)
            ]
            datos = comparar_determinante_suma(matriz_a, matriz_b)
            lineas = [
                "Contraejemplo de aditividad del determinante:",
                "A =", formatear_matriz(matriz_a),
                "B =", formatear_matriz(matriz_b),
                "A + B =", formatear_matriz(datos["suma"]),
                f"det(A+B) = {formatear_valor(datos['det_suma'])}",
                f"det(A) = {formatear_valor(datos['det_a'])}",
                f"det(B) = {formatear_valor(datos['det_b'])}",
                "det(A) + det(B) = "
                f"{formatear_valor(datos['det_a'])} + "
                f"{formatear_valor(datos['det_b'])} = "
                f"{formatear_valor(datos['suma_determinantes'])}",
            ]
            if datos["coinciden"]:
                conclusion = (
                    "Para estas matrices coinciden; este caso no muestra una desigualdad. "
                    "En general, det(A+B) no siempre es det(A)+det(B)."
                )
            else:
                conclusion = (
                    "Contraejemplo: det(A+B) ≠ det(A)+det(B); por tanto, "
                    "el determinante no es aditivo en general."
                )
            lineas.append("Conclusión: " + conclusion)
            reemplazar_texto(
                self.resultado,
                "\n".join(lineas) + "\n",
                f"det(A+B) = {formatear_valor(datos['det_suma'])}; "
                f"det(A)+det(B) = {formatear_valor(datos['suma_determinantes'])}",
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        """Reinicia a cero todas las entradas de la matriz."""
        reiniciar_celdas(self.entradas, self.entradas_A_suma, self.entradas_B_suma)
        self.ultima_matriz_resultado = None
        reemplazar_texto(self.resultado, "")

    def copiar_entrada(self):
        copiar_entradas_al_portapapeles(self, self.entradas)

    def pegar_entrada(self):
        pegar_matriz_en_entradas(self, self.entradas)

    def copiar_resultado(self):
        copiar_matriz_al_portapapeles(self, self.ultima_matriz_resultado)
