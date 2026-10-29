"""
Pantalla del módulo de Factorización LU (A = LU) y solución de Ax = b.

Unidad II, Álgebra de matrices [P6]. Lee A (m×n) y b; sin pivoteo muestra L, U,
la verificación L·U = A y las etapas Ly = b y Ux = y; con pivoteo parcial usa PA = LU.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import customtkinter as ctk

from backend.factorizacion_lu import resolver_lu, resolver_sistema_lu
from backend.matriz import formatear_valor, subindice
from backend.operaciones_matriciales import multiplicar_matrices

from modulos._comun import (
    llenar,
    Selector, boton_primario, boton_secundario, copiar_entradas_al_portapapeles,
    copiar_matriz_al_portapapeles, crear_controles, crear_estructura, entrada_numero,
    etiqueta, formatear_matriz, formatear_vector, leer_entero, leer_fraccion,
    formatear_paso_explicado, mensaje_error, pegar_matriz_en_entradas, reemplazar_texto, reiniciar_celdas, subtitulo,
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
            clave_teoremas="lu", ejemplo=self.cargar_ejemplo,
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
            # Fracciones exactas: así L·U == A y A·x == b se comparan sin errores de redondeo.
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
            
        # Con A rectangular Ux = y no tiene solución única garantizada: se clasifica el sistema.
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
        lineas.extend(_texto_pasos_registrados(pasos, estado_final={"P": P, "L": L, "U": U}))
        producto_LU, PA = multiplicar_matrices(L, U), multiplicar_matrices(P, A)
        lineas.extend(["", "P =", formatear_matriz(P), "L =", formatear_matriz(L), "U =", formatear_matriz(U),
                       "", "Comparación para verificar PA = LU:", "P · A =", formatear_matriz(PA),
                       "L · U =", formatear_matriz(producto_LU),
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

    def cargar_ejemplo(self):
        """Carga un sistema de 3 × 3 y lo resuelve con A = LU."""
        llenar([self.entry_m, self.entry_n], [3, 3])
        self.actualizar_entradas()
        for fila, valores in zip(self.entradas_A, [[2, 1, 1], [4, -6, 0], [-2, 7, 2]]):
            llenar(fila, valores)
        llenar(self.entradas_b, [5, -2, 9])
        self.selector_pivoteo.set(SIN_PIVOTEO)
        self.calcular()

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
    if datos["pasos"]:
        lineas.append("   Traza técnica:")
        for indice, (descripcion, matriz) in enumerate(datos["pasos"], 1):
            lineas.append(f"   {indice}. {descripcion}")
            if matriz != datos["U"]:
                lineas.append(formatear_matriz(matriz))
    else:
        lineas.append("   No se aplicó ninguna operación de eliminación.")
    explicaciones = datos.get("pasos_explicados", [])
    if explicaciones:
        lineas.append("   Explicación pedagógica:")
        for indice, paso in enumerate(explicaciones, 1):
            lineas.append(f"   Paso {indice}:")
            lineas.extend("   " + texto for texto in formatear_paso_explicado(paso, incluir_estado=False))
    lineas.extend(["", f"L ({m} × {m}, triangular inferior con unos en la diagonal) =",
                   formatear_matriz(datos["L"]), "", f"U ({m} × {n}, forma escalonada) =",
                   formatear_matriz(datos["U"]), "", "Construcción: la diagonal de L es 1 y cada lᵢₖ guarda el multiplicador usado para anular la entrada inferior correspondiente.",
                   "2. Verificación: L · U reconstruye A porque L conserva esos multiplicadores; L · U =", formatear_matriz(datos["LU"]),
                   "La factorización es correcta (L · U == A)" if datos["factorizacion_correcta"]
                   else "La factorización NO es correcta (L · U ≠ A)"])
    return lineas


def _texto_pasos(titulo, etapa):
    """Presenta la traza técnica sin volver a imprimir estados idénticos."""
    lineas = ["", titulo, "Traza técnica:"]
    matriz_anterior = None
    total = len(etapa["pasos"])
    for indice, paso in enumerate(etapa["pasos"]):
        lineas.append(f"   {paso['descripcion']}")
        matriz = paso["matriz"]
        es_estado_final = total > 1 and indice == total - 1
        if matriz != matriz_anterior and not es_estado_final:
            lineas.append(formatear_matriz(matriz))
            matriz_anterior = matriz
    return lineas


def _texto_solucion(datos):
    """Devuelve las líneas de las etapas Ly = b y Ux = y y de la comprobación A·x = b."""
    lineas = _texto_pasos("3. Etapa 1: Ly = b (sustitución hacia adelante sobre [L | b])", datos["etapa_y"])
    lineas.append("Explicación pedagógica: como L es triangular inferior con diagonal unitaria, se despeja y en orden ascendente.")
    lineas.extend(_ecuaciones_triangulares(datos["L"], datos["b"], datos["y"], "y", True))
    lineas.append(f"Resultado intermedio: y = {formatear_vector(datos['y'])}")
    lineas += _texto_pasos("4. Etapa 2: Ux = y (sustitución hacia atrás sobre [U | y])", datos["etapa_x"])
    lineas.append("Explicación pedagógica: como U es triangular superior, se despeja x desde la última fila hacia arriba.")
    if "x" in datos:
        lineas.extend(_ecuaciones_triangulares(datos["U"], datos["y"], datos["x"], "x", False))
    if "x" not in datos:
        return lineas + [f"U tiene un cero en la diagonal: A es singular y Ax = b no tiene "
                         f"solución única ({datos['clase_x']['descripcion']})"]
    lineas.extend(["Resultado final:", f"x = {formatear_vector(datos['x'])}", "", "5. Comprobación: A · x =",
                   formatear_vector(datos["Ax"]),
                   "Comprobación exitosa: A · x == b" if datos["comprobacion"]
                   else "La comprobación falló: A · x ≠ b"])
    return lineas


def _texto_pasos_registrados(pasos, estado_final=None):
    """Convierte los pasos registrados por la factorización con traza en líneas de texto."""
    pasos_visibles = [
        paso for paso in pasos
        if not paso["objetivo"].startswith(("Cerrar la eliminación", "Comprobar que la solución particular",
                                            "Calcular y_", "Despejar x_", "Determinar si el sistema triangular"))
    ]
    lineas = ["Matrices de estado (solo cuando cambian):"]
    anterior = None
    for indice, paso in enumerate(pasos_visibles, 1):
        if paso["mostrar_matrices"]:
            for nombre in ("P", "L", "U"):
                if (nombre in paso and (anterior is None or paso[nombre] != anterior.get(nombre))
                        and (estado_final is None or paso[nombre] != estado_final.get(nombre))):
                    lineas.extend([f"{nombre} =", formatear_matriz(paso[nombre])])
        if "vector" in paso:
            nombre, valores = paso["vector"]
            if nombre == "Pb":
                lineas.append(f"{nombre} = {formatear_vector(valores)}")
        anterior = paso
    lineas.append("\nDETALLE DE LOS PASOS")
    pivote_fundamento_mostrado = False
    for indice, paso in enumerate(pasos_visibles):
        lineas.append(f"Paso {indice + 1}: {paso['descripcion']}")
        detalle = formatear_paso_explicado(paso, incluir_estado=False)
        es_pivote = "Pivote de la etapa" in paso["descripcion"]
        if es_pivote and pivote_fundamento_mostrado:
            detalle = [texto for texto in detalle if not texto.startswith("Fundamento:")]
        lineas.extend("   " + texto for texto in detalle if not texto.startswith("Objetivo:"))
        pivote_fundamento_mostrado = pivote_fundamento_mostrado or es_pivote
        if es_pivote:
            posteriores = pasos_visibles[indice + 1:]
            siguientes_etapa = []
            for siguiente in posteriores:
                if "Pivote de la etapa" in siguiente["descripcion"]:
                    break
                siguientes_etapa.append(siguiente)
            sin_eliminacion = not any("Multiplicador" in siguiente["descripcion"]
                                      for siguiente in siguientes_etapa)
            if sin_eliminacion:
                lineas.append("   Eliminación: no se requiere; no hay entradas no nulas debajo del pivote.")
    return lineas


def _formatear_paso_lu(paso, fundamento_pivote_mostrado=False):
    """Renderiza el detalle sin repetir el criterio de selección de pivote."""
    lineas = formatear_paso_explicado(paso, incluir_estado=False)
    if fundamento_pivote_mostrado and "Pivote de la etapa" in paso["descripcion"]:
        lineas = [linea for linea in lineas if not linea.startswith("Fundamento:")]
    return lineas


def _ecuaciones_triangulares(matriz, rhs, solucion, variable, adelante):
    """Muestra la ecuación de cada fila y su sustitución numérica exacta."""
    filas = range(len(matriz)) if adelante else range(len(matriz) - 1, -1, -1)
    lineas = ["Ecuación de fila y sustitución:"]
    for i in filas:
        pivote_col = i if adelante else next((j for j, v in enumerate(matriz[i]) if v != 0), None)
        if pivote_col is None or pivote_col >= len(matriz[i]):
            lineas.append(f"   Fila {i + 1}: no tiene variable pivote; se usa para clasificar el sistema.")
            continue
        cols = range(pivote_col) if adelante else range(pivote_col + 1, len(matriz[i]))
        terminos = [(j, matriz[i][j]) for j in cols]
        suma = sum(matriz[i][j] * solucion[j] for j, _ in terminos)
        expresion = " + ".join(f"({formatear_valor(a)})·{variable}{j + 1}" for j, a in terminos) or "0"
        sustitucion = " + ".join(f"({formatear_valor(a)})({formatear_valor(solucion[j])})" for j, a in terminos) or "0"
        if adelante:
            valor = rhs[i] - suma
            lineas.append(f"   {formatear_valor(matriz[i][pivote_col])}·{variable}{pivote_col + 1} + {expresion} = {formatear_valor(rhs[i])}; {variable}{pivote_col + 1} = {formatear_valor(rhs[i])} − ({sustitucion}) = {formatear_valor(valor)}.")
        else:
            valor = (rhs[i] - suma) / matriz[i][pivote_col]
            lineas.append(f"   {formatear_valor(matriz[i][pivote_col])}·{variable}{pivote_col + 1} + {expresion} = {formatear_valor(rhs[i])}; {variable}{pivote_col + 1} = ({formatear_valor(rhs[i])} − ({sustitucion})) / {formatear_valor(matriz[i][pivote_col])} = {formatear_valor(valor)}.")
    return lineas


def _texto_clasificacion(A, b, sistema):
    """Líneas con y, la clasificación de Ax = b y su solución (particular más núcleo)."""
    if sistema["estado"] == "incompatible":
        fila = next(i for i, valores in enumerate(sistema["U"])
                    if all(valor == 0 for valor in valores) and sistema["y"][i] != 0)
        return ["Clasificación: sistema incompatible.",
                f"Fila {fila + 1} de U: 0 = {formatear_valor(sistema['y'][fila])} ≠ 0; por eso no existe solución."]
    rhs_y = [sum(sistema["P"][i][j] * b[j] for j in range(len(b))) for i in range(len(b))]
    lado_derecho = "Pb" if sistema["P"] != [[int(i == j) for j in range(len(b))] for i in range(len(b))] else "b"
    lineas = [f"Explicación pedagógica: resolver Ly={lado_derecho} hacia adelante porque L es triangular inferior y su diagonal es unitaria."]
    lineas.extend(_ecuaciones_triangulares(sistema["L"], rhs_y, sistema["y"], "y", True))
    lineas.append(f"Resultado intermedio: y = {formatear_vector(sistema['y'])}")
    x0 = sistema["solucion_particular"]
    lineas.append("Explicación pedagógica: resolver Ux=y hacia atrás desde la última fila no nula, usando los valores ya despejados.")
    lineas.extend(_ecuaciones_triangulares(sistema["U"], sistema["y"], x0, "x", False))
    lineas.append("Resultado final:")
    if sistema["estado"] == "unica":
        lineas.append("x = " + formatear_vector(x0))
    else:
        libres = ", ".join(f"x{subindice(j + 1)}" for j in sistema["columnas_libres"])
        bases = " + ".join(f"t{subindice(k)}·{formatear_vector(v)}" for k, v in enumerate(sistema["bases_nucleo"], 1))
        lineas.extend([f"Infinitas soluciones: las variables {libres} son libres.",
                       f"x = {formatear_vector(x0)} + {bases}"])
    producto = [sum(A[i][j] * x0[j] for j in range(len(x0))) for i in range(len(A))]
    lineas.extend([f"A · x = {formatear_vector(producto)}",
                   "Comprobación exitosa: A · x == b" if sistema["verificacion"]
                   else "La comprobación falló: A · x ≠ b"])
    return lineas


def _resumen(datos):
    """Texto del recuadro negro con la respuesta final (método sin pivoteo, A cuadrada)."""
    if "x" not in datos:
        return "Ax = b no tiene solución única (A es singular)"
    return f"Solución única: x = {formatear_vector(datos['x'])}   ·   L·U = A ✓   ·   A·x = b ✓"


def _resumen_sistema(sistema):
    """Texto corto con la clasificación de Ax = b obtenida por la factorización con traza."""
    if sistema["estado"] == "incompatible":
        return "Ax = b no tiene solución"
    if sistema["estado"] == "unica":
        return f"Solución única: x = {formatear_vector(sistema['solucion_particular'])}"
    return "Ax = b tiene infinitas soluciones"
