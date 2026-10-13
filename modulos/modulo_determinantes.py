"""Ventana independiente para calcular determinantes de matrices cuadradas."""

import customtkinter as ctk

from backend.matriz import formatear_valor
from backend.matrices import determinante_cofactores_con_pasos, determinante_triangular
from backend.operaciones_matriciales import suma_matrices
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
                "Expansión recursiva por cofactores:",
            ]
            for indice, (descripcion, estado) in enumerate(pasos_cofactores, 1):
                lineas.append(f"Paso {indice}: {descripcion}")
                if estado is not None:
                    lineas.append(formatear_matriz(estado))
            lineas.extend([
                f"Determinante por cofactores: {formatear_valor(determinante_cofactores)}",
                "",
                "Eliminación hacia forma triangular:",
            ])
            for indice, (descripcion, estado) in enumerate(pasos, 1):
                lineas.extend([
                    f"Paso {indice}: {descripcion}",
                    formatear_matriz(estado),
                ])
            lineas.extend([
                "",
                f"Determinante por triangulación: {formatear_valor(determinante)}",
                "Comparación de métodos: " + (
                    "coinciden" if determinante_cofactores == determinante
                    else "NO coinciden"
                ),
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
