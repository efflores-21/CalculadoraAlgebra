"""
Pantalla del módulo de transformaciones lineales T(x) = A·x.

Unidad III, Transformaciones lineales [P7]: propiedades de suma y escalar,
combinación lineal, núcleo, imagen, rango, nulidad y teorema de la dimensión.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import customtkinter as ctk

from backend.matriz import formatear_valor, subindice
from backend.transformaciones import analizar, aplicar, esta_en_imagen, verificar_linealidad
from modulos._comun import (
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    entrada_numero,
    etiqueta,
    formatear_matriz,
    formatear_vector,
    leer_entero,
    leer_fraccion,
    llenar,
    mensaje_error,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
)


def _r(n):
    """Escribe ℝ con el exponente n en superíndice (ℝ³)."""
    return "ℝ" + str(n).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))


def _x(j):
    """Nombre de la variable j (base 0): x₁, x₂, …"""
    return f"x{subindice(j + 1)}"


def _si_no(cumple):
    """Marca de comprobación para una igualdad."""
    return "✓ se cumple" if cumple else "✗ NO se cumple"


def _texto_componentes(A, x, nombre):
    """Muestra cómo sale cada componente de A·x (fila de A por el vector)."""
    lineas = []
    for i, fila in enumerate(A):
        productos = " + ".join(f"({formatear_valor(a)})({formatear_valor(xi)})" for a, xi in zip(fila, x))
        total = sum((a * xi for a, xi in zip(fila, x)), 0)
        lineas.append(f"   componente {i + 1}: {productos} = {formatear_valor(total)}")
    return [f"T({nombre}) = A·{nombre} se calcula fila por fila:"] + lineas


def _texto_linealidad(A, u, v, c):
    """Sección 2: las dos propiedades que definen una transformación lineal."""
    d = verificar_linealidad(A, u, v, c)
    fv, k = formatear_vector, formatear_valor(c)
    return [
        "2) ¿T ES LINEAL? (propiedades de suma y de multiplicación por escalar)",
        "Qué se hace: se calculan los dos lados de cada igualdad y se comparan.",
        *_texto_componentes(A, u, "u"),
        "",
        "Propiedad de la suma:  T(u + v) = T(u) + T(v)",
        f"   u + v = {fv(d['u+v'])}",
        f"   Lado izquierdo:  T(u + v) = {fv(d['T(u+v)'])}",
        f"   Lado derecho:    T(u) + T(v) = {fv(d['T(u)'])} + {fv(d['T(v)'])} = {fv(d['T(u)+T(v)'])}",
        f"   Resultado: {_si_no(d['cumple_suma'])}",
        "",
        f"Propiedad del escalar (c = {k}):  T(c·u) = c·T(u)",
        f"   c·u = {fv(d['c·u'])}",
        f"   Lado izquierdo:  T(c·u) = {fv(d['T(c·u)'])}",
        f"   Lado derecho:    c·T(u) = {k}·{fv(d['T(u)'])} = {fv(d['c·T(u)'])}",
        f"   Resultado: {_si_no(d['cumple_escalar'])}",
        "Por qué siempre se cumple: multiplicar por una matriz reparte la suma y saca "
        "el escalar, así que toda T(x) = A·x es lineal.",
    ], d["cumple_suma"] and d["cumple_escalar"]


def _texto_combinacion(A, u, b):
    """Sección 3: T(u) como combinación lineal de las columnas y si b está en la imagen."""
    n = len(A[0])
    columnas = [[fila[j] for fila in A] for j in range(n)]
    lineas = [
        "3) COMBINACIÓN LINEAL",
        "Idea clave: A·x = x₁·a₁ + x₂·a₂ + … (las aᵢ son las columnas de A).",
        "T(u) = " + " + ".join(f"({formatear_valor(u[j])})·{formatear_vector(columnas[j])}" for j in range(n))
        + f" = {formatear_vector(aplicar(A, u))}",
        "",
        f"¿b = {formatear_vector(b)} es combinación lineal de las columnas de A?",
        "Qué se hace: se resuelve A·x = b reduciendo [A | b].",
    ]
    esta, x, R = esta_en_imagen(A, b)
    lineas.extend(["[A | b] reducida:", formatear_matriz(R)])
    if esta:
        lineas.extend([
            "Sí: el sistema tiene solución, así que b está en la imagen de T.",
            "Una solución: " + ", ".join(f"{_x(j)} = {formatear_valor(x[j])}" for j in range(n)),
            "b = " + " + ".join(f"({formatear_valor(x[j])})·a{subindice(j + 1)}" for j in range(n)),
        ])
    else:
        lineas.append("No: aparece una fila 0 = (algo ≠ 0), el sistema no tiene solución y "
                      "b NO está en la imagen de T.")
    return lineas, esta


def _por_que_paso(descripcion):
    """Explica en una frase para qué sirve cada operación de fila."""
    if descripcion.startswith("Intercambio"):
        return "Se cambian filas para tener un pivote distinto de cero arriba."
    if descripcion.startswith("Normalizar"):
        return "Se divide la fila entre su pivote para que el pivote quede en 1."
    return "Se resta un múltiplo de la fila del pivote para hacer cero esa entrada."


def _texto_reduccion(datos):
    """Sección 4: la forma escalonada reducida de A, paso a paso."""
    lineas = ["4) REDUCCIÓN DE A (Gauss-Jordan sobre [A | 0])",
              "Qué se hace: se lleva A a forma escalonada reducida para ver sus pivotes."]
    for indice, paso in enumerate(datos["pasos"][1:], 1):
        lineas.extend([f"Paso {indice}: {paso['descripcion']}",
                       f"   Por qué: {_por_que_paso(paso['descripcion'])}",
                       formatear_matriz(paso["matriz"])])
    if len(datos["pasos"]) == 1:
        lineas.append("A ya está reducida (o es la matriz cero): no hace falta ningún paso.")
    pivotes = ", ".join(str(p + 1) for p in datos["pivotes"]) or "ninguna"
    lineas.append(f"Columnas pivote: {pivotes}.")
    return lineas


def _texto_imagen(datos):
    """Sección 5: rango e imagen de T."""
    base = datos["base_imagen"]
    lineas = [
        "5) IMAGEN Y RANGO",
        "Imagen: todos los vectores T(x) que se pueden obtener (las combinaciones de las columnas).",
        "Una base de la imagen son las columnas de la A ORIGINAL que tienen pivote:",
    ]
    lineas.extend(f"   a{subindice(p + 1)} = {formatear_vector(col)}" for p, col in zip(datos["pivotes"], base))
    if not base:
        lineas.append("   Ninguna: la imagen es solo el vector cero.")
    lineas.append(f"Rango(T) = número de pivotes = dim Im(T) = {datos['rango']}")
    return lineas


def _ecuacion(fila, pivote, libres):
    """Escribe la ecuación de una fila reducida y despeja la variable pivote."""
    despeje = " + ".join(f"({formatear_valor(-fila[j])})·{_x(j)}" for j in libres if fila[j] != 0)
    return f"   {_x(pivote)} = {despeje or '0'}"


def _texto_nucleo(A, datos):
    """Sección 6: núcleo y nulidad, con la comprobación A·v = 0."""
    lineas = ["6) NÚCLEO Y NULIDAD",
              "Núcleo: todos los x que T manda al cero, es decir, las soluciones de A·x = 0."]
    if not datos["libres"]:
        return lineas + ["No hay variables libres: la única solución es x = 0.",
                         "Núcleo = {0}   →   Nulidad(T) = 0"]
    lineas.append("Variables libres (columnas sin pivote): "
                  + ", ".join(_x(j) for j in datos["libres"]) + ". De la matriz reducida:")
    lineas.extend(_ecuacion(datos["R"][i], p, datos["libres"]) for i, p in enumerate(datos["pivotes"]))
    lineas.append("Dando valor 1 a una libre (y 0 a las demás) sale cada vector de la base:")
    for indice, (libre, vector) in enumerate(zip(datos["libres"], datos["base_nucleo"]), 1):
        nombre = f"v{subindice(indice)}"
        lineas.append(f"   {_x(libre)} = 1  →  {nombre} = {formatear_vector(vector)}   "
                      f"comprobación A·{nombre} = {formatear_vector(aplicar(A, vector))} ✓")
    lineas.append("Base del núcleo: {" + ", ".join(f"v{subindice(i + 1)}" for i in range(datos["nulidad"])) + "}")
    lineas.append(f"Nulidad(T) = número de variables libres = dim Nu(T) = {datos['nulidad']}")
    return lineas


def _texto_dimension(datos):
    """Sección 7: teorema de la dimensión y qué tipo de transformación es."""
    r, k, n, m = datos["rango"], datos["nulidad"], datos["n"], datos["m"]
    return [
        "7) TEOREMA DE LA DIMENSIÓN",
        f"Dice: rango(T) + nulidad(T) = n (dimensión del espacio de salida {_r(n)}).",
        f"   {r} + {k} = {r + k}   y   n = {n}   →   {_si_no(datos['cumple_dimension'])}",
        "Por qué: cada columna de A tiene pivote (cuenta en el rango) o es libre (cuenta en la nulidad).",
        "",
        "Conclusión:",
        "   Inyectiva (uno a uno): " + ("Sí, porque el núcleo es solo {0}." if datos["inyectiva"]
                                         else "No, porque el núcleo tiene vectores distintos de 0."),
        "   Sobreyectiva (sobre): " + (f"Sí, porque rango = {r} = m: la imagen es todo {_r(m)}."
                                       if datos["sobreyectiva"]
                                       else f"No, porque rango = {r} < m = {m}: la imagen no llena {_r(m)}."),
    ]


class ModuloTransformaciones(ctk.CTkFrame):
    """Panel para estudiar una transformación lineal T: ℝⁿ → ℝᵐ dada por su matriz."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A, self.entradas_u, self.entradas_v, self.entradas_b = [], [], [], []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Arma la pantalla estándar con los datos de A, u, v, c y b."""
        zonas = crear_estructura(
            self, self.on_back, numero=8, titulo="Transformaciones lineales",
            descripcion="T(x) = A·x: linealidad, núcleo, imagen, rango, nulidad y teorema de la dimensión.",
            logo=("  T: ℝⁿ → ℝᵐ    MÓDULO: TRANSFORMACIONES LINEALES\n"
                  "  T(x) = A·x    Nu(T) · Im(T) · rango · nulidad\n"
                  "  rango + nulidad = n"),
            pasos=[
                "Escribe m (filas) y n (columnas) de la matriz A y pulsa «Crear tablas». "
                "T va de ℝⁿ a ℝᵐ.",
                "Llena A. Escribe u, v y c para probar las propiedades de suma y escalar, "
                "y b para ver si está en la imagen.",
                "Pulsa «Analizar T»: verás linealidad, combinación lineal, núcleo, imagen, "
                "rango, nulidad y el teorema de la dimensión.",
            ],
            clave_teoremas="transformaciones", ejemplo=self.cargar_ejemplo,
            indicacion="Aquí verás cada parte explicada paso a paso, con su comprobación.",
        )
        self.resultado = zonas.resultado
        controles, entradas = crear_controles(
            zonas.contenido,
            [("m", "Filas m", "2", 80), ("n", "Columnas n", "3", 90), ("c", "Escalar c", "2", 80, False)],
            self.actualizar_entradas, texto_boton="Crear tablas",
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_m, self.entry_n, self.entry_c = entradas["m"], entradas["n"], entradas["c"]
        self.marco_A = self._seccion(zonas.contenido, "Matriz A")
        self.marco_vectores = self._seccion(zonas.contenido, "Vectores u, v (n componentes)  y  b (m componentes)")
        boton_primario(zonas.acciones, "Analizar T", self.calcular).pack(side="left", fill="x", expand=True, padx=(0, 8))
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(side="left")

    @staticmethod
    def _seccion(contenido, titulo):
        """Subtítulo y marco vacío donde luego van las celdas."""
        subtitulo(contenido, titulo).pack(anchor="w", padx=10, pady=(18, 6))
        marco = ctk.CTkFrame(contenido, fg_color="transparent")
        marco.pack(anchor="w", padx=6)
        return marco

    def actualizar_entradas(self):
        """Crea las celdas de A (m×n), de u y v (n) y de b (m)."""
        try:
            m = leer_entero(self.entry_m, "Las filas m")
            n = leer_entero(self.entry_n, "Las columnas n")
        except ValueError as error:
            mensaje_error(error)
            return
        for marco in (self.marco_A, self.marco_vectores):
            for widget in marco.winfo_children():
                widget.destroy()
        self.entradas_A = [[self._celda(self.marco_A, i, j) for j in range(n)] for i in range(m)]
        self.entradas_u, self.entradas_v, self.entradas_b = (
            self._columna(self.marco_vectores, columna, nombre, tamano)
            for columna, nombre, tamano in ((0, "u", n), (1, "v", n), (2, "b", m))
        )
        reemplazar_texto(self.resultado, "")

    @staticmethod
    def _celda(marco, fila, columna):
        """Una celda numérica colocada en la cuadrícula."""
        celda = entrada_numero(marco)
        celda.grid(row=fila, column=columna, padx=3, pady=3)
        return celda

    def _columna(self, marco, columna, nombre, tamano):
        """Un vector escrito en columna, con su nombre arriba."""
        etiqueta(marco, nombre, color="texto", negrita=True).grid(row=0, column=columna, pady=(0, 2))
        return [self._celda(marco, i + 1, columna) for i in range(tamano)]

    def _leer(self):
        """Lee A, u, v, b y c como fracciones exactas."""
        def vector(celdas, nombre):
            return [leer_fraccion(celda, f"La componente {i + 1} de {nombre}") for i, celda in enumerate(celdas)]
        A = [vector(fila, f"la fila {i + 1} de A") for i, fila in enumerate(self.entradas_A)]
        return (A, vector(self.entradas_u, "u"), vector(self.entradas_v, "v"),
                vector(self.entradas_b, "b"), leer_fraccion(self.entry_c, "El escalar c"))

    def calcular(self):
        """Analiza T(x) = A·x y muestra todas las secciones explicadas."""
        try:
            A, u, v, b, c = self._leer()
            datos = analizar(A)
            lineal_txt, lineal = _texto_linealidad(A, u, v, c)
            combinacion_txt, _ = _texto_combinacion(A, u, b)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)
            return
        m, n = datos["m"], datos["n"]
        lineas = ["1) LA TRANSFORMACIÓN",
                  f"T: {_r(n)} → {_r(m)},  T(x) = A·x   (A tiene {m} filas y {n} columnas)",
                  formatear_matriz(A), ""]
        for seccion in (lineal_txt, combinacion_txt, _texto_reduccion(datos),
                        _texto_imagen(datos), _texto_nucleo(A, datos), _texto_dimension(datos)):
            lineas.extend(seccion + [""])
        resumen = (f"{'Lineal ✓' if lineal else 'No lineal'}   ·   rango = {datos['rango']}   ·   "
                   f"nulidad = {datos['nulidad']}   ·   {datos['rango']} + {datos['nulidad']} = {n}")
        reemplazar_texto(self.resultado, "\n".join(lineas), resumen)

    def cargar_ejemplo(self):
        """Carga T: ℝ⁴ → ℝ³ con rango 2 y nulidad 2, y la analiza."""
        llenar([self.entry_m, self.entry_n, self.entry_c], [3, 4, 2])
        self.actualizar_entradas()
        for fila, valores in zip(self.entradas_A, [[1, 2, 0, 1], [2, 4, 1, 3], [3, 6, 1, 4]]):
            llenar(fila, valores)
        for celdas, valores in ((self.entradas_u, [1, 0, 1, 0]), (self.entradas_v, [0, 1, 0, 1]),
                                (self.entradas_b, [1, 3, 4])):
            llenar(celdas, valores)
        self.calcular()

    def limpiar(self):
        """Pone todas las celdas en cero y borra el resultado."""
        reiniciar_celdas(self.entradas_A, self.entradas_u, self.entradas_v, self.entradas_b)
        reemplazar_texto(self.resultado, "")
