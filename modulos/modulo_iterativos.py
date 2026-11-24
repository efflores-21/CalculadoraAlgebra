"""
Pantalla del módulo de métodos iterativos: Jacobi y Gauss-Seidel.

Unidad III, Métodos numéricos [P8]: tabla de iteraciones, error, residuo,
reordenamiento de ecuaciones, gráfica comparativa del error y validación con
la solución de Gauss-Jordan.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import math
import tkinter as tk

import customtkinter as ctk

from backend.matriz import formatear_valor, subindice
from backend.metodos_iterativos import MAX_ITERACIONES, resolver
from modulos._comun import (
    COLOR,
    Selector,
    TarjetaResultado,
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    entrada_numero,
    etiqueta,
    formatear_matriz,
    fuente_mono,
    leer_entero,
    leer_fraccion,
    llenar,
    mensaje_error,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
)

REORDENAR, NO_REORDENAR = "Reordenar si hace falta", "No reordenar"
NOMBRES = {"jacobi": "Jacobi", "gauss_seidel": "Gauss-Seidel"}
COLORES = {"jacobi": "#9DB8F5", "gauss_seidel": "#F4A261"}
MAX_FILAS = 50

# (A, b, x⁽⁰⁾, ε, máximo, reordenar) de los tres casos de prueba de la guía.
CASOS = {
    "Caso 1: converge": ([[10, -1, 2, 0], [-1, 11, -1, 3], [2, -1, 10, -1], [0, 3, -1, 8]],
                         [6, 25, -11, 15], [0, 0, 0, 0], "0.000001", 100, REORDENAR),
    "Caso 2: reordenar": ([[0, 1, 3], [5, 0, 2], [1, 4, 0]], [11, 11, 9], [0, 0, 0], "0.000001", 100, REORDENAR),
    "Caso 3: no converge": ([[1, 3], [1, 2]], [4, 3], [0, 0], "0.000001", 50, REORDENAR),
}


def _num(valor):
    """Número decimal corto para tablas y resúmenes."""
    return "—" if valor is None else f"{valor:.10g}"


def _exacto(valor):
    """Fracción exacta si es corta; si no, su valor decimal (o la fracción, si no cabe en float)."""
    texto = formatear_valor(valor)
    if len(texto) <= 20:
        return texto
    try:
        return f"≈ {float(valor):.10g}"
    except OverflowError:
        return texto[:20] + "…"


def _x(i):
    """Nombre de la incógnita i (base 0): x₁, x₂, …"""
    return f"x{subindice(i + 1)}"


def _vector(v):
    """Vector en una línea: (1, 2, -1)."""
    return "(" + ", ".join(_num(c) for c in v) + ")"


def _texto_validaciones(datos):
    """Sección 1: dimensiones, diagonal, dominancia y reordenamiento."""
    n = len(datos["A"])
    lineas = ["1) VALIDACIONES",
              f"Dimensiones: A es {n}×{n}, b y x⁽⁰⁾ tienen {n} componentes ✓",
              f"Tolerancia ε = {_num(datos['tolerancia'])} ✓"]
    if datos["ceros_originales"]:
        filas = ", ".join(f"a{subindice(i + 1)}{subindice(i + 1)}" for i in datos["ceros_originales"])
        lineas.append(f"La diagonal original tenía ceros ({filas}): no se puede dividir entre aᵢᵢ.")
    if datos["orden"]:
        orden = ", ".join(f"E{i + 1}" for i in datos["orden"])
        lineas += [f"Reordenamiento: {datos['motivo_orden']}",
                   f"Nuevo orden de las ecuaciones: {orden}", "[A | b] reordenada:",
                   formatear_matriz(_aumentada(datos), separar=len(datos["A"]))]
    elif datos["motivo_orden"]:
        lineas.append(f"Reordenamiento: {datos['motivo_orden']}")
    lineas.append("Diagonal sin ceros ✓")
    lineas.append("Diagonal estrictamente dominante por filas (|aᵢᵢ| > suma del resto de la fila):")
    for i, (diagonal, resto, cumple) in enumerate(datos["dominancia"]):
        lineas.append(f"   Fila {i + 1}: {_num(diagonal)} {'>' if cumple else '≤'} {_num(resto)}   "
                      f"{'✓' if cumple else '✗'}")
    if datos["dominante"]:
        lineas.append("La matriz es estrictamente dominante: los dos métodos convergen (condición suficiente) ✓")
    else:
        lineas.append("Significa: no es estrictamente dominante. Esto NO prueba que diverjan; solo que la "
                      "convergencia no está garantizada (es una condición suficiente, no necesaria).")
    return lineas


def _aumentada(datos):
    """Matriz [A | b] tal como se usa en los métodos."""
    return [fila + [bi] for fila, bi in zip(datos["A"], datos["b"])]


def _formula_primer_paso(datos, metodo):
    """Cálculo de la iteración 1 con números, para ver la diferencia entre métodos."""
    A, b, x = datos["A"], datos["b"], datos["x0"][:]
    nuevo = x[:]
    lineas = []
    for i in range(len(A)):
        usados = nuevo if metodo == "gauss_seidel" else x
        terminos = " ".join(f"− ({formatear_valor(A[i][j])})({_num(usados[j])})" for j in range(len(A)) if j != i)
        valor = (b[i] - sum(A[i][j] * usados[j] for j in range(len(A)) if j != i)) / A[i][i]
        lineas.append(f"   {_x(i)}⁽¹⁾ = ({_num(b[i])} {terminos}) / {_num(A[i][i])} = {_num(valor)}")
        nuevo[i] = valor
    return lineas


def _fila(valores, ancho=15):
    """Fila de la tabla de iteraciones en columnas de ancho fijo."""
    k, *resto = valores
    return f"{str(k):>4}" + "".join(f"{str(v):>{ancho}}" for v in resto)


def _tabla(datos, resultado):
    """Tabla k, x₁…xₙ, error; con muchas iteraciones muestra las primeras y las últimas."""
    n = len(datos["A"])
    lineas = [_fila(["k"] + [_x(i) for i in range(n)] + ["error ‖Δx‖∞"]),
              _fila([0] + [_num(v) for v in datos["x0"]] + ["—"])]
    filas = resultado["tabla"]
    if len(filas) > MAX_FILAS:
        mitad = MAX_FILAS // 2
        omitidas = len(filas) - MAX_FILAS
        filas = filas[:mitad] + [None] + filas[-mitad:]
    else:
        omitidas = 0
    for fila in filas:
        if fila is None:
            lineas.append(f"   …  {omitidas} iteraciones intermedias no se muestran  …")
            continue
        lineas.append(_fila([fila["k"]] + [_num(v) for v in fila["x"]] + [f"{fila['error']:.3e}"]))
    return lineas


def _estado(resultado, tolerancia):
    """Frase del estado final de un método."""
    if resultado["estado"] == "converge":
        return f"Convergencia alcanzada en {resultado['iteraciones']} iteraciones ✓ (error ≤ ε = {_num(tolerancia)})"
    if resultado["estado"] == "diverge":
        return (f"✗ El método diverge: en la iteración {resultado['iteraciones'] + 1} los valores crecieron "
                "sin control (o dejaron de ser finitos). Se detuvo para no cerrar la calculadora.")
    texto = f"✗ Se llegó al máximo de iteraciones ({resultado['iteraciones']}) sin alcanzar la tolerancia"
    if resultado["error_creciente"]:
        texto += ": el error está creciendo, posible no convergencia"
    return texto + "."


def _texto_metodo(datos, metodo, numero):
    """Secciones 2 y 3: fórmula, primer paso, tabla, solución, estado y residuo."""
    r = datos[metodo]
    if metodo == "jacobi":
        idea = ("Idea clave: todos los componentes nuevos se calculan con los valores de la iteración "
                "ANTERIOR (actualización simultánea).")
        formula = "   xᵢ⁽ᵏ⁺¹⁾ = (bᵢ − Σⱼ≠ᵢ aᵢⱼ xⱼ⁽ᵏ⁾) / aᵢᵢ"
    else:
        idea = ("Idea clave: cada componente nuevo se usa DE INMEDIATO para calcular los siguientes "
                "en la misma iteración.")
        formula = "   xᵢ⁽ᵏ⁺¹⁾ = (bᵢ − Σⱼ<ᵢ aᵢⱼ xⱼ⁽ᵏ⁺¹⁾ − Σⱼ>ᵢ aᵢⱼ xⱼ⁽ᵏ⁾) / aᵢᵢ"
    lineas = [f"{numero}) MÉTODO DE {NOMBRES[metodo].upper()}", idea, formula,
              "Iteración 1 con números:", *_formula_primer_paso(datos, metodo), "", "Tabla de iteraciones:"]
    lineas += _tabla(datos, r)
    lineas += ["", f"Solución aproximada: x = {_vector(r['x'])}", _estado(r, datos["tolerancia"])]
    if r["residuo"] is not None:
        lineas.append(f"Residuo final ‖Ax − b‖∞ = {r['residuo']:.3e}")
    return lineas


def _texto_comparacion(datos):
    """Secciones 4 y 5: comparación de métodos y validación con Gauss-Jordan."""
    c = datos["comparacion"]
    lineas = ["4) COMPARACIÓN DE LOS MÉTODOS"]
    for metodo in ("jacobi", "gauss_seidel"):
        r = datos[metodo]
        lineas.append(f"   {NOMBRES[metodo]:<13} {r['iteraciones']:>6} iteraciones   ·   {_estado(r, datos['tolerancia'])}")
    if c["mas_rapido"] == "empate":
        lineas.append("Los dos necesitaron las mismas iteraciones.")
    elif c["mas_rapido"]:
        lineas.append(f"Necesitó menos iteraciones: {NOMBRES[c['mas_rapido']]} ✓")
    else:
        lineas.append("Ninguno de los dos alcanzó la tolerancia con estos datos.")
    if c["diferencia"] is not None and c["mas_rapido"]:
        lineas.append(f"Diferencia entre las dos soluciones: ‖x_Jacobi − x_Gauss-Seidel‖∞ = {c['diferencia']:.3e}")
    lineas.append("5) VALIDACIÓN CON GAUSS-JORDAN (solución de referencia exacta)")
    if datos["referencia"] is None:
        return lineas + ["El sistema no tiene solución única: no hay solución de referencia."]
    lineas.append("x_ref = (" + ", ".join(_exacto(v) for v in datos["referencia"]) + ")")
    for metodo, diferencia in c["contra_referencia"].items():
        if datos[metodo]["estado"] == "converge":
            lineas.append(f"   ‖x_{NOMBRES[metodo]} − x_ref‖∞ = {diferencia:.3e} ✓")
    return lineas


def texto_resultado(datos):
    """Todo el resultado explicado, en el orden de la guía."""
    lineas = _texto_validaciones(datos) + [""]
    lineas += _texto_metodo(datos, "jacobi", 2) + [""]
    lineas += _texto_metodo(datos, "gauss_seidel", 3) + [""]
    return "\n".join(lineas + _texto_comparacion(datos))


def resumen(datos):
    """Respuesta corta para el recuadro de arriba."""
    partes = []
    for metodo in ("jacobi", "gauss_seidel"):
        r = datos[metodo]
        marca = "✓" if r["estado"] == "converge" else "✗"
        partes.append(f"{NOMBRES[metodo]}: {r['iteraciones']} iter. {marca}")
    mas_rapido = datos["comparacion"]["mas_rapido"]
    if mas_rapido and mas_rapido != "empate":
        partes.append(f"más rápido: {NOMBRES[mas_rapido]}")
    elif not mas_rapido:
        partes.append("ninguno converge")
    return "   ·   ".join(partes)


def _texto_iteraciones(datos, metodo):
    """Presenta la trayectoria real de un método en su propia vista."""
    resultado = datos[metodo]
    lineas = [f"MÉTODO DE {NOMBRES[metodo].upper()}",
              "Error por iteración: ||x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾||∞",
              "", *_tabla(datos, resultado), "",
              f"Estado: {_estado(resultado, datos['tolerancia'])}"]
    if resultado["residuo"] is not None:
        lineas.append(f"Residuo final ||Ax − b||∞ = {resultado['residuo']:.3e}")
    return "\n".join(lineas)


def _texto_procedimiento(datos):
    """Explica las reglas de actualización aplicadas con los datos ingresados."""
    lineas = _texto_validaciones(datos) + [""]
    for metodo in ("jacobi", "gauss_seidel"):
        if metodo == "jacobi":
            idea = "Todos los componentes nuevos usan exclusivamente x de la iteración anterior."
            formula = "xᵢ⁽ᵏ⁺¹⁾ = (bᵢ − Σⱼ≠ᵢ aᵢⱼ xⱼ⁽ᵏ⁾) / aᵢᵢ"
        else:
            idea = "Cada componente nuevo se usa de inmediato en las ecuaciones siguientes."
            formula = "xᵢ⁽ᵏ⁺¹⁾ = (bᵢ − Σⱼ<ᵢ aᵢⱼ xⱼ⁽ᵏ⁺¹⁾ − Σⱼ>ᵢ aᵢⱼ xⱼ⁽ᵏ⁾) / aᵢᵢ"
        lineas += [f"{NOMBRES[metodo].upper()}", idea, formula,
                   "Iteración 1 sustituida con los valores ingresados:",
                   *_formula_primer_paso(datos, metodo), "",
                   f"Terminación: error ||x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾||∞ ≤ ε = {_num(datos['tolerancia'])}; "
                   "si no se cumple, se continúa hasta el máximo o hasta detectar divergencia.", ""]
    lineas += ["COMPROBACIÓN", "El residuo ||Ax − b||∞ mide cuánto satisface cada aproximación el sistema.",
               "La referencia se obtiene con Gauss-Jordan cuando existe solución única."]
    return "\n".join(lineas)


class ModuloIterativos(ctk.CTkFrame):
    """Panel para resolver Ax = b con Jacobi y Gauss-Seidel y compararlos."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A, self.entradas_b, self.entradas_x0 = [], [], []
        self.ultimo = None
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Pantalla estándar: datos a la izquierda, resultado explicado a la derecha."""
        zonas = crear_estructura(
            self, self.on_back, numero=10, titulo="Jacobi y Gauss-Seidel",
            descripcion="Métodos iterativos para Ax = b: tabla, error, residuo y comparación.",
            logo=("  x⁽ᵏ⁺¹⁾ = (b − Σ a x⁽ᵏ⁾)/aᵢᵢ    MÓDULO: MÉTODOS ITERATIVOS\n"
                  "  ‖x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾‖∞ ≤ ε          Jacobi · Gauss-Seidel"),
            pasos=[
                "Escribe n (tamaño del sistema), la tolerancia ε y el máximo de iteraciones; pulsa «Crear tabla».",
                "Llena A, b y el vector inicial x⁽⁰⁾ (puede ser todo 0). Deja «Reordenar si hace falta» para "
                "que se busque otro orden de ecuaciones si hay ceros en la diagonal.",
                "Pulsa «Resolver con ambos métodos». Los botones «Caso 1/2/3» cargan los casos de prueba de la guía.",
            ],
            clave_teoremas="iterativos", ejemplo=lambda: self.cargar_caso("Caso 1: converge"),
            indicacion="Aquí verás las validaciones, la tabla de cada método, el residuo, la comparación y "
                       "la validación con Gauss-Jordan.",
        )
        self.resultado = zonas.resultado
        self._crear_vistas_resultado()
        contenido = zonas.contenido
        controles, entradas = crear_controles(
            contenido,
            [("n", "Tamaño n", "3", 80), ("tol", "Tolerancia ε", "0.000001", 110, False),
             ("max", "Máx. iteraciones", "100", 110, False)],
            self.actualizar_entradas,
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_n, self.entry_tol, self.entry_max = entradas["n"], entradas["tol"], entradas["max"]
        self.selector = Selector(contenido, [REORDENAR, NO_REORDENAR])
        self.selector.pack(anchor="w", padx=10, pady=(12, 0))
        casos = ctk.CTkFrame(contenido, fg_color="transparent")
        casos.pack(anchor="w", padx=10, pady=(12, 0))
        for nombre in CASOS:
            boton_secundario(casos, nombre, lambda n=nombre: self.cargar_caso(n), width=150).pack(side="left", padx=(0, 6))
        subtitulo(contenido, "Sistema  A · x = b   y   vector inicial x⁽⁰⁾").pack(anchor="w", padx=10, pady=(18, 6))
        self.marco_tabla = ctk.CTkFrame(contenido, fg_color="transparent")
        self.marco_tabla.pack(anchor="w", padx=6)
        subtitulo(contenido, "Gráfica del error por iteración").pack(anchor="w", padx=10, pady=(18, 6))
        self.lienzo = tk.Canvas(contenido, height=260, background=COLOR["suave"], highlightthickness=0)
        self.lienzo.pack(fill="x", padx=10, pady=(0, 10))
        self.lienzo.bind("<Configure>", lambda _evento: self.dibujar_grafica())
        boton_primario(zonas.acciones, "Resolver con ambos métodos", self.calcular).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(side="left")

    def actualizar_entradas(self):
        """Crea las celdas de A (n×n), b y x⁽⁰⁾."""
        try:
            n = leer_entero(self.entry_n, "El tamaño n")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.marco_tabla.winfo_children():
            widget.destroy()
        for j in range(n):
            etiqueta(self.marco_tabla, _x(j), color="texto", negrita=True).grid(row=0, column=j, pady=(0, 2))
        etiqueta(self.marco_tabla, "= b", color="texto", negrita=True).grid(row=0, column=n + 1, pady=(0, 2))
        etiqueta(self.marco_tabla, "x⁽⁰⁾", color="texto", negrita=True).grid(row=0, column=n + 3, pady=(0, 2))
        self.entradas_A, self.entradas_b, self.entradas_x0 = [], [], []
        for i in range(n):
            self.entradas_A.append([self._celda(i + 1, j) for j in range(n)])
            self.entradas_b.append(self._celda(i + 1, n + 1, padx=(14, 3)))
            self.entradas_x0.append(self._celda(i + 1, n + 3, padx=(14, 3)))
        self.ultimo = None
        self.dibujar_grafica()
        reemplazar_texto(self.resultado, "")

    def _celda(self, fila, columna, padx=3):
        """Una celda numérica en la cuadrícula del sistema."""
        celda = entrada_numero(self.marco_tabla)
        celda.grid(row=fila, column=columna, padx=padx, pady=3)
        return celda

    def _leer(self):
        """Lee A, b, x⁽⁰⁾, ε y el máximo de iteraciones."""
        A = [[leer_fraccion(c, f"La entrada ({i + 1},{j + 1}) de A") for j, c in enumerate(fila)]
             for i, fila in enumerate(self.entradas_A)]
        b = [leer_fraccion(c, f"La componente {i + 1} de b") for i, c in enumerate(self.entradas_b)]
        x0 = [leer_fraccion(c, f"La componente {i + 1} de x⁽⁰⁾") for i, c in enumerate(self.entradas_x0)]
        tolerancia = leer_fraccion(self.entry_tol, "La tolerancia ε")
        maximo = leer_entero(self.entry_max, "El máximo de iteraciones", 1, MAX_ITERACIONES)
        return A, b, x0, tolerancia, maximo

    def calcular(self):
        """Valida, ejecuta Jacobi y Gauss-Seidel y muestra todo explicado."""
        try:
            A, b, x0, tolerancia, maximo = self._leer()
            datos = resolver(A, b, x0, tolerancia, maximo, reordenar=self.selector.get() == REORDENAR)
        except (ValueError, ZeroDivisionError, OverflowError) as error:
            mensaje_error(error)
            return
        self.ultimo = datos
        reemplazar_texto(self.resultado, texto_resultado(datos), resumen(datos))
        self._actualizar_vistas_resultado(datos)
        self.resultado.grid_remove()
        self.vistas_resultado.grid()
        self.dibujar_grafica()

    def _crear_vistas_resultado(self):
        """Sustituye la salida larga por vistas enfocadas, locales a este módulo."""
        padre = self.resultado.master
        self.resultado.grid_remove()
        self.vistas_resultado = ctk.CTkFrame(padre, fg_color="transparent")
        self.vistas_resultado.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.vistas_resultado.grid_remove()
        self.vistas_resultado.grid_columnconfigure(0, weight=1)
        self.vistas_resultado.grid_rowconfigure(0, weight=1)
        self.pestanas = ctk.CTkTabview(
            self.vistas_resultado, fg_color=COLOR["suave"],
            segmented_button_fg_color=COLOR["tarjeta"],
            segmented_button_selected_color=COLOR["acento"],
            segmented_button_selected_hover_color=COLOR["hover"],
            segmented_button_unselected_color=COLOR["tarjeta"],
            text_color=COLOR["texto"],
        )
        self.pestanas.grid(row=0, column=0, sticky="nsew")
        for nombre in ("Resumen", "Jacobi", "Gauss-Seidel", "Procedimiento"):
            self.pestanas.add(nombre)
        resumen_tab = self.pestanas.tab("Resumen")
        resumen_tab.grid_columnconfigure((0, 1), weight=1, uniform="metodos")
        self.tarjetas_metodo = {}
        for columna, metodo in enumerate(("jacobi", "gauss_seidel")):
            tarjeta = TarjetaResultado(resumen_tab, NOMBRES[metodo], "—", "Aún sin resolver")
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=8, pady=(8, 14))
            self.tarjetas_metodo[metodo] = tarjeta
        etiqueta(resumen_tab, "Comparación basada en las iteraciones y métricas observadas", negrita=True).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(4, 2))
        self.caja_comparacion = self._crear_caja_resultado(resumen_tab)
        self.caja_comparacion.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=(4, 8))
        resumen_tab.grid_rowconfigure(2, weight=1)
        self.cajas_iteraciones = {
            metodo: self._crear_caja_resultado(self.pestanas.tab(nombre))
            for metodo, nombre in (("jacobi", "Jacobi"), ("gauss_seidel", "Gauss-Seidel"))
        }
        for caja in self.cajas_iteraciones.values():
            caja.pack(fill="both", expand=True, padx=8, pady=8)
        self.caja_procedimiento = self._crear_caja_resultado(self.pestanas.tab("Procedimiento"))
        self.caja_procedimiento.pack(fill="both", expand=True, padx=8, pady=8)
        # El botón compartido "Cómo usar" se enlaza a la guía de esta pantalla y
        # también oculta la vista local, sin alterar el helper global.
        pendientes = list(self.winfo_children())
        while pendientes:
            widget = pendientes.pop()
            pendientes.extend(widget.winfo_children())
            if isinstance(widget, ctk.CTkButton) and str(widget.cget("text")).startswith("?  Cómo usar"):
                widget.configure(command=self.mostrar_guia)
                break

    @staticmethod
    def _crear_caja_resultado(parent):
        caja = ctk.CTkTextbox(
            parent, font=fuente_mono(12), wrap="none",
            fg_color=COLOR["tarjeta"], text_color=COLOR["texto"],
            border_width=1, border_color=COLOR["borde"], corner_radius=10,
        )
        return caja

    @staticmethod
    def _escribir_caja(caja, texto):
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def _actualizar_vistas_resultado(self, datos):
        for metodo in ("jacobi", "gauss_seidel"):
            resultado = datos[metodo]
            detalle = (f"{resultado['iteraciones']} iteraciones · error final "
                       f"{_num(resultado['tabla'][-1]['error'] if resultado['tabla'] else None)}\n"
                       f"Residuo ||Ax − b||∞: {_num(resultado['residuo'])}")
            estado = ("Convergió", "ok") if resultado["estado"] == "converge" else (
                "Divergió", "mal") if resultado["estado"] == "diverge" else ("Máximo alcanzado", "warning")
            self.tarjetas_metodo[metodo].actualizar(_vector(resultado["x"]), detalle, estado)
            self._escribir_caja(self.cajas_iteraciones[metodo], _texto_iteraciones(datos, metodo))
        comparacion = _texto_comparacion(datos)
        self._escribir_caja(self.caja_comparacion, "\n".join(comparacion))
        self._escribir_caja(self.caja_procedimiento, _texto_procedimiento(datos))

    def mostrar_guia(self):
        """Vuelve a la guía de uso y oculta las vistas del último cálculo."""
        self.vistas_resultado.grid_remove()
        reemplazar_texto(self.resultado, "")

    def dibujar_grafica(self):
        """Error (escala logarítmica) contra el número de iteración, para ambos métodos."""
        lienzo = self.lienzo
        lienzo.delete("all")
        ancho, alto = max(lienzo.winfo_width(), 300), max(lienzo.winfo_height(), 200)
        series = {}
        if self.ultimo:
            for metodo in ("jacobi", "gauss_seidel"):
                puntos = [(f["k"], math.log10(f["error"])) for f in self.ultimo[metodo]["tabla"] if f["error"] > 0]
                if puntos:
                    series[metodo] = puntos
        if not series:
            lienzo.create_text(ancho / 2, alto / 2, fill=COLOR["gris"], font=("Segoe UI", 11),
                               text="Aquí aparecerá la gráfica del error de Jacobi y Gauss-Seidel.")
            return
        self._ejes_y_series(lienzo, ancho, alto, series)

    def _ejes_y_series(self, lienzo, ancho, alto, series):
        """Dibuja cuadrícula, ejes, la línea de la tolerancia y una curva por método."""
        izq, der, arr, aba = 58, 16, 30, 34
        todos = [p for puntos in series.values() for p in puntos]
        log_tol = math.log10(self.ultimo["tolerancia"])
        kmax = max(k for k, _ in todos)
        # El eje va de una potencia de 10 entera a otra para que las marcas sean exactas.
        ymin = math.floor(min(min(y for _, y in todos), log_tol))
        ymax = max(math.ceil(max(max(y for _, y in todos), log_tol)), ymin + 1)
        paso = max(1, math.ceil((ymax - ymin) / 5))
        px = lambda k: izq + (k - 1) * (ancho - izq - der) / max(kmax - 1, 1)
        py = lambda y: arr + (ymax - y) * (alto - arr - aba) / (ymax - ymin)
        for y in range(ymin, ymax + 1, paso):
            lienzo.create_line(izq, py(y), ancho - der, py(y), fill=COLOR["borde"])
            lienzo.create_text(izq - 6, py(y), text=f"1e{y}", anchor="e", fill=COLOR["gris"], font=("Segoe UI", 9))
        lienzo.create_line(izq, py(log_tol), ancho - der, py(log_tol), fill=COLOR["ok"], dash=(4, 3))
        lienzo.create_text(ancho - der, py(log_tol) - 8, text="tolerancia ε", anchor="e", fill=COLOR["ok"], font=("Segoe UI", 9))
        for metodo, puntos in series.items():
            coords = [c for k, y in puntos for c in (px(k), py(y))]
            if len(coords) >= 4:
                lienzo.create_line(*coords, fill=COLORES[metodo], width=2)
            for k, y in puntos[-1:]:
                lienzo.create_oval(px(k) - 3, py(y) - 3, px(k) + 3, py(y) + 3, fill=COLORES[metodo], outline="")
        for indice, metodo in enumerate(series):
            lienzo.create_rectangle(izq + 10 + 130 * indice, 10, izq + 24 + 130 * indice, 18, fill=COLORES[metodo], outline="")
            lienzo.create_text(izq + 30 + 130 * indice, 14, text=NOMBRES[metodo], anchor="w", fill=COLOR["texto"], font=("Segoe UI", 10))
        lienzo.create_text((izq + ancho - der) / 2, alto - 10, text=f"iteración k (1 a {kmax})", fill=COLOR["gris"], font=("Segoe UI", 9))
        lienzo.create_text(14, (arr + alto - aba) / 2, text="error ‖Δx‖∞", angle=90, fill=COLOR["gris"], font=("Segoe UI", 9))

    def cargar_caso(self, nombre):
        """Carga uno de los tres casos de prueba de la guía y lo resuelve."""
        A, b, x0, tolerancia, maximo, reordenar = CASOS[nombre]
        llenar([self.entry_n, self.entry_tol, self.entry_max], [len(A), tolerancia, maximo])
        self.actualizar_entradas()
        for fila, valores in zip(self.entradas_A, A):
            llenar(fila, valores)
        llenar(self.entradas_b, b)
        llenar(self.entradas_x0, x0)
        self.selector.set(reordenar)
        self.calcular()

    def limpiar(self):
        """Pone las celdas en cero y borra el resultado y la gráfica."""
        reiniciar_celdas(self.entradas_A, self.entradas_b, self.entradas_x0)
        self.ultimo = None
        self.vistas_resultado.grid_remove()
        self.dibujar_grafica()
        reemplazar_texto(self.resultado, "")
