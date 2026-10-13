"""
Pantalla del módulo de Factorización LU (A = LU) y solución de Ax = b.

Unidad II, Álgebra de matrices [P6]. Lee A (m×n) y b; sin pivoteo muestra L, U,
la verificación L·U = A y las etapas Ly = b y Ux = y; con pivoteo parcial usa PA = LU.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import customtkinter as ctk

from backend.factorizacion_lu import resolver_lu, resolver_sistema_lu
from backend.matriz import subindice
from backend.operaciones_matriciales import multiplicar_matrices
from modulos._comun import (
    Selector, boton_primario, boton_secundario, copiar_entradas_al_portapapeles,
    copiar_matriz_al_portapapeles, crear_controles, crear_estructura, entrada_numero,
    etiqueta, formatear_matriz, formatear_vector, leer_entero, leer_fraccion,
    mensaje_error, pegar_matriz_en_entradas, reemplazar_texto, reiniciar_celdas, subtitulo,
)

LOGO = (
    "[ 1 0 0 ][ * * * ]  MÓDULO: FACTORIZACIÓN LU\n"
    "[ * 1 0 ][ 0 * * ]  A = LU   ·   Ly = b   ·   Ux = y\n"
    "[ * * 1 ][ 0 0 * ]"
)
SIN_PIVOTEO, CON_PIVOTEO = "Sin pivoteo (A = LU)", "Pivoteo parcial (PA = LU)"


class ModuloLU(ctk.CTkFrame):
    """Panel que factoriza A = LU (o PA = LU) y resuelve Ax = b por doble sustitución."""

    def __init__(self, master, on_back):
        """Construye la pantalla y una tabla inicial de 3 × 3."""
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A, self.entradas_b = [], []
        self.ultima_L = self.ultima_U = None
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Crea la guía, los campos m y n, el método, la tabla [A | b] y los botones."""
        zonas = crear_estructura(
            self, self.on_back, numero=6, titulo="Factorización LU",
            descripcion="Factoriza A = LU (o PA = LU) y resuelve Ax = b en dos etapas: Ly = b y Ux = y.",
            logo=LOGO,
            pasos=[
                "Escribe las filas m y columnas n de A y pulsa «Crear tabla».",
                "Llena A y, en la última columna, el vector b (una componente por fila).",
                "Elige el método y pulsa «Factorizar y resolver». «Sin pivoteo» sigue A = LU solo con "
                "reemplazos; «Pivoteo parcial» permite intercambiar filas (PA = LU).",
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
        etiqueta(zonas.contenido, "Método").pack(anchor="w", padx=10, pady=(12, 2))
        self.selector_pivoteo = Selector(zonas.contenido, [SIN_PIVOTEO, CON_PIVOTEO])
        self.selector_pivoteo.pack(anchor="w", padx=10)
        subtitulo(zonas.contenido, "Matriz A y vector b").pack(anchor="w", padx=10, pady=(14, 6))
        self.tabla = ctk.CTkFrame(zonas.contenido, fg_color="transparent")
        self.tabla.pack(anchor="w", padx=6)
        portapapeles = ctk.CTkFrame(zonas.contenido, fg_color="transparent")
        portapapeles.pack(anchor="w", padx=10, pady=(8, 0))
        for texto, accion, ancho in (("Copiar A", self.copiar_A, 90), ("Pegar en A", self.pegar_A, 100),
                                     ("Copiar L", self.copiar_L, 90), ("Copiar U", self.copiar_U, 90)):
            boton_secundario(portapapeles, texto, accion, width=ancho).pack(side="left", padx=(0, 5))
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
        self.ultima_L = self.ultima_U = None
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
        """Lee A y b y muestra la factorización y la solución con el método elegido."""
        self.ultima_L = self.ultima_U = None
        try:
            A = [[leer_fraccion(celda, f"La entrada ({i + 1},{j + 1}) de A") for j, celda in enumerate(fila)]
                 for i, fila in enumerate(self.entradas_A)]
            b = [leer_fraccion(celda, f"La componente {i + 1} de b") for i, celda in enumerate(self.entradas_b)]
            if self.selector_pivoteo.get() == CON_PIVOTEO:
                lineas, resumen = self._con_pivoteo(A, b)
            else:
                lineas, resumen = self._sin_pivoteo(A, b)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)
            return
        reemplazar_texto(self.resultado, "\n".join(lineas) + "\n", resumen)

    def _sin_pivoteo(self, A, b):
        """A = LU solo con reemplazos de fila (lo que pide el programa) y solución de Ax = b."""
        datos = resolver_lu(A, b)
        self.ultima_L, self.ultima_U = datos["L"], datos["U"]
        lineas = _texto_factorizacion(A, datos)
        if datos["cuadrada"]:
            return lineas + _texto_solucion(datos), _resumen(datos)
        sistema = resolver_sistema_lu(A, b)
        return (lineas + ["", "3. Solución de Ax = b (A rectangular)"] + _texto_clasificacion(A, b, sistema),
                f"L·U = A ✓   ·   {_resumen_sistema(sistema)}")

    def _con_pivoteo(self, A, b):
        """P·A = L·U con pivoteo parcial; muestra cada paso registrado y clasifica Ax = b."""
        pasos = []
        sistema = resolver_sistema_lu(A, b, registrar_paso=pasos.append, pivoteo_parcial=True)
        P, L, U = sistema["P"], sistema["L"], sistema["U"]
        self.ultima_L, self.ultima_U = L, U
        lineas = ["FACTORIZACIÓN P·A = L·U CON PIVOTEO PARCIAL", "A =", formatear_matriz(A), "",
                  "Pasos (intercambios, multiplicadores y eliminación):"]
        lineas.extend(_texto_pasos_registrados(pasos))
        producto_LU, PA = multiplicar_matrices(L, U), multiplicar_matrices(P, A)
        lineas.extend(["", "P =", formatear_matriz(P), "L =", formatear_matriz(L), "U =", formatear_matriz(U),
                       "", "Verificación: L · U =", formatear_matriz(producto_LU),
                       "La factorización es correcta (L · U == P · A)" if producto_LU == PA
                       else "La factorización NO es correcta (L · U ≠ P · A)",
                       "", "Solución de Ax = b (Ly = Pb y Ux = y):"])
        lineas.extend(_texto_clasificacion(A, b, sistema))
        return lineas, f"P·A = L·U ✓   ·   {_resumen_sistema(sistema)}"

    def copiar_A(self):
        """Copia A al portapapeles (se puede pegar en Excel)."""
        copiar_entradas_al_portapapeles(self, self.entradas_A)

    def pegar_A(self):
        """Pega en A una matriz copiada (por ejemplo, desde Excel)."""
        pegar_matriz_en_entradas(self, self.entradas_A)

    def copiar_L(self):
        """Copia la última L calculada."""
        copiar_matriz_al_portapapeles(self, self.ultima_L)

    def copiar_U(self):
        """Copia la última U calculada."""
        copiar_matriz_al_portapapeles(self, self.ultima_U)

    def limpiar(self):
        """Pone en cero A y b y vuelve a mostrar la guía."""
        reiniciar_celdas(self.entradas_A, self.entradas_b)
        self.ultima_L = self.ultima_U = None
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


def _texto_pasos_registrados(pasos):
    """Convierte los pasos registrados por la factorización con traza en líneas de texto."""
    lineas = []
    for indice, paso in enumerate(pasos, 1):
        lineas.append(f"Paso {indice}: {paso['descripcion']}")
        if paso["mostrar_matrices"]:
            lineas.extend(["L =", formatear_matriz(paso["L"]), "U =", formatear_matriz(paso["U"])])
            if "P" in paso:
                lineas.extend(["P =", formatear_matriz(paso["P"])])
        if "vector" in paso:
            nombre, valores = paso["vector"]
            lineas.append(f"{nombre} = {formatear_vector(valores)}")
    return lineas


def _texto_clasificacion(A, b, sistema):
    """Líneas con y, la clasificación de Ax = b y su solución (particular más núcleo)."""
    lineas = [f"y = {formatear_vector(sistema['y'])}"]
    if sistema["estado"] == "incompatible":
        return lineas + ["Sistema incompatible: una fila cero de U corresponde a un valor no nulo de y."]
    x0 = sistema["solucion_particular"]
    lineas.append(("x = " if sistema["estado"] == "unica" else "x₀ = ") + formatear_vector(x0))
    if sistema["estado"] == "infinitas":
        libres = ", ".join(f"x{subindice(j + 1)}" for j in sistema["columnas_libres"])
        bases = " + ".join(f"t{subindice(k)}·{formatear_vector(v)}" for k, v in enumerate(sistema["bases_nucleo"], 1))
        lineas.extend([f"Infinitas soluciones; variables libres: {libres}.", f"x = x₀ + {bases}"])
    producto = [sum(A[i][j] * x0[j] for j in range(len(x0))) for i in range(len(A))]
    lineas.extend([f"A · x = {formatear_vector(producto)}",
                   "Comprobación exitosa: A · x == b" if sistema["verificacion"]
                   else "La comprobación falló: A · x ≠ b"])
    return lineas


def _resumen(datos):
    """Texto del recuadro negro con la respuesta final (método sin pivoteo, A cuadrada)."""
    factorizacion = "L·U = A ✓" if datos["factorizacion_correcta"] else "L·U ≠ A"
    if "x" not in datos:
        return f"{factorizacion}   ·   Ax = b no tiene solución única (A es singular)"
    return f"x = {formatear_vector(datos['x'])}   ·   {factorizacion}   ·   A·x = b ✓"


def _resumen_sistema(sistema):
    """Texto corto con la clasificación de Ax = b obtenida por la factorización con traza."""
    if sistema["estado"] == "incompatible":
        return "Ax = b no tiene solución"
    if sistema["estado"] == "unica":
        return f"x = {formatear_vector(sistema['solucion_particular'])}"
    return "Ax = b tiene infinitas soluciones"
