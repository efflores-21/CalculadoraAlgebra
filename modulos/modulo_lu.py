"""
Pantalla del módulo de Factorización LU (A = LU) y solución de Ax = b.

Unidad II, Álgebra de matrices [P6]. Lee A (m×n) y b, muestra L, U,
la verificación L·U = A y, si A es cuadrada, las etapas Ly = b y Ux = y.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import customtkinter as ctk

from backend.factorizacion_lu import resolver_lu
from backend.matriz import subindice
from modulos._comun import (
    boton_primario, boton_secundario, crear_controles, crear_estructura,
    entrada_numero, etiqueta, formatear_matriz, formatear_vector, leer_entero,
    leer_fraccion, mensaje_error, reemplazar_texto, reiniciar_celdas, subtitulo,
)

LOGO = (
    "[ 1 0 0 ][ * * * ]  MÓDULO: FACTORIZACIÓN LU\n"
    "[ * 1 0 ][ 0 * * ]  A = LU   ·   Ly = b   ·   Ux = y\n"
    "[ * * 1 ][ 0 0 * ]"
)


class ModuloLU(ctk.CTkFrame):
    """Panel que factoriza A = LU y resuelve Ax = b por doble sustitución."""

    def __init__(self, master, on_back):
        """Construye la pantalla y una tabla inicial de 3 × 3."""
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A, self.entradas_b = [], []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Crea la guía, los campos m y n, la tabla [A | b] y los botones."""
        zonas = crear_estructura(
            self, self.on_back, numero=6, titulo="Factorización LU",
            descripcion="Factoriza A = LU y resuelve Ax = b en dos etapas: Ly = b y Ux = y.",
            logo=LOGO,
            pasos=[
                "Escribe las filas m y columnas n de A y pulsa «Crear tabla».",
                "Llena A y, en la última columna, el vector b (una componente por fila).",
                "Pulsa «Factorizar y resolver». Si A es cuadrada también se resuelve Ax = b.",
            ],
            clave_teoremas="lu",
            indicacion="Verás cada reemplazo de fila con su multiplicador, las matrices L y U, "
                       "la verificación L·U = A, las etapas Ly = b y Ux = y, y la comprobación A·x = b.",
        )
        self.resultado = zonas.resultado
        controles, entradas = crear_controles(
            zonas.contenido,
            [("m", "Filas m", "3", 80), ("n", "Columnas n", "3", 90)],
            self.actualizar_entradas,
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_m, self.entry_n = entradas["m"], entradas["n"]
        subtitulo(zonas.contenido, "Matriz A y vector b").pack(anchor="w", padx=10, pady=(18, 6))
        self.tabla = ctk.CTkFrame(zonas.contenido, fg_color="transparent")
        self.tabla.pack(anchor="w", padx=6)
        boton_primario(zonas.acciones, "Factorizar y resolver", self.calcular).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(side="left")

    def actualizar_entradas(self):
        """Valida m y n y construye las celdas de A (m×n) y de b (m componentes)."""
        try:
            m = leer_entero(self.entry_m, "El número de filas m")
            n = leer_entero(self.entry_n, "El número de columnas n")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.tabla.winfo_children():
            widget.destroy()
        for j in range(n):
            etiqueta(self.tabla, f"a{subindice(j + 1)}").grid(row=0, column=j, pady=(0, 2))
        etiqueta(self.tabla, "b", color="texto", negrita=True).grid(row=0, column=n, padx=(18, 0))
        self.entradas_A, self.entradas_b = [], []
        for i in range(m):
            fila = [entrada_numero(self.tabla) for _ in range(n)]
            for j, celda in enumerate(fila):
                celda.grid(row=i + 1, column=j, padx=3, pady=3)
            celda_b = entrada_numero(self.tabla)
            celda_b.grid(row=i + 1, column=n, padx=(18, 3), pady=3)
            self.entradas_A.append(fila)
            self.entradas_b.append(celda_b)
        reemplazar_texto(self.resultado, "")

    def calcular(self):
        """Lee A y b, llama a resolver_lu y muestra todo el procedimiento."""
        try:
            A = [[leer_fraccion(celda, f"La entrada ({i + 1},{j + 1}) de A") for j, celda in enumerate(fila)]
                 for i, fila in enumerate(self.entradas_A)]
            b = [leer_fraccion(celda, f"La componente {i + 1} de b") for i, celda in enumerate(self.entradas_b)]
            datos = resolver_lu(A, b)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)
            return
        lineas = _texto_factorizacion(A, datos) + _texto_solucion(datos)
        reemplazar_texto(self.resultado, "\n".join(lineas) + "\n", _resumen(datos))

    def limpiar(self):
        """Pone en cero A y b y vuelve a mostrar la guía."""
        reiniciar_celdas(self.entradas_A, self.entradas_b)
        reemplazar_texto(self.resultado, "")


def _texto_factorizacion(A, datos):
    """Devuelve las líneas de la reducción a U, las matrices L y U y la verificación L·U = A."""
    m, n = len(A), len(A[0])
    lineas = [f"FACTORIZACIÓN LU DE A ({m} × {n})", "A =", formatear_matriz(A), "",
              "1. Reducción a la forma escalonada U (solo reemplazos Fᵢ ← Fᵢ − l·Fⱼ):"]
    if not datos["pasos"]:
        lineas.append("   No hace falta ningún reemplazo: A ya está en forma escalonada.")
    for descripcion, matriz in datos["pasos"]:
        lineas.extend([f"   {descripcion}", formatear_matriz(matriz)])
    lineas.extend(["", f"L ({m} × {m}, triangular inferior con unos en la diagonal) =",
                   formatear_matriz(datos["L"]), "", f"U ({m} × {n}, forma escalonada) =",
                   formatear_matriz(datos["U"]), "", "2. Verificación: L · U =", formatear_matriz(datos["LU"]),
                   "La factorización es correcta (L · U == A)" if datos["factorizacion_correcta"]
                   else "La factorización NO es correcta (L · U ≠ A)"])
    return lineas


def _texto_pasos(titulo, etapa):
    """Devuelve las líneas de una reducción [matriz | vector] con sus operaciones de fila."""
    lineas = ["", titulo]
    for paso in etapa["pasos"]:
        lineas.extend([f"   {paso['descripcion']}", formatear_matriz(paso["matriz"])])
    return lineas


def _texto_solucion(datos):
    """Devuelve las líneas de las etapas Ly = b y Ux = y y de la comprobación A·x = b."""
    if not datos["cuadrada"]:
        return ["", "La solución de Ax = b por LU se calcula cuando A es cuadrada (n × n)."]
    lineas = _texto_pasos("3. Etapa 1: Ly = b (sustitución hacia adelante sobre [L | b])", datos["etapa_y"])
    lineas.append(f"y = {formatear_vector(datos['y'])}")
    lineas += _texto_pasos("4. Etapa 2: Ux = y (sustitución hacia atrás sobre [U | y])", datos["etapa_x"])
    if "x" not in datos:
        return lineas + [f"U tiene un cero en la diagonal: A es singular y Ax = b no tiene "
                         f"solución única ({datos['clase_x']['descripcion']})"]
    lineas.extend([f"x = {formatear_vector(datos['x'])}", "", "5. Comprobación: A · x =",
                   formatear_vector(datos["Ax"]),
                   "Comprobación exitosa: A · x == b" if datos["comprobacion"]
                   else "La comprobación falló: A · x ≠ b"])
    return lineas


def _resumen(datos):
    """Texto del recuadro negro con la respuesta final."""
    factorizacion = "L·U = A ✓" if datos["factorizacion_correcta"] else "L·U ≠ A"
    if not datos["cuadrada"]:
        return f"Factorización correcta:  {factorizacion}"
    if "x" not in datos:
        return f"{factorizacion}   ·   Ax = b no tiene solución única (A es singular)"
    return f"x = {formatear_vector(datos['x'])}   ·   {factorizacion}   ·   A·x = b ✓"
