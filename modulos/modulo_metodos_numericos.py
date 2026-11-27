"""Pantalla integrada de bisección, gráficas, notación posicional y errores numéricos."""

import math
import re
import tkinter as tk

import customtkinter as ctk

from backend.biseccion import resolver_biseccion
from backend.errores_numericos import (
    analizar_punto_flotante,
    calcular_errores,
    propagar_error,
    resumen_tipos_error,
)
from backend.graficador import muestrear_funcion
from backend.newton_raphson import resolver_newton_raphson
from backend.notacion_posicional import binario_a_decimal, decimal_a_binario, descomponer_decimal
from backend.funciones import identificar_variables
from backend.propagacion_errores import propagar_errores
from backend.series_maclaurin import MAX_TERMINOS_MACLAURIN, calcular_maclaurin
from modulos._comun import (
    COLOR,
    Panel,
    TarjetaResultado,
    boton_primario,
    boton_secundario,
    boton_texto,
    etiqueta,
    fuente_mono,
    reemplazar_texto,
    mostrar_teoremas,
)


def _leer_entero(texto, nombre):
    """Convierte un campo a entero con un mensaje en español (int() da uno técnico en inglés)."""
    texto = texto.strip()
    if not re.fullmatch(r"[+-]?[0-9]+", texto):
        raise ValueError(f"{nombre} debe ser un número entero, sin decimales ni letras.")
    if len(texto.lstrip("+-")) > 30:
        raise ValueError(f"{nombre} puede tener como máximo 30 cifras.")
    return int(texto)


def _leer_real(texto, nombre):
    """Convierte un campo a número real con un mensaje en español."""
    try:
        return float(texto)
    except ValueError as error:
        raise ValueError(f"{nombre} debe ser un número real.") from error


MAX_FILAS_TABLA = 50


def _filas_a_mostrar(tabla, maximo=MAX_FILAS_TABLA):
    """Primeras y últimas iteraciones, con None donde se omiten las del medio."""
    # Cada celda es un widget: con ~1000 iteraciones (tolerancia 1e-300) dibujarlas
    # todas congelaba la app varios minutos.
    if len(tabla) <= maximo:
        return list(tabla)
    mitad = maximo // 2
    return tabla[:mitad] + [None] + tabla[-mitad:]


def _formatear_numero(valor):
    """Formatea números para la GUI sin perder valores pequeños ni precisión interna."""
    if valor is None:
        return "—"
    if not math.isfinite(valor):
        return "No finito"
    if valor == 0:
        return "0"
    magnitud = abs(valor)
    if 1e-4 <= magnitud < 1e7:
        return f"{valor:.8g}"
    return f"{valor:.6e}"


def _texto_procedimiento_biseccion(datos, expresion, intervalo_inicial):
    """Organiza exclusivamente valores existentes en el resultado y la traza."""
    lineas = [
        f"1. Función: f(x) = {expresion}",
        f"2. Intervalo inicial: [{_formatear_numero(intervalo_inicial[0])}, "
        f"{_formatear_numero(intervalo_inicial[1])}]",
    ]
    if not datos["tabla"]:
        lineas.extend([
            "3. No se requieren iteraciones: el backend encontró una raíz exacta en un extremo.",
            "4. En los demás casos, Bisección requiere un cambio de signo y continuidad en todo "
            "el intervalo para aplicar Bolzano.",
        ])
    else:
        lineas.extend([
            "3. El backend validó el cambio de signo en los extremos. Este cambio por sí solo "
            "no prueba continuidad; consulta la advertencia de Bolzano.",
            "4. En cada fila se calcula xr = a/2 + b/2, se evalúa f(xr) y se conserva el "
            "subintervalo cuyos extremos mantienen signos opuestos.",
        ])
    for paso in datos["tabla"]:
        siguiente = paso["intervalo_siguiente"]
        lineas.extend([
            f"\nIteración {paso['k']} · intervalo usado "
            f"[{_formatear_numero(paso['a'])}, {_formatear_numero(paso['b'])}]",
            f"f(a) = {_formatear_numero(paso['fa'])}; f(b) = {_formatear_numero(paso['fb'])}",
            f"xr = a/2 + b/2 = {_formatear_numero(paso['xr'])}",
            f"f(xr) = {_formatear_numero(paso['fr'])}",
            f"Cota de semiancho = {_formatear_numero(paso['cota_error'])}",
            f"Intervalo siguiente: [{_formatear_numero(siguiente[0])}, "
            f"{_formatear_numero(siguiente[1])}]",
            "Decisión: " + paso["decision"],
        ])
        if paso["error_absoluto_aprox"] is not None:
            lineas.append("Cambio absoluto entre puntos medios = " +
                          _formatear_numero(paso["error_absoluto_aprox"]))
    lineas.extend([
        "\nCriterio de terminación: " + datos["motivo"],
        f"Resultado reportado: x ≈ {_formatear_numero(datos['raiz'])}; "
        f"f(x) = {_formatear_numero(datos['f_raiz'])}.",
    ])
    return "\n".join(lineas)


def _estado_visual_newton(datos):
    """Clasifica el resultado para presentarlo sin inferir convergencia."""
    if datos["convergio"]:
        return "Convergencia satisfactoria", "success"
    motivo = (datos.get("motivo") or "").lower()
    if datos["estado"] == "maximo":
        return "Aproximación obtenida · convergencia no confirmada", "warning"
    if "derivada" in motivo:
        return "Detenido por derivada inválida o cercana a cero", "warning"
    if datos["estado"] == "error":
        return "Error de evaluación o numérico", "error"
    return "Detenido sin convergencia", "error"


def _texto_procedimiento_newton(datos, indice):
    """Construye la explicación del paso con valores registrados por el backend."""
    lineas = [
        f"1. Función: f(x) = {datos['expresion']}",
        f"2. Derivada utilizada: f′(x) = {datos['derivada']}",
        f"3. Valor inicial: x₀ = {_formatear_numero(datos['valor_inicial'])}",
        "4. Fórmula: xₙ₊₁ = xₙ − f(xₙ) / f′(xₙ)",
    ]
    tabla = datos["tabla"]
    if tabla:
        paso = tabla[max(0, min(len(tabla) - 1, indice))]
        lineas.extend([
            f"5. Iteración {paso['k']}: xₙ = {_formatear_numero(paso['xi'])}",
            f"   f(xₙ) = {_formatear_numero(paso['fxi'])}",
            f"   f′(xₙ) = {_formatear_numero(paso.get('derivada'))}",
        ])
        siguiente = paso.get("xi_siguiente")
        if siguiente is None:
            lineas.append("   No se calculó xₙ₊₁.")
            if paso.get("motivo"):
                lineas.append(f"   Motivo: {paso['motivo']}")
        else:
            error_paso = paso.get("error_aproximado_porcentual")
            if error_paso is None and siguiente == 0:
                error_texto = "No definido (xₙ₊₁ = 0)"
            else:
                error_texto = _formatear_numero(error_paso) + "%"
            lineas.append(
                "   Sustitución: xₙ₊₁ = "
                f"{_formatear_numero(paso['xi'])} − "
                f"({_formatear_numero(paso['fxi'])}) / "
                f"({_formatear_numero(paso.get('derivada'))}) = "
                f"{_formatear_numero(siguiente)}"
            )
            lineas.append(
                f"   Error aproximado porcentual: {error_texto}"
            )
            lineas.append(
                f"   Residuo |f(xₙ₊₁)|: {_formatear_numero(paso.get('residuo'))}"
            )
    else:
        lineas.append(
            "5. No hubo iteraciones: " + (
                "el valor inicial ya es una raíz exacta."
                if datos["convergio"] else "el proceso terminó antes del primer paso."
            )
        )
    lineas.append(f"6. Criterio de terminación: {datos['motivo']}")
    return "\n".join(lineas)


def _texto_terminos_maclaurin(datos):
    """Presenta los datos de cada término sin omitir coeficientes nulos."""
    lineas = ["n | Derivada | Derivada en 0 | Factorial | Coeficiente | Término"]
    for termino in datos["terminos"]:
        lineas.extend((
            f"n = {termino['orden']}",
            f"Derivada: {termino['derivada']}",
            f"Derivada en 0: {termino['derivada_en_cero']}",
            f"Factorial: {termino['orden']}! = {termino['factorial']}",
            f"Coeficiente: {termino['derivada_en_cero']} / {termino['factorial']} = {termino['coeficiente']}",
            f"Término: {termino['termino']}",
            "",
        ))
    return "\n".join(lineas)


def _texto_procedimiento_maclaurin(datos):
    """Construye una explicación basada solo en valores entregados por el backend."""
    lineas = [
        "Fórmula general: f(x) = Σ[n=0..∞] (f⁽ⁿ⁾(0) / n!) xⁿ",
        f"Función: f(x) = {datos['expresion']}",
        f"Se usan N = {datos['numero_terminos']} términos; el orden máximo incluido es N − 1 = {datos['numero_terminos'] - 1}.",
    ]
    for termino in datos["terminos"]:
        n = termino["orden"]
        lineas.extend((
            f"\nOrden n = {n}",
            f"f⁽{n}⁾(x) = {termino['derivada']}",
            f"f⁽{n}⁾(0) = {termino['derivada_en_cero']}",
            f"Coeficiente = f⁽{n}⁾(0) / {n}! = {termino['derivada_en_cero']} / {termino['factorial']} = {termino['coeficiente']}",
            f"Término = {termino['coeficiente']}·x^{n} = {termino['termino']}",
        ))
    lineas.extend((
        f"\nPolinomio: P_{datos['numero_terminos']}(x) = {datos['polinomio']}",
        f"Sustitución: P_{datos['numero_terminos']}({datos['x']:.12g}) = {datos['aproximacion']:.12g}",
    ))
    if datos["valor_real"] is not None:
        lineas.append(f"Valor de la función: f({datos['x']:.12g}) = {datos['valor_real']:.12g}")
        if datos["error_absoluto"] is not None:
            lineas.append(
                f"Error absoluto = |f(x) − P_N(x)| = {datos['error_absoluto']:.12g}"
            )
        if datos["aviso_error"]:
            lineas.append(datos["aviso_error"])
        elif datos["error_relativo_porcentual"] is None:
            lineas.append("Error relativo porcentual: no definido porque f(x) = 0.")
        elif datos["error_absoluto"] is not None:
            lineas.append(
                "Error relativo porcentual = error absoluto / |f(x)| × 100 = "
                f"{datos['error_relativo_porcentual']:.12g}%"
            )
    elif datos["aviso_evaluacion"]:
        lineas.append(datos["aviso_evaluacion"])
    if datos["aviso_convergencia"]:
        lineas.append(datos["aviso_convergencia"])
    lineas.append("\n" + datos["nota_convergencia"])
    return "\n".join(lineas)


class ModuloMetodosNumericos(ctk.CTkFrame):
    """Agrupa las actividades de métodos numéricos en pestañas de una misma pantalla."""

    def __init__(self, master, on_back):
        """Construye las pestañas e inicializa el estado compartido de bisección/gráfica."""
        super().__init__(master, fg_color=COLOR["fondo"])
        self.on_back = on_back
        self.ultimo_resultado = None
        self.ultima_muestra = None
        self._construir_interfaz()

    def _construir_interfaz(self):
        """Crea barra superior, pestañas y formularios de cada funcionalidad."""
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=28, pady=(14, 4))
        boton_secundario(barra, "←  Menú principal", self.on_back, width=160).pack(side="left")
        ctk.CTkLabel(barra, text="MÉTODOS NUMÉRICOS", font=ctk.CTkFont(size=27, weight="bold"),
                     text_color=COLOR["texto"]).pack(side="left", padx=20)
        boton_secundario(
            barra, "0. Teoremas clave",
            lambda: mostrar_teoremas(self, "metodos_numericos", "Métodos numéricos"),
        ).pack(side="right")
        boton_texto(barra, "? Cómo usar", self.mostrar_guia, width=110).pack(side="right", padx=8)
        etiqueta(self, "Bisección · Graficador · Notación posicional · Errores numéricos · Newton-Raphson · Maclaurin", tamano=14).pack(
            anchor="w", padx=34, pady=(0, 8))
        self.pestanas = ctk.CTkTabview(self, fg_color=COLOR["tarjeta"])
        self.pestanas.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        for nombre in ("Bisección", "Graficador", "Notación posicional", "Errores numéricos", "Newton-Raphson", "Series de Maclaurin"):
            self.pestanas.add(nombre)
        self._crear_biseccion(self.pestanas.tab("Bisección"))
        self._crear_graficador(self.pestanas.tab("Graficador"))
        self._crear_notacion(self.pestanas.tab("Notación posicional"))
        self._crear_errores(self.pestanas.tab("Errores numéricos"))
        self._crear_newton_raphson(self.pestanas.tab("Newton-Raphson"))
        self._crear_maclaurin(self.pestanas.tab("Series de Maclaurin"))

    @staticmethod
    def _entrada(parent, titulo, inicial, ancho=150):
        """Crea una etiqueta y un campo de texto sencillo."""
        grupo = ctk.CTkFrame(parent, fg_color="transparent")
        grupo.pack(side="left", padx=(0, 12), pady=6)
        etiqueta(grupo, titulo, tamano=12, color="texto").pack(anchor="w")
        campo = ctk.CTkEntry(grupo, width=ancho)
        campo.insert(0, str(inicial))
        campo.pack(anchor="w", pady=(3, 0))
        return campo

    @staticmethod
    def _caja_texto(parent, alto=14):
        """Añade una caja monoespaciada desplazable para resultados y tablas."""
        caja = ctk.CTkTextbox(parent, height=alto * 20, wrap="none", font=ctk.CTkFont(family="Consolas", size=12))
        caja.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        return caja

    def _crear_biseccion(self, parent):
        marco = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True)
        etiqueta(marco, "El cambio de signo permite aplicar Bolzano solo si f es continua en todo [a,b].", tamano=13).pack(anchor="w", padx=12, pady=(10, 4))
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(anchor="w", padx=12)
        self.b_expr = self._entrada(fila, "f(x)", "x**3 - 2*x - 5", 240)
        self.b_a = self._entrada(fila, "a", "2", 85)
        self.b_b = self._entrada(fila, "b", "3", 85)
        self.b_tol = self._entrada(fila, "Tolerancia absoluta", "0.0001", 130)
        self.b_max = self._entrada(fila, "Máximo iteraciones", "100", 125)
        acciones = ctk.CTkFrame(marco, fg_color="transparent")
        acciones.pack(anchor="w", padx=12, pady=5)
        boton_primario(acciones, "Resolver por bisección", self.calcular_biseccion, width=205).pack(side="left", padx=(0, 8))
        boton_secundario(acciones, "Graficar este intervalo", self.graficar_intervalo_biseccion, width=195).pack(side="left")
        self.b_resultado = ctk.CTkTabview(
            marco, fg_color=COLOR["suave"],
            segmented_button_fg_color=COLOR["tarjeta"],
            segmented_button_selected_color=COLOR["acento"],
            segmented_button_selected_hover_color=COLOR["hover"],
            segmented_button_unselected_color=COLOR["tarjeta"],
            text_color=COLOR["texto"],
        )
        self.b_resultado.pack(fill="both", expand=True, padx=6, pady=(8, 12))
        for nombre in ("Resumen", "Iteraciones", "Gráfica", "Procedimiento"):
            self.b_resultado.add(nombre)
        self.b_tab_resumen = self.b_resultado.tab("Resumen")
        self.b_tab_iteraciones = self.b_resultado.tab("Iteraciones")
        self.b_tab_grafica = self.b_resultado.tab("Gráfica")
        self.b_tab_procedimiento = self.b_resultado.tab("Procedimiento")
        self.b_datos = None
        self.b_paso_seleccionado = None

    def calcular_biseccion(self):
        """Calcula la raíz y explica resumen, cota y trazabilidad de cada intervalo."""
        try:
            maximo = _leer_entero(self.b_max.get(), "El máximo de iteraciones")
            datos = resolver_biseccion(self.b_expr.get(), self.b_a.get(), self.b_b.get(), self.b_tol.get(), maximo)
        except (ValueError, OverflowError) as error:
            self._mostrar_error(error)
            return
        self.ultimo_resultado = {
            "expresion": self.b_expr.get().strip(),
            "a": float(self.b_a.get()), "b": float(self.b_b.get()), **datos,
        }
        self.b_datos = datos
        self.b_paso_seleccionado = len(datos["tabla"]) - 1 if datos["tabla"] else None
        for tab in (self.b_tab_resumen, self.b_tab_iteraciones,
                    self.b_tab_grafica, self.b_tab_procedimiento):
            for widget in tab.winfo_children():
                widget.destroy()

        def numero(valor):
            return "—" if valor is None else f"{valor:.8g}"

        resumen = ctk.CTkFrame(self.b_tab_resumen, fg_color="transparent")
        resumen.pack(fill="x", padx=6, pady=(0, 8))
        valores = (
            ("Raíz aproximada", numero(datos["raiz"])),
            ("Iteraciones realizadas", str(datos["iteraciones"])),
            ("Iteraciones teóricas", str(datos["iteraciones_teoricas"])),
            ("Intervalo final", f"[{numero(datos['intervalo_final'][0])}, {numero(datos['intervalo_final'][1])}]"),
            ("Cota de error final", numero(datos["cota_error"])),
            ("f(raíz aproximada)", numero(datos["f_raiz"])),
            ("Tolerancia solicitada", numero(float(self.b_tol.get()))),
        )
        for columna in range(3):
            resumen.grid_columnconfigure(columna, weight=1, uniform="resumen_biseccion")
        for indice, (titulo, valor) in enumerate(valores):
            tarjeta = ctk.CTkFrame(resumen, fg_color=COLOR["tarjeta"], corner_radius=10,
                                   border_width=1, border_color=COLOR["borde"])
            tarjeta.grid(row=indice // 3, column=indice % 3, sticky="ew", padx=4, pady=4)
            etiqueta(tarjeta, titulo, tamano=11, color="gris").pack(anchor="w", padx=12, pady=(8, 1))
            etiqueta(tarjeta, valor, tamano=14, negrita=True, color="texto").pack(anchor="w", padx=12, pady=(0, 8))

        if datos["aviso_discontinuidad"]:
            estado = "Sin raíz confiable: posible asíntota"
        elif datos["alcanzada_tolerancia"]:
            estado = "Tolerancia alcanzada"
        elif "precisión" in datos["motivo"]:
            estado = "Límite de precisión de la computadora"
        else:
            estado = "Máximo de iteraciones alcanzado"
        if datos["aviso_discontinuidad"]:
            color_estado = COLOR["mal"]
        else:
            color_estado = "#66C2A5" if datos["alcanzada_tolerancia"] else "#F4A261"
        tarjeta_estado = ctk.CTkFrame(resumen, fg_color=COLOR["tarjeta"], corner_radius=10,
                                      border_width=1, border_color=COLOR["borde"])
        tarjeta_estado.grid(row=3, column=0, columnspan=3, sticky="ew", padx=4, pady=4)
        etiqueta(tarjeta_estado, "Estado de terminación", tamano=11, color="gris").pack(
            anchor="w", padx=12, pady=(8, 1)
        )
        ctk.CTkLabel(tarjeta_estado, text=estado, text_color=color_estado,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(0, 8))
        explicacion = (
            "Se alcanzó la tolerancia solicitada porque la cota del semiancho del intervalo final "
            "es menor o igual que la tolerancia establecida."
            if datos["alcanzada_tolerancia"] else
            datos["motivo"] if "precisión" in datos["motivo"] else
            "Se llegó al máximo de iteraciones antes de cumplir la tolerancia; la aproximación mostrada "
            "no garantiza que el error sea menor o igual que el valor solicitado."
        )
        if datos["aviso_discontinuidad"]:
            ctk.CTkLabel(self.b_tab_resumen, text="⚠  " + datos["aviso_discontinuidad"], text_color=COLOR["mal"],
                         font=ctk.CTkFont(size=13, weight="bold"), anchor="w", justify="left",
                         wraplength=900).pack(anchor="w", padx=10, pady=(6, 2))
        etiqueta(self.b_tab_resumen, datos["advertencia"], tamano=11, color="gris").pack(
            anchor="w", padx=10, pady=(4, 6)
        )

        contenedor = ctk.CTkFrame(self.b_tab_iteraciones, fg_color=COLOR["tarjeta"], corner_radius=10)
        contenedor.pack(fill="x", expand=True, padx=6, pady=(0, 6))
        canvas = tk.Canvas(contenedor, height=330, background=COLOR["tarjeta"],
                           highlightthickness=0, borderwidth=0)
        barra_y = ctk.CTkScrollbar(contenedor, orientation="vertical", command=canvas.yview)
        barra_x = ctk.CTkScrollbar(contenedor, orientation="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)
        tabla = ctk.CTkFrame(canvas, fg_color=COLOR["tarjeta"], width=1390)
        canvas.create_window((0, 0), window=tabla, anchor="nw")
        tabla.bind("<Configure>", lambda _evento: canvas.configure(scrollregion=canvas.bbox("all")))

        titulos = ("Iteración k", "a", "b", "f(a)", "f(b)", "Punto medio xr",
                   "f(xr)", "Cota de error", "Error aproximado", "Intervalo siguiente")
        anchos = (82, 120, 120, 125, 125, 145, 125, 135, 145, 250)
        for columna, (titulo, ancho) in enumerate(zip(titulos, anchos)):
            ctk.CTkLabel(tabla, text=titulo, width=ancho, height=42, anchor="center",
                         fg_color=COLOR["acento"], text_color=COLOR["texto"],
                         font=ctk.CTkFont(size=12, weight="bold")).grid(
                             row=0, column=columna, sticky="nsew", padx=1, pady=1)
        if not datos["tabla"]:
            etiqueta(tabla, "La raíz exacta está en un extremo; no se requieren iteraciones.",
                     tamano=12, color="gris").grid(row=1, column=0, columnspan=10, sticky="w", padx=12, pady=12)
        fuente_celda = ctk.CTkFont(size=12)
        self.b_filas_tabla = {}
        for fila, paso in enumerate(_filas_a_mostrar(datos["tabla"]), 1):
            if paso is None:
                omitidas = len(datos["tabla"]) - MAX_FILAS_TABLA
                etiqueta(tabla, f"…  {omitidas} iteraciones intermedias no se muestran "
                         f"(hay {len(datos['tabla'])} en total; el resumen de arriba usa todas)  …",
                         tamano=12, color="gris").grid(row=fila, column=0, columnspan=10, pady=8)
                continue
            intervalo = paso["intervalo_siguiente"]
            if paso["fr"] == 0:
                conservado = f"Raíz exacta: xr = {numero(paso['xr'])}"
            elif intervalo[1] == paso["xr"]:
                conservado = f"[a, xr] = [{numero(intervalo[0])}, {numero(intervalo[1])}]"
            else:
                conservado = f"[xr, b] = [{numero(intervalo[0])}, {numero(intervalo[1])}]"
            celdas = (str(paso["k"]), numero(paso["a"]), numero(paso["b"]),
                      numero(paso["fa"]), numero(paso["fb"]), numero(paso["xr"]),
                      numero(paso["fr"]), numero(paso["cota_error"]),
                      numero(paso["error_absoluto_aprox"]), conservado)
            fondo = COLOR["suave"] if fila % 2 == 0 else COLOR["tarjeta"]
            celdas_widgets = []
            for columna, (valor, ancho) in enumerate(zip(celdas, anchos)):
                celda = ctk.CTkLabel(tabla, text=valor, width=ancho, height=34, anchor="center",
                                     fg_color=fondo, text_color=COLOR["texto"],
                                     font=fuente_celda)
                celda.grid(row=fila, column=columna, sticky="nsew", padx=1, pady=1)
                celdas_widgets.append((celda, fondo))
                celda.bind(
                    "<Button-1>",
                    lambda _evento, indice=paso["k"] - 1:
                        self._seleccionar_paso_biseccion(indice),
                )
            self.b_filas_tabla[paso["k"] - 1] = celdas_widgets
        cabecera = ctk.CTkFrame(self.b_tab_resumen, fg_color=COLOR["suave"], corner_radius=8)
        cabecera.pack(fill="x", padx=6, pady=(4, 0))
        ctk.CTkLabel(cabecera, text=estado, text_color=color_estado,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(9, 2))
        etiqueta(cabecera, explicacion, tamano=12, color="texto").pack(anchor="w", padx=12, pady=(0, 9))
        etiqueta(cabecera, "Criterio: " + datos["motivo"], tamano=11, color="gris").pack(
            anchor="w", padx=12, pady=(0, 9)
        )
        self._crear_grafica_biseccion()
        self._crear_procedimiento_biseccion(datos)
        self._resaltar_fila_biseccion()

    def _crear_procedimiento_biseccion(self, datos):
        """Ordena la traza ya calculada sin alterar sus criterios ni valores."""
        texto = _texto_procedimiento_biseccion(
            datos, self.ultimo_resultado["expresion"],
            (self.ultimo_resultado["a"], self.ultimo_resultado["b"]),
        )
        caja = ctk.CTkTextbox(self.b_tab_procedimiento, wrap="word", height=330,
            fg_color=COLOR["tarjeta"], text_color=COLOR["texto"],
            font=ctk.CTkFont(family="Consolas", size=12))
        caja.pack(fill="both", expand=True, padx=10, pady=10)
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def _crear_grafica_biseccion(self):
        """Dibuja f(x) y el intervalo de la iteración seleccionada desde la traza."""
        marco = ctk.CTkFrame(self.b_tab_grafica, fg_color=COLOR["tarjeta"], corner_radius=10)
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        self.b_grafica_info = ctk.CTkLabel(marco, text="", anchor="w", wraplength=850,
                                           text_color=COLOR["texto"])
        self.b_grafica_info.pack(fill="x", padx=12, pady=(10, 4))
        controles = ctk.CTkFrame(marco, fg_color="transparent")
        controles.pack(fill="x", padx=12)
        self.b_slider = ctk.CTkSlider(controles, from_=0,
            to=max(1, len(self.b_datos["tabla"]) - 1), command=self._cambiar_paso_biseccion)
        self.b_slider.pack(fill="x", expand=True, side="left", padx=(0, 10))
        self.b_canvas = tk.Canvas(marco, height=330, background=COLOR["tarjeta"],
                                  highlightthickness=0, borderwidth=0)
        self.b_canvas.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        self.b_canvas.bind("<Configure>", lambda _evento: self._dibujar_grafica_biseccion())
        self._dibujar_grafica_biseccion()

    def _cambiar_paso_biseccion(self, valor):
        if self.b_datos and self.b_datos["tabla"]:
            self._seleccionar_paso_biseccion(round(float(valor)))

    def _seleccionar_paso_biseccion(self, indice):
        if not self.b_datos or not self.b_datos["tabla"]:
            return
        indice = max(0, min(len(self.b_datos["tabla"]) - 1, int(indice)))
        self.b_paso_seleccionado = indice
        if hasattr(self, "b_slider"):
            self.b_slider.set(indice)
        self._resaltar_fila_biseccion()
        self._dibujar_grafica_biseccion()

    def _resaltar_fila_biseccion(self):
        for indice, celdas in getattr(self, "b_filas_tabla", {}).items():
            for celda, fondo in celdas:
                if celda.winfo_exists():
                    celda.configure(fg_color=COLOR["interaccion"] if indice == self.b_paso_seleccionado else fondo)

    def _dibujar_grafica_biseccion(self):
        canvas = getattr(self, "b_canvas", None)
        datos = getattr(self, "b_datos", None)
        if canvas is None or datos is None or not canvas.winfo_exists():
            return
        ancho, alto = max(280, canvas.winfo_width()), max(200, canvas.winfo_height())
        margen = 54
        a0, b0 = self.ultimo_resultado["a"], self.ultimo_resultado["b"]
        canvas.delete("all")
        try:
            muestra = muestrear_funcion(datos.get("expresion", self.ultimo_resultado["expresion"]),
                                       a0, b0, cantidad=500)
        except (ValueError, OverflowError):
            canvas.create_text(ancho / 2, alto / 2, text="No fue posible dibujar la función en el intervalo.",
                               fill=COLOR["advertencia"])
            return
        valores = [y for segmento in muestra["segmentos"] for _, y in segmento]
        ymin, ymax = min(valores + [0.0]), max(valores + [0.0])
        if ymin == ymax:
            ymin, ymax = ymin - 1, ymax + 1
        else:
            espacio = (ymax - ymin) * 0.08
            ymin, ymax = ymin - espacio, ymax + espacio
        px = lambda x: margen + (x - a0) * (ancho - 2 * margen) / (b0 - a0)
        py = lambda y: alto - margen - (y - ymin) * (alto - 2 * margen) / (ymax - ymin)
        for i in range(6):
            gx = margen + i * (ancho - 2 * margen) / 5
            gy = margen + i * (alto - 2 * margen) / 5
            canvas.create_line(gx, margen, gx, alto - margen, fill=COLOR["borde"])
            canvas.create_line(margen, gy, ancho - margen, gy, fill=COLOR["borde"])
        if ymin <= 0 <= ymax:
            canvas.create_line(margen, py(0), ancho - margen, py(0), fill=COLOR["gris"], width=2)
        if a0 <= 0 <= b0:
            canvas.create_line(px(0), margen, px(0), alto - margen, fill=COLOR["gris"], width=2)
        for segmento in muestra["segmentos"]:
            coords = [coordenada for x, y in segmento for coordenada in (px(x), py(y))]
            if len(coords) >= 4:
                canvas.create_line(*coords, fill=COLOR["verde"], width=2)
        paso = datos["tabla"][self.b_paso_seleccionado] if datos["tabla"] else None
        if paso:
            intervalo = paso["intervalo_siguiente"]
            if ymin <= 0 <= ymax:
                canvas.create_line(px(intervalo[0]), py(0), px(intervalo[1]), py(0),
                                   fill=COLOR["advertencia"], width=5)
            for x, y, color, marca in ((paso["a"], paso["fa"], COLOR["acento"], "a"),
                                       (paso["b"], paso["fb"], COLOR["acento"], "b"),
                                       (paso["xr"], paso["fr"], COLOR["advertencia"], "c") ):
                canvas.create_oval(px(x)-5, py(y)-5, px(x)+5, py(y)+5,
                                   fill=color, outline=COLOR["texto"])
                canvas.create_text(px(x)+7, py(y)-10, text=marca, fill=color, anchor="w")
            self.b_grafica_info.configure(text=(
                f"Iteración {paso['k']} · intervalo usado [{_formatear_numero(paso['a'])}, "
                f"{_formatear_numero(paso['b'])}] · siguiente [{_formatear_numero(intervalo[0])}, "
                f"{_formatear_numero(intervalo[1])}] · xr = {_formatear_numero(paso['xr'])}"
            ))
        else:
            raiz = datos["raiz"]
            canvas.create_oval(px(raiz)-5, py(datos["f_raiz"])-5,
                               px(raiz)+5, py(datos["f_raiz"])+5,
                               fill=COLOR["advertencia"], outline=COLOR["texto"])
            self.b_grafica_info.configure(text="Raíz exacta en un extremo; no se generaron iteraciones.")
        canvas.create_text(ancho / 2, 14, text=f"f(x) = {self.ultimo_resultado['expresion']}",
                           fill=COLOR["texto"], font=("Segoe UI", 12, "bold"))

    def _crear_newton_raphson(self, parent):
        """Construye el formulario, el resumen numérico y la tabla de Newton-Raphson."""
        marco = ctk.CTkFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True)
        etiqueta(
            marco,
            "Usa la misma sintaxis segura que las otras herramientas: ** para potencias y funciones como sin(x), cos(x), exp(x). "
            "La tolerancia se introduce en porcentaje.",
            tamano=13,
        ).pack(anchor="w", padx=12, pady=(10, 5))

        fila_funcion = ctk.CTkFrame(marco, fg_color="transparent")
        fila_funcion.pack(anchor="w", padx=12)
        self.nr_expr = self._entrada(fila_funcion, "Función f(x)", "x**3 - 2*x - 5", 360)
        self.nr_x0 = self._entrada(fila_funcion, "Valor inicial x₀", "2", 130)

        fila_parametros = ctk.CTkFrame(marco, fg_color="transparent")
        fila_parametros.pack(anchor="w", padx=12)
        self.nr_tol = self._entrada(fila_parametros, "Tolerancia (%)", "0.0001", 150)
        self.nr_max = self._entrada(fila_parametros, "Máximo de iteraciones", "100", 180)
        boton_primario(
            fila_parametros, "Calcular", self.calcular_newton_raphson, width=120
        ).pack(side="left", padx=(2, 6), pady=(22, 0))
        boton_secundario(
            fila_parametros, "Ejemplo", self.ejemplo_newton_raphson, width=100
        ).pack(side="left", padx=(0, 6), pady=(22, 0))
        boton_secundario(
            fila_parametros, "Limpiar", self.limpiar_newton_raphson, width=100
        ).pack(side="left", pady=(22, 0))

        self.nr_estado = ctk.CTkLabel(
            marco, text="Ingresa una función y sus parámetros para comenzar.",
            text_color=COLOR["gris"], anchor="w", justify="left",
            font=ctk.CTkFont(size=13),
        )
        self.nr_estado.pack(fill="x", padx=16, pady=(4, 4))
        self.nr_resultado = ctk.CTkFrame(marco, fg_color="transparent")
        self.nr_resultado.pack(fill="both", expand=True, padx=6, pady=(4, 12))
        self.nr_grafica = None
        self.nr_datos = None
        self.nr_paso_seleccionado = 0
        self.nr_filas_tabla = {}

    def _vaciar_resultado_newton(self):
        """Elimina el resumen y las filas anteriores antes de una nueva ejecución."""
        for widget in self.nr_resultado.winfo_children():
            widget.destroy()
        self.nr_datos = None
        self.nr_filas_tabla = {}

    def ejemplo_newton_raphson(self):
        """Carga un ejemplo didáctico válido para el evaluador actual."""
        for campo, valor in (
            (self.nr_expr, "x**3 - 2*x - 5"),
            (self.nr_x0, "2"),
            (self.nr_tol, "0.0001"),
            (self.nr_max, "100"),
        ):
            campo.delete(0, "end")
            campo.insert(0, valor)
        self._vaciar_resultado_newton()
        self.nr_estado.configure(text="Ejemplo cargado. Pulsa Calcular para ver las iteraciones.",
                                 text_color=COLOR["gris"])

    def limpiar_newton_raphson(self):
        """Restablece campos, estado, resumen y tabla de iteraciones."""
        self.nr_expr.delete(0, "end")
        for campo, valor in ((self.nr_x0, "1"), (self.nr_tol, "0.0001"), (self.nr_max, "100")):
            campo.delete(0, "end")
            campo.insert(0, valor)
        self._vaciar_resultado_newton()
        self.nr_estado.configure(text="Formulario limpiado. Escribe una función para comenzar.",
                                 text_color=COLOR["gris"])

    def calcular_newton_raphson(self):
        """Valida las entradas, invoca el backend y presenta su resultado sin recalcularlo."""
        self._vaciar_resultado_newton()
        try:
            expresion = self.nr_expr.get().strip()
            if not expresion:
                raise ValueError("Escribe una función matemática en f(x).")
            x0 = _leer_real(self.nr_x0.get(), "El valor inicial x₀")
            tolerancia = _leer_real(self.nr_tol.get(), "La tolerancia")
            maximo = _leer_entero(self.nr_max.get(), "El máximo de iteraciones")
            datos = resolver_newton_raphson(expresion, x0, tolerancia, maximo)
        except (ValueError, OverflowError) as error:
            self.nr_estado.configure(text="Datos inválidos o función no evaluable.",
                                     text_color=COLOR["mal"])
            self._mostrar_error(error)
            return
        except Exception:
            self.nr_estado.configure(text="Ocurrió un error inesperado durante el cálculo.",
                                     text_color=COLOR["mal"])
            self._mostrar_error(ValueError(
                "No se pudo completar el cálculo. Revisa la función y vuelve a intentarlo."
            ))
            return

        self._mostrar_resultado_newton(datos)

    def _mostrar_resultado_newton(self, datos):
        """Presenta estado, métricas, gráfico, traza y explicación de la ejecución."""
        estado, variante = _estado_visual_newton(datos)
        color_estado = {
            "success": COLOR["ok"],
            "warning": COLOR["advertencia"],
            "error": COLOR["mal"],
        }[variante]
        etiqueta_aproximacion = (
            "raíz" if datos["convergio"] else "última aproximación"
        )
        self.nr_estado.configure(
            text=(f"{estado} · {etiqueta_aproximacion} x = "
                  f"{_formatear_numero(datos['aproximacion'])}"),
            text_color=color_estado,
        )
        self.nr_datos = datos
        self.nr_paso_seleccionado = max(0, len(datos["tabla"]) - 1)
        self.nr_filas_tabla = {}
        self.nr_selector_vista = ctk.CTkSegmentedButton(
            self.nr_resultado,
            values=("Gráfica", "Resumen", "Iteraciones", "Procedimiento"),
            command=self._cambiar_vista_newton,
        )
        self.nr_selector_vista.pack(pady=(0, 5))
        self.nr_area_vistas = ctk.CTkFrame(self.nr_resultado, fg_color="transparent")
        self.nr_area_vistas.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self.nr_area_vistas.grid_rowconfigure(0, weight=1)
        self.nr_area_vistas.grid_columnconfigure(0, weight=1)
        self.nr_panel_grafica = ctk.CTkFrame(self.nr_area_vistas, fg_color="transparent")
        self.nr_panel_resumen = ctk.CTkFrame(self.nr_area_vistas, fg_color="transparent")
        self.nr_panel_iteraciones = ctk.CTkFrame(self.nr_area_vistas, fg_color="transparent")
        self.nr_panel_procedimiento = ctk.CTkFrame(self.nr_area_vistas, fg_color="transparent")
        self.nr_paneles_vista = {
            "Gráfica": self.nr_panel_grafica,
            "Resumen": self.nr_panel_resumen,
            "Iteraciones": self.nr_panel_iteraciones,
            "Procedimiento": self.nr_panel_procedimiento,
        }
        for panel in self.nr_paneles_vista.values():
            panel.grid(row=0, column=0, sticky="nsew")
        self._crear_resumen_newton(self.nr_panel_resumen, datos, estado, color_estado)
        self._crear_grafica_newton(self.nr_panel_grafica)
        self._crear_tabla_newton(self.nr_panel_iteraciones, datos)
        self._crear_procedimiento_newton(self.nr_panel_procedimiento, datos)
        self.nr_selector_vista.set("Gráfica")
        self._cambiar_vista_newton("Gráfica")
        self._actualizar_resaltado_fila_newton()

    def _cambiar_vista_newton(self, nombre):
        panel = getattr(self, "nr_paneles_vista", {}).get(nombre)
        if panel is not None:
            panel.tkraise()

    def _crear_resumen_newton(self, parent, datos, estado, color_estado):
        """Destaca la aproximación y conserva las métricas finales del algoritmo."""
        principal = ctk.CTkFrame(parent, fg_color=COLOR["tarjeta"],
                                 corner_radius=12, border_width=1,
                                 border_color=COLOR["borde"])
        principal.pack(fill="x", padx=6, pady=(0, 7))
        principal.grid_columnconfigure(0, weight=3)
        principal.grid_columnconfigure(1, weight=2)
        etiqueta_aproximacion = (
            "Raíz aproximada" if datos["convergio"]
            else "Última aproximación · no confirmada como raíz"
        )
        etiqueta(principal, etiqueta_aproximacion, tamano=12, color="gris").grid(
            row=0, column=0, sticky="w", padx=16, pady=(10, 0)
        )
        ctk.CTkLabel(
            principal, text=_formatear_numero(datos["aproximacion"]),
            text_color=COLOR["texto"], font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 3))
        ctk.CTkLabel(
            principal, text=f"f(x) = {datos['expresion']}\nf′(x) = {datos['derivada']}",
            text_color=COLOR["gris"], font=ctk.CTkFont(size=12),
            anchor="w", justify="left", wraplength=600,
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))
        estado_widget = ctk.CTkLabel(
            principal, text=estado, text_color=color_estado,
            font=ctk.CTkFont(size=15, weight="bold"), anchor="w",
            justify="left", wraplength=330,
        )
        estado_widget.grid(row=0, column=1, rowspan=2, sticky="w", padx=12, pady=12)
        motivo = ctk.CTkLabel(
            principal, text=datos["motivo"], text_color=COLOR["gris"],
            font=ctk.CTkFont(size=11), anchor="w", justify="left", wraplength=340,
        )
        motivo.grid(row=2, column=1, sticky="ew", padx=12, pady=(0, 12))

        if datos["error_final"] is not None:
            error_final = _formatear_numero(datos["error_final"]) + "%"
        elif datos["iteraciones"] and datos["tabla"][-1].get("xi_siguiente") == 0:
            error_final = "No definido (xₙ₊₁ = 0)"
        elif datos["iteraciones"] == 0 and datos["convergio"]:
            error_final = "No aplica · raíz inicial exacta"
        else:
            error_final = "No disponible"
        residuo_relativo = datos.get("residuo_relativo_porcentual_final")
        metricas = (
            ("Iteraciones", str(datos["iteraciones"])),
            ("Error aproximado final", error_final),
            ("|f(x)| final", _formatear_numero(datos["residuo_final"])),
            ("Residuo relativo inicial", "—" if residuo_relativo is None else
             _formatear_numero(residuo_relativo) + "%"),
        )
        fila = ctk.CTkFrame(parent, fg_color="transparent")
        fila.pack(fill="x", padx=3, pady=(0, 5))
        for columna, (titulo, valor) in enumerate(metricas):
            fila.grid_columnconfigure(columna, weight=1, uniform="indicadores_newton")
            tarjeta = ctk.CTkFrame(fila, fg_color=COLOR["tarjeta"], corner_radius=9,
                                   border_width=1, border_color=COLOR["borde"])
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=3)
            etiqueta(tarjeta, titulo, tamano=10, color="gris").pack(
                anchor="w", padx=10, pady=(7, 1)
            )
            ctk.CTkLabel(
                tarjeta, text=valor, text_color=COLOR["texto"],
                font=ctk.CTkFont(size=12, weight="bold"), anchor="w",
                justify="left", wraplength=210,
            ).pack(anchor="w", fill="x", padx=10, pady=(0, 7))

    def _crear_tabla_newton(self, parent, datos):
        etiqueta(parent, "Selecciona una fila para enfocar esa iteración en la gráfica.",
                 tamano=12, color="gris").pack(anchor="w", padx=12, pady=(8, 4))
        contenedor = ctk.CTkFrame(parent, fg_color=COLOR["tarjeta"], corner_radius=10)
        contenedor.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        canvas = tk.Canvas(contenedor, height=290, background=COLOR["tarjeta"],
                           highlightthickness=0, borderwidth=0)
        barra_y = ctk.CTkScrollbar(contenedor, orientation="vertical", command=canvas.yview)
        barra_x = ctk.CTkScrollbar(contenedor, orientation="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        titulos = ("Iteración k", "xₙ", "f(xₙ)", "f′(xₙ)", "xₙ₊₁", "Error aprox. (%)",
                   "Residuo |f(xₙ₊₁)|", "Residuo relativo (%)")
        anchos = (76, 130, 145, 145, 130, 150, 165, 170)
        tabla = ctk.CTkFrame(canvas, fg_color=COLOR["tarjeta"], width=sum(anchos))
        canvas.create_window((0, 0), window=tabla, anchor="nw")
        tabla.bind("<Configure>", lambda _evento: canvas.configure(scrollregion=canvas.bbox("all")))
        for columna, (titulo, ancho) in enumerate(zip(titulos, anchos)):
            ctk.CTkLabel(tabla, text=titulo, width=ancho, height=42, anchor="center",
                         fg_color=COLOR["acento"], text_color=COLOR["texto"],
                         font=ctk.CTkFont(size=11, weight="bold")).grid(
                             row=0, column=columna, sticky="nsew", padx=1, pady=1)

        if not datos["tabla"]:
            mensaje = ("El valor inicial ya era una raíz; no se requirieron iteraciones."
                       if datos["convergio"] else "No se completó ninguna iteración.")
            etiqueta(tabla, mensaje, tamano=12, color="gris").grid(
                row=1, column=0, columnspan=len(titulos), sticky="w", padx=12, pady=12
            )
        fuente_celda = ctk.CTkFont(size=11)
        for fila, paso in enumerate(_filas_a_mostrar(datos["tabla"]), 1):
            if paso is None:
                omitidas = len(datos["tabla"]) - MAX_FILAS_TABLA
                etiqueta(tabla, f"…  {omitidas} iteraciones intermedias omitidas; se registraron {len(datos['tabla'])} en total  …",
                         tamano=12, color="gris").grid(
                             row=fila, column=0, columnspan=len(titulos), pady=8
                         )
                continue
            error = paso.get("error_aproximado_porcentual")
            if error is None and paso.get("xi_siguiente") == 0:
                error_texto = "No definido"
            else:
                error_texto = "—" if error is None else _formatear_numero(error) + "%"
            celdas = (
                str(paso["k"]), _formatear_numero(paso["xi"]), _formatear_numero(paso["fxi"]),
                _formatear_numero(paso.get("derivada")), _formatear_numero(paso.get("xi_siguiente")),
                error_texto, _formatear_numero(paso.get("residuo")),
                ("—" if paso.get("residuo_relativo_porcentual") is None else
                 _formatear_numero(paso["residuo_relativo_porcentual"]) + "%"),
            )
            indice_paso = paso["k"] - 1
            fondo = COLOR["suave"] if fila % 2 == 0 else COLOR["tarjeta"]
            celdas_fila = []
            for columna, (valor, ancho) in enumerate(zip(celdas, anchos)):
                celda = ctk.CTkLabel(
                    tabla, text=valor, width=ancho, height=34,
                    anchor="center" if columna == 0 else "e",
                    fg_color=fondo, text_color=COLOR["texto"], font=fuente_celda,
                )
                celda.grid(
                    row=fila, column=columna, sticky="nsew", padx=1, pady=1
                )
                celda.bind(
                    "<Button-1>",
                    lambda _evento, indice=indice_paso:
                        self._seleccionar_paso_newton(indice, desde_tabla=True),
                )
                celdas_fila.append((celda, fondo))
            self.nr_filas_tabla[indice_paso] = celdas_fila

    def _crear_procedimiento_newton(self, parent, datos):
        etiqueta(
            parent,
            "Cada valor se toma de la traza calculada. Cambia la iteración desde la gráfica o la tabla para revisar su sustitución.",
            tamano=12, color="gris", justify="left", anchor="w", wraplength=900,
        ).pack(anchor="w", fill="x", padx=14, pady=(12, 7))
        panel = ctk.CTkFrame(parent, fg_color=COLOR["suave"], corner_radius=10)
        panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.nr_texto_procedimiento = ctk.CTkTextbox(
            panel, wrap="word", font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=COLOR["suave"], text_color=COLOR["texto"],
        )
        self.nr_texto_procedimiento.pack(fill="both", expand=True, padx=10, pady=10)
        self._actualizar_procedimiento_newton()

    def _actualizar_procedimiento_newton(self):
        caja = getattr(self, "nr_texto_procedimiento", None)
        if caja is None or not caja.winfo_exists() or not self.nr_datos:
            return
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", _texto_procedimiento_newton(
            self.nr_datos, self.nr_paso_seleccionado
        ))
        caja.configure(state="disabled")

    def _actualizar_resaltado_fila_newton(self):
        for indice, celdas in getattr(self, "nr_filas_tabla", {}).items():
            for celda, color_base in celdas:
                if celda.winfo_exists():
                    color = (
                        COLOR["interaccion"]
                        if indice == self.nr_paso_seleccionado else color_base
                    )
                    celda.configure(fg_color=color)

    def _crear_grafica_newton(self, parent):
        """Crea la gráfica y controles; navegar reutiliza la traza ya calculada."""
        marco = ctk.CTkFrame(parent, fg_color=COLOR["tarjeta"], corner_radius=10)
        marco.pack(fill="both", expand=True, padx=8, pady=8)
        self.nr_info_paso = ctk.CTkLabel(marco, text="", anchor="w", justify="left",
                                          text_color=COLOR["texto"],
                                          font=ctk.CTkFont(size=12, weight="bold"))
        self.nr_info_paso.pack(fill="x", padx=12, pady=(9, 4))
        marco.bind(
            "<Configure>",
            lambda evento: self.nr_info_paso.configure(
                wraplength=max(240, evento.width - 36)
            ),
            add="+",
        )
        controles = ctk.CTkFrame(marco, fg_color="transparent")
        controles.pack(fill="x", padx=10, pady=(0, 5))
        self.nr_boton_anterior = boton_secundario(
            controles, "◀ Anterior", lambda: self._navegar_paso_newton(-1), width=115)
        self.nr_boton_anterior.pack(side="left", padx=(0, 8))
        filas = self.nr_datos["tabla"]
        self.nr_slider = ctk.CTkSlider(
            controles, from_=0, to=max(1, len(filas) - 1), number_of_steps=max(1, len(filas) - 1),
            command=self._cambiar_paso_newton)
        self.nr_slider.set(self.nr_paso_seleccionado)
        self.nr_slider.pack(side="left", fill="x", expand=True, padx=6)
        self.nr_boton_siguiente = boton_secundario(
            controles, "Siguiente ▶", lambda: self._navegar_paso_newton(1), width=115)
        self.nr_boton_siguiente.pack(side="left", padx=(8, 0))
        self.nr_canvas = tk.Canvas(marco, height=350, background=COLOR["tarjeta"],
                                   highlightthickness=0, borderwidth=0)
        self.nr_canvas.pack(fill="both", expand=True, padx=6, pady=(0, 8))
        self.nr_canvas.bind("<Configure>", lambda _evento: self._dibujar_grafica_newton())
        self._dibujar_grafica_newton()

    def _navegar_paso_newton(self, desplazamiento):
        if not self.nr_datos or not self.nr_datos["tabla"]:
            return
        self._seleccionar_paso_newton(self.nr_paso_seleccionado + desplazamiento)

    def _cambiar_paso_newton(self, valor):
        self._seleccionar_paso_newton(round(float(valor)), desde_slider=True)

    def _seleccionar_paso_newton(self, indice, desde_slider=False, desde_tabla=False):
        if not self.nr_datos or not self.nr_datos["tabla"]:
            return
        indice = max(0, min(len(self.nr_datos["tabla"]) - 1, int(indice)))
        self.nr_paso_seleccionado = indice
        if not desde_slider:
            self.nr_slider.set(indice)
        self._actualizar_resaltado_fila_newton()
        self._actualizar_procedimiento_newton()
        self._dibujar_grafica_newton()
        if desde_tabla and hasattr(self, "nr_selector_vista"):
            self.nr_selector_vista.set("Gráfica")
            self._cambiar_vista_newton("Gráfica")

    @staticmethod
    def _rango_robusto(valores, incluir_cero=False):
        """Calcula límites centrados que reducen el efecto de iteraciones extremas."""
        finitos = sorted(v for v in valores if math.isfinite(v))
        if not finitos:
            return (-1.0, 1.0)
        mediana = finitos[len(finitos) // 2]
        desviaciones = sorted(abs(v - mediana) for v in finitos)
        mad = desviaciones[len(desviaciones) // 2]
        escala = max(4 * mad, abs(mediana) * 0.05, 0.1)
        minimo, maximo = mediana - escala, mediana + escala
        if incluir_cero:
            minimo, maximo = min(minimo, 0.0), max(maximo, 0.0)
        return minimo, maximo

    def _dibujar_grafica_newton(self):
        """Traza f(x), el recorrido y solo la tangente del paso seleccionado."""
        datos = self.nr_datos
        canvas = getattr(self, "nr_canvas", None)
        if not datos or canvas is None or not canvas.winfo_exists():
            return
        ancho, alto = max(280, canvas.winfo_width()), max(140, canvas.winfo_height())
        margen = max(32, min(70, alto * 0.23))
        filas = datos["tabla"]
        indice = min(self.nr_paso_seleccionado, len(filas) - 1) if filas else -1
        x0 = datos["valor_inicial"]
        xs = [x0]
        for paso in filas:
            xs.append(paso["xi"])
            if paso.get("xi_siguiente") is not None:
                xs.append(paso["xi_siguiente"])
        if datos["convergio"]:
            xs.append(datos["aproximacion"])
        xmin, xmax = self._rango_robusto(xs)
        if xmin == xmax:
            xmin, xmax = xmin - 1, xmax + 1
        muestra = muestrear_funcion(datos["expresion"], xmin, xmax, cantidad=1200)
        ys = [y for segmento in muestra["segmentos"] for _, y in segmento]
        if not ys:
            canvas.delete("all")
            canvas.create_text(ancho / 2, alto / 2, text="No hay valores reales finitos para graficar.",
                               fill=COLOR["texto"])
            return
        ymin, ymax = self._rango_robusto(ys, incluir_cero=True)
        for paso in filas:
            if ymin <= paso["fxi"] <= ymax:
                ys.append(paso["fxi"])
        ymin, ymax = self._rango_robusto(ys, incluir_cero=True)
        if ymin == ymax:
            ymin, ymax = ymin - 1, ymax + 1
        # Recorta valores atípicos al muestrear y vuelve a usar los segmentos seguros.
        muestra = muestrear_funcion(datos["expresion"], xmin, xmax, cantidad=1200,
                                   limites_y=(ymin, ymax))
        px = lambda x: margen + (x - xmin) * (ancho - 2 * margen) / (xmax - xmin)
        py = lambda y: alto - margen - (y - ymin) * (alto - 2 * margen) / (ymax - ymin)
        canvas.delete("all")
        for marca in range(6):
            gx = margen + marca * (ancho - 2 * margen) / 5
            gy = margen + marca * (alto - 2 * margen) / 5
            canvas.create_line(gx, margen, gx, alto - margen, fill=COLOR["borde"])
            canvas.create_line(margen, gy, ancho - margen, gy, fill=COLOR["borde"])
            canvas.create_text(gx, alto - margen + 16,
                               text=f"{xmin + marca * (xmax - xmin) / 5:.3g}", fill="#B8B8C0")
            canvas.create_text(margen - 27, gy,
                               text=f"{ymax - marca * (ymax - ymin) / 5:.3g}", fill="#B8B8C0")
        canvas.create_text(15, alto / 2, text="f(x)", fill=COLOR["gris"], angle=90)
        canvas.create_text(ancho - margen + 34, alto - margen + 16, text="x",
                           fill=COLOR["gris"], anchor="w")
        if xmin <= 0 <= xmax:
            canvas.create_line(px(0), margen, px(0), alto - margen, fill="#85858D", width=2)
        if ymin <= 0 <= ymax:
            canvas.create_line(margen, py(0), ancho - margen, py(0), fill="#85858D", width=2)
        for segmento in muestra["segmentos"]:
            coords = [c for x, y in segmento for c in (px(x), py(y))]
            if len(coords) >= 4:
                canvas.create_line(*coords, fill="#66C2A5", width=2)

        # La trayectoria usa únicamente los valores xi y xi+1 devueltos por el backend.
        for paso_indice, paso in enumerate(filas[:indice + 1]):
            xi, fxi = paso["xi"], paso["fxi"]
            if xmin <= xi <= xmax and ymin <= fxi <= ymax:
                color = "#F4A261" if paso_indice == indice else "#8AB4F8"
                canvas.create_line(px(xi), py(0), px(xi), py(fxi), fill=color, dash=(3, 3))
                canvas.create_oval(px(xi)-4, py(fxi)-4, px(xi)+4, py(fxi)+4,
                                   fill=color, outline="white")
            siguiente = paso.get("xi_siguiente")
            derivada = paso.get("derivada")
            if siguiente is not None and derivada not in (None, 0) and xmin <= siguiente <= xmax:
                tangencia_en_x = min(xmax, max(xmin, siguiente))
                y_intermedio = fxi + derivada * (tangencia_en_x - xi)
                if math.isfinite(y_intermedio) and ymin <= y_intermedio <= ymax:
                    canvas.create_line(px(tangencia_en_x), py(0), px(tangencia_en_x),
                                       py(y_intermedio), fill="#B39DDB", dash=(2, 3))
                canvas.create_oval(px(siguiente)-4, py(0)-4, px(siguiente)+4, py(0)+4,
                                   fill="#B39DDB", outline="white")
            if paso_indice == indice and derivada is not None:
                if derivada == 0:
                    if ymin <= fxi <= ymax:
                        canvas.create_line(margen, py(fxi), ancho - margen, py(fxi),
                                           fill="#F4A261", width=2, dash=(6, 3))
                    canvas.create_text(ancho / 2, alto - 27,
                                       text="Derivada cero: no existe intercepto de Newton para este paso.",
                                       fill="#F4A261")
                else:
                    # La recta se recorta al área visible y nunca evalúa valores no finitos.
                    cortes = (xi + (ymin - fxi) / derivada, xi + (ymax - fxi) / derivada)
                    if all(math.isfinite(corte) for corte in cortes):
                        xa, xb = max(xmin, min(cortes)), min(xmax, max(cortes))
                    else:
                        xa, xb = xmin, xmax
                    if xa <= xb and math.isfinite(fxi):
                        ya, yb = fxi + derivada * (xa - xi), fxi + derivada * (xb - xi)
                        if math.isfinite(ya) and math.isfinite(yb) and ymin <= ya <= ymax and ymin <= yb <= ymax:
                            canvas.create_line(px(xa), py(ya), px(xb), py(yb),
                                               fill="#F4A261", width=2, dash=(6, 3))

        if datos["convergio"] and xmin <= datos["aproximacion"] <= xmax:
            canvas.create_oval(px(datos["aproximacion"])-6, py(0)-6,
                               px(datos["aproximacion"])+6, py(0)+6,
                               fill="#66D19E", outline="white", width=2)
            canvas.create_text(px(datos["aproximacion"])+8, py(0)-14,
                               text="raíz confirmada", fill="#66D19E", anchor="w")
        canvas.create_text(ancho / 2, 15, text=f"Newton-Raphson · f(x) = {datos['expresion']}",
                           fill=COLOR["texto"], font=("Segoe UI", 12, "bold"))
        leyenda_x = max(margen + 12, ancho - 425)
        leyenda_y = 34
        canvas.create_line(leyenda_x, leyenda_y, leyenda_x + 18, leyenda_y,
                           fill="#66C2A5", width=2)
        canvas.create_text(leyenda_x + 23, leyenda_y, text="f(x)",
                           fill=COLOR["texto"], anchor="w")
        canvas.create_line(leyenda_x + 82, leyenda_y, leyenda_x + 100, leyenda_y,
                           fill="#F4A261", width=2, dash=(5, 3))
        canvas.create_text(leyenda_x + 105, leyenda_y, text="tangente",
                           fill=COLOR["texto"], anchor="w")
        canvas.create_oval(leyenda_x + 180, leyenda_y - 4,
                           leyenda_x + 188, leyenda_y + 4,
                           fill="#F4A261", outline="white")
        canvas.create_text(leyenda_x + 194, leyenda_y, text="xₙ",
                           fill=COLOR["texto"], anchor="w")
        canvas.create_oval(leyenda_x + 236, leyenda_y - 4,
                           leyenda_x + 244, leyenda_y + 4,
                           fill="#B39DDB", outline="white")
        canvas.create_text(leyenda_x + 250, leyenda_y, text="xₙ₊₁",
                           fill=COLOR["texto"], anchor="w")
        if indice >= 0:
            paso = filas[indice]
            detalle = (f"Iteración {paso['k']} / {len(filas)}   ·   xi = {_formatear_numero(paso['xi'])}"
                       f"   ·   f(xi) = {_formatear_numero(paso['fxi'])}"
                       f"   ·   xi+1 = {_formatear_numero(paso.get('xi_siguiente'))}")
            if paso.get("motivo"):
                detalle += "   ·   " + paso["motivo"]
        else:
            detalle = ("Raíz inicial exacta; no se generaron tangentes." if datos["convergio"]
                       else "No se generaron iteraciones.")
        self.nr_info_paso.configure(text=detalle)
        if hasattr(self, "nr_slider"):
            self.nr_slider.configure(state="normal" if filas else "disabled")
            self.nr_boton_anterior.configure(state="normal" if indice > 0 else "disabled")
            self.nr_boton_siguiente.configure(state="normal" if indice < len(filas) - 1 else "disabled")

    def graficar_intervalo_biseccion(self):
        """Copia expresión e intervalo de búsqueda a la pestaña del graficador."""
        for campo, valor in ((self.g_expr, self.b_expr.get()), (self.g_xmin, self.b_a.get()), (self.g_xmax, self.b_b.get())):
            campo.delete(0, "end")
            campo.insert(0, valor)
        self.pestanas.set("Graficador")
        self.dibujar_grafica()

    def mostrar_guia(self):
        """Presenta instrucciones breves y criterios matemáticos de las cuatro pestañas."""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Cómo usar · Métodos numéricos")
        ventana.geometry("720x560")
        # En Windows la ventana nueva a veces queda detrás de la principal.
        ventana.after(150, ventana.lift)
        ventana.after(150, ventana.focus_force)
        caja = ctk.CTkTextbox(ventana, wrap="word", font=ctk.CTkFont(size=14))
        caja.pack(fill="both", expand=True, padx=18, pady=18)
        texto = (
            "SERIES DE MACLAURIN\n"
            "Introduce f(x), el punto x y una cantidad de términos entre 1 y "
            f"{MAX_TERMINOS_MACLAURIN}. El desarrollo se centra en cero; con N términos, "
            "el mayor orden es N−1. Usa ** para potencias y funciones permitidas como sin(x), "
            "cos(x), exp(x) y log(x). El resultado es un polinomio truncado: la convergencia "
            "depende de la función y del punto evaluado.\n\n"
            "BISECCIÓN\n"
            "Escribe f(x), a<b, tolerancia absoluta positiva y un máximo de iteraciones. "
            "Usa ** para potencias. La fila k registra sus extremos antes de actualizar. "
            "Eb=(b-a)/2; el cambio de signo no demuestra continuidad: comprueba que la función "
            "sea continua en todo el intervalo. La comparación con SciPy se omite por las reglas del proyecto.\n\n"
            "GRAFICADOR\n"
            "Escribe la misma sintaxis segura y un intervalo horizontal. Puedes fijar ambos "
            "límites verticales o dejarlos vacíos. Se muestrean 1200 puntos; se excluyen dominios "
            "inválidos y se separan segmentos ante saltos grandes. Tras resolver bisección, "
            "«Graficar este intervalo» pasa la función y el intervalo a esta pestaña.\n\n"
            "NOTACIÓN POSICIONAL\n"
            "Introduce un entero decimal para descomponerlo en potencias de 10 y convertirlo a "
            "binario, o introduce dígitos 0/1 para desarrollar potencias de 2. Si el número es "
            "negativo, el signo se conserva y las potencias se aplican a su valor absoluto.\n\n"
            "ERRORES NUMÉRICOS\n"
            "Revisa los ejemplos de float, épsilon, overflow, underflow y tipos de error. Introduce "
            "valor verdadero/aproximado para calcular errores. Para propagación, x se mide en "
            "radianes y Δy≈f'(x)Δx es una linealización que mejora con perturbaciones pequeñas."
        )
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def _crear_maclaurin(self, parent):
        """Añade el formulario y las vistas de resultados al conjunto de métodos numéricos."""
        marco = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        marco.grid_columnconfigure(0, weight=1)
        etiqueta(marco, "Serie de Maclaurin", tamano=19, negrita=True, color="texto").grid(
            row=0, column=0, sticky="w", padx=6, pady=(2, 0)
        )
        etiqueta(
            marco,
            "Aproxima f(x) con sus derivadas evaluadas en cero. Usa ** para potencias y funciones de la sintaxis segura.",
            tamano=12, color="gris", anchor="w", justify="left", wraplength=900,
        ).grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 10))
        entrada = Panel(marco, titulo="Datos de entrada", descripcion="N cuenta los términos desde n = 0.")
        entrada.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        fila_funcion = ctk.CTkFrame(entrada.contenido, fg_color="transparent")
        fila_funcion.pack(anchor="w", padx=8)
        self.mac_expr = self._entrada(fila_funcion, "Función f(x)", "exp(x)", 320)
        self.mac_x = self._entrada(fila_funcion, "Valor de x", "1", 130)
        self.mac_n = self._entrada(fila_funcion, "Cantidad de términos N", "5", 170)
        fila_botones = ctk.CTkFrame(entrada.contenido, fg_color="transparent")
        fila_botones.pack(anchor="w", padx=8, pady=(0, 6))
        boton_primario(fila_botones, "Calcular", self.calcular_maclaurin, width=120).pack(side="left", padx=(0, 6))
        boton_secundario(fila_botones, "Ejemplo", self.ejemplo_maclaurin, width=100).pack(side="left", padx=(0, 6))
        boton_secundario(fila_botones, "Limpiar", self.limpiar_maclaurin, width=100).pack(side="left")
        self.mac_estado = ctk.CTkLabel(
            marco, text="Introduce una función para obtener su desarrollo.",
            text_color=COLOR["gris"], anchor="w", justify="left", font=ctk.CTkFont(size=13),
        )
        self.mac_estado.grid(row=3, column=0, sticky="ew", padx=10, pady=4)
        self.mac_resultado = ctk.CTkFrame(marco, fg_color="transparent")
        self.mac_resultado.grid(row=4, column=0, sticky="nsew", padx=6, pady=(2, 10))

    def _vaciar_resultado_maclaurin(self):
        for widget in self.mac_resultado.winfo_children():
            widget.destroy()

    def ejemplo_maclaurin(self):
        for campo, valor in ((self.mac_expr, "exp(x)"), (self.mac_x, "1"), (self.mac_n, "5")):
            campo.delete(0, "end")
            campo.insert(0, valor)
        self._vaciar_resultado_maclaurin()
        self.mac_estado.configure(text="Ejemplo cargado. Pulsa Calcular para ver el desarrollo.",
                                  text_color=COLOR["gris"])

    def limpiar_maclaurin(self):
        for campo, valor in ((self.mac_expr, ""), (self.mac_x, "0"), (self.mac_n, "5")):
            campo.delete(0, "end")
            if valor:
                campo.insert(0, valor)
        self._vaciar_resultado_maclaurin()
        self.mac_estado.configure(text="Formulario limpiado.", text_color=COLOR["gris"])

    def calcular_maclaurin(self):
        self._vaciar_resultado_maclaurin()
        try:
            expresion = self.mac_expr.get().strip()
            if not expresion:
                raise ValueError("Escribe una función matemática en f(x).")
            x = _leer_real(self.mac_x.get(), "El valor de x")
            numero_terminos = _leer_entero(self.mac_n.get(), "La cantidad de términos")
            datos = calcular_maclaurin(expresion, x, numero_terminos)
        except (ValueError, OverflowError) as error:
            self.mac_estado.configure(text="Datos inválidos o función no evaluable en cero.",
                                      text_color=COLOR["mal"])
            self._mostrar_error(error)
            return
        self._mostrar_resultado_maclaurin(datos)

    def _mostrar_resultado_maclaurin(self, datos):
        self.mac_estado.configure(
            text=f"Polinomio P_{datos['numero_terminos']} calculado en x = {_formatear_numero(datos['x'])}.",
            text_color=COLOR["ok"],
        )
        selector = ctk.CTkSegmentedButton(
            self.mac_resultado, values=("Resumen", "Términos", "Procedimiento"),
            command=self._cambiar_vista_maclaurin,
        )
        selector.pack(pady=(0, 5))
        area = ctk.CTkFrame(self.mac_resultado, fg_color="transparent")
        area.pack(fill="both", expand=True)
        area.grid_rowconfigure(0, weight=1)
        area.grid_columnconfigure(0, weight=1)
        textos = {
            "Resumen": self._resumen_maclaurin(datos),
            "Términos": _texto_terminos_maclaurin(datos),
            "Procedimiento": _texto_procedimiento_maclaurin(datos),
        }
        self.mac_paneles_vista = {}
        for nombre, texto in textos.items():
            panel = ctk.CTkFrame(area, fg_color="transparent")
            panel.grid(row=0, column=0, sticky="nsew")
            caja = ctk.CTkTextbox(
                panel, wrap="word", font=fuente_mono(12), fg_color=COLOR["suave"],
                text_color=COLOR["texto"], border_width=1, border_color=COLOR["borde"], corner_radius=10,
            )
            caja.pack(fill="both", expand=True, padx=4, pady=4)
            caja.insert("1.0", texto)
            caja.configure(state="disabled")
            self.mac_paneles_vista[nombre] = panel
        selector.configure(command=self._cambiar_vista_maclaurin)
        selector.set("Resumen")
        self.mac_selector_vista = selector
        self._cambiar_vista_maclaurin("Resumen")

    @staticmethod
    def _resumen_maclaurin(datos):
        lineas = [
            f"Función: f(x) = {datos['expresion']}",
            f"Términos: N = {datos['numero_terminos']} (órdenes 0 a {datos['numero_terminos'] - 1})",
            f"Evaluación: x = {_formatear_numero(datos['x'])}",
            f"Polinomio: P_{datos['numero_terminos']}(x) = {datos['polinomio']}",
            f"Aproximación: P_N(x) = {_formatear_numero(datos['aproximacion'])}",
        ]
        if datos["valor_real"] is None:
            lineas.append(datos["aviso_evaluacion"])
        else:
            lineas.extend((
                f"Valor real de la función: f(x) = {_formatear_numero(datos['valor_real'])}",
                f"Error absoluto: {_formatear_numero(datos['error_absoluto'])}",
                "Error relativo porcentual: " + (
                    datos["aviso_error"] if datos["aviso_error"] else
                    "no definido porque el valor real es cero."
                    if datos["error_relativo_porcentual"] is None else
                    f"{_formatear_numero(datos['error_relativo_porcentual'])}%"
                ),
            ))
            if datos["error_absoluto"] == 0:
                lineas.append("Conclusión: el polinomio coincide con f(x) en el punto evaluado.")
            elif datos["error_absoluto"] is not None:
                lineas.append(
                    "Conclusión: el polinomio truncado difiere de f(x) en el punto evaluado; "
                    "la diferencia depende de la función, x y N."
                )
            else:
                lineas.append("Conclusión: no fue posible cuantificar el error dentro del rango numérico finito.")
        lineas.extend(("", datos["nota_convergencia"]))
        if datos["aviso_convergencia"]:
            lineas.insert(-1, datos["aviso_convergencia"])
        return "\n".join(lineas)

    def _cambiar_vista_maclaurin(self, nombre):
        panel = getattr(self, "mac_paneles_vista", {}).get(nombre)
        if panel is not None:
            panel.tkraise()

    def _crear_graficador(self, parent):
        marco = ctk.CTkFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=12, pady=10)
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(2, weight=1)

        configuracion = ctk.CTkFrame(
            marco, fg_color=COLOR["tarjeta"], corner_radius=12,
            border_width=1, border_color=COLOR["borde"],
        )
        configuracion.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        configuracion.grid_columnconfigure(0, weight=4, uniform="grafica_campos")
        for columna in range(1, 5):
            configuracion.grid_columnconfigure(columna, weight=1, uniform="grafica_campos")
        etiqueta(configuracion, "Configuración de la gráfica", tamano=15,
                 negrita=True, color="texto").grid(
            row=0, column=0, columnspan=5, sticky="w", padx=14, pady=(12, 4)
        )

        def crear_campo(columna, titulo, inicial, ancho):
            grupo = ctk.CTkFrame(configuracion, fg_color="transparent")
            grupo.grid(row=1, column=columna, sticky="ew", padx=8, pady=(2, 10))
            etiqueta(grupo, titulo, tamano=11, color="gris").pack(anchor="w", padx=2)
            campo = ctk.CTkEntry(grupo, width=ancho)
            campo.insert(0, str(inicial))
            campo.pack(fill="x", expand=True, pady=(4, 0))
            return campo

        self.g_expr = crear_campo(0, "Función f(x)", "1/x", 300)
        self.g_xmin = crear_campo(1, "x mínimo", "-5", 90)
        self.g_xmax = crear_campo(2, "x máximo", "5", 90)
        self.g_ymin = crear_campo(3, "y mínimo · opcional", "", 110)
        self.g_ymax = crear_campo(4, "y máximo · opcional", "", 110)
        boton_primario(configuracion, "Graficar", self.dibujar_grafica, width=130).grid(
            row=2, column=0, sticky="w", padx=14, pady=(0, 12)
        )
        etiqueta(configuracion, "Deja ambos límites y vacíos para ajustar la escala automáticamente.",
                 tamano=11, color="gris").grid(
            row=2, column=1, columnspan=4, sticky="w", padx=8, pady=(0, 12)
        )

        panel_grafica = ctk.CTkFrame(
            marco, fg_color=COLOR["tarjeta"], corner_radius=12,
            border_width=1, border_color=COLOR["borde"],
        )
        panel_grafica.grid(row=2, column=0, sticky="nsew")
        panel_grafica.grid_columnconfigure(0, weight=1)
        panel_grafica.grid_rowconfigure(1, weight=1)
        encabezado = ctk.CTkFrame(panel_grafica, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 2))
        encabezado.grid_columnconfigure(0, weight=1)
        etiqueta(encabezado, "Vista gráfica", tamano=15, negrita=True, color="texto").grid(
            row=0, column=0, sticky="w"
        )
        self.g_estado = etiqueta(encabezado, "Ingresa una función y pulsa Graficar.",
                                 tamano=11, color="gris")
        self.g_estado.grid(row=0, column=1, sticky="e", padx=(10, 0))
        self.canvas = tk.Canvas(
            panel_grafica, background=COLOR["fondo_secundario"],
            highlightthickness=0, height=420,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.canvas.bind("<Configure>", lambda _evento: self._repintar_ultima_grafica())

    def dibujar_grafica(self):
        """Muestrea la función y dibuja cuadrícula, ejes, curva y resultado de bisección."""
        try:
            ymin_txt, ymax_txt = self.g_ymin.get().strip(), self.g_ymax.get().strip()
            if bool(ymin_txt) != bool(ymax_txt):
                raise ValueError("Ingrese ambos límites verticales o deje los dos vacíos.")
            limites = (_leer_real(ymin_txt, "y mínimo"), _leer_real(ymax_txt, "y máximo")) if ymin_txt else None
            self.ultima_muestra = muestrear_funcion(
                self.g_expr.get(), self.g_xmin.get(), self.g_xmax.get(), limites_y=limites
            )
        except (ValueError, OverflowError) as error:
            self._mostrar_error(error)
            self.g_estado.configure(text="No se pudo graficar; revisa la función y los límites.",
                                    text_color=COLOR["mal"])
            return
        cantidad_segmentos = len(self.ultima_muestra["segmentos"])
        estado = ("Sin puntos reales finitos en el intervalo." if not cantidad_segmentos else
                  f"Función muestreada · {cantidad_segmentos} segmento(s)")
        self.g_estado.configure(text=estado,
                                text_color=COLOR["advertencia"] if not cantidad_segmentos else COLOR["ok"])
        self._repintar_ultima_grafica()

    def _repintar_ultima_grafica(self):
        """Dibuja la última muestra usando el tamaño actual del lienzo."""
        if self.ultima_muestra is None:
            return
        muestra, canvas = self.ultima_muestra, self.canvas
        ancho, alto = max(200, canvas.winfo_width()), max(180, canvas.winfo_height())
        margen = 48
        valores = [y for segmento in muestra["segmentos"] for _, y in segmento]
        canvas.delete("all")
        if not valores:
            canvas.create_text(ancho / 2, alto / 2, text="No hay puntos reales finitos en el dominio.", fill="#E4E4E7")
            return
        if muestra["y_min"] is None:
            ymin, ymax = min(valores), max(valores)
            if ymin == ymax:
                ymin, ymax = ymin - 1, ymax + 1
            else:
                espacio = (ymax - ymin) * 0.08
                ymin, ymax = ymin - espacio, ymax + espacio
        else:
            ymin, ymax = muestra["y_min"], muestra["y_max"]
        xmin, xmax = muestra["x_min"], muestra["x_max"]
        px = lambda x: margen + (x - xmin) * (ancho - 2 * margen) / (xmax - xmin)
        py = lambda y: alto - margen - (y - ymin) * (alto - 2 * margen) / (ymax - ymin)
        for indice in range(6):
            gx = margen + indice * (ancho - 2 * margen) / 5
            gy = margen + indice * (alto - 2 * margen) / 5
            canvas.create_line(gx, margen, gx, alto - margen, fill="#303036")
            canvas.create_line(margen, gy, ancho - margen, gy, fill="#303036")
            xv = xmin + indice * (xmax - xmin) / 5
            yv = ymax - indice * (ymax - ymin) / 5
            canvas.create_text(gx, alto - margen + 17, text=f"{xv:.3g}", fill=COLOR["gris"])
            canvas.create_text(margen - 24, gy, text=f"{yv:.3g}", fill=COLOR["gris"])
        if xmin <= 0 <= xmax:
            canvas.create_line(px(0), margen, px(0), alto - margen, fill=COLOR["deshabilitado"], width=2)
        if ymin <= 0 <= ymax:
            canvas.create_line(margen, py(0), ancho - margen, py(0), fill=COLOR["deshabilitado"], width=2)
        for segmento in muestra["segmentos"]:
            coords = [coordenada for x, y in segmento for coordenada in (px(x), py(y))]
            if len(coords) >= 4:
                canvas.create_line(*coords, fill=COLOR["verde"], width=2, smooth=False)
        canvas.create_text(ancho / 2, 14, text=f"f(x) = {self.g_expr.get()}",
                           fill=COLOR["texto"], font=("Segoe UI", 12, "bold"),
                           width=max(160, ancho - 100))
        canvas.create_text(ancho / 2, alto - 9, text="x", fill=COLOR["texto"])
        canvas.create_text(13, alto / 2, text="f(x)", fill=COLOR["texto"], angle=90)
        canvas.create_rectangle(ancho - 160, 18, ancho - 142, 27, fill=COLOR["verde"], outline="")
        canvas.create_text(ancho - 136, 23, text="f(x)", fill=COLOR["texto"], anchor="w")
        resultado = self.ultimo_resultado
        if resultado and resultado["expresion"] == self.g_expr.get().strip():
            xr, fr = resultado["raiz"], resultado["f_raiz"]
            a0, b0 = resultado["a"], resultado["b"]
            if xmin <= a0 <= xmax and xmin <= b0 <= xmax and ymin <= 0 <= ymax:
                # La guía pide identificar qué intervalo se dibuja: es el inicial [a, b].
                canvas.create_line(px(a0), py(0), px(b0), py(0), fill=COLOR["advertencia"], width=4)
                canvas.create_text((px(a0) + px(b0)) / 2, py(0) + 16, fill=COLOR["advertencia"],
                                   text=f"intervalo inicial de bisección [{a0:g}, {b0:g}]")
            if xmin <= xr <= xmax and ymin <= fr <= ymax:
                canvas.create_oval(px(xr)-5, py(fr)-5, px(xr)+5, py(fr)+5,
                                   fill=COLOR["advertencia"], outline=COLOR["texto"])
                canvas.create_text(px(xr)+9, py(fr)-10, text=f"raíz ≈ {xr:.6g}",
                                   fill=COLOR["advertencia"], anchor="w")

    def _crear_notacion(self, parent):
        marco = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        marco.grid_columnconfigure((0, 1), weight=1, uniform="notacion_operaciones")
        etiqueta(marco, "Conversiones entre decimal y binario", tamano=19,
                 negrita=True, color="texto").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 2)
        )
        etiqueta(marco, "Trabaja con enteros; las descomposiciones muestran los dígitos, "
                 "sus potencias y la comprobación del resultado.", tamano=12,
                 color="gris", justify="left", anchor="w", wraplength=850).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 10)
        )

        decimal = Panel(
            marco, titulo="Decimal → binario",
            descripcion="Introduce un entero decimal para obtener su desarrollo en base 10 y su equivalente binario.",
        )
        decimal.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        decimal.contenido.grid_columnconfigure(0, weight=1)
        etiqueta(decimal.contenido, "Número decimal", tamano=12,
                 color="texto", negrita=True).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.n_decimal = ctk.CTkEntry(decimal.contenido, height=38, font=fuente_mono(14))
        self.n_decimal.insert(0, "84506")
        self.n_decimal.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        boton_primario(decimal.contenido, "Descomponer y convertir",
                       self.convertir_decimal).grid(row=2, column=0, sticky="ew")

        binario = Panel(
            marco, titulo="Binario → decimal",
            descripcion="Usa únicamente dígitos 0 y 1, con signo opcional, para obtener el desarrollo en base 2 y el entero decimal.",
        )
        binario.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        binario.contenido.grid_columnconfigure(0, weight=1)
        etiqueta(binario.contenido, "Número binario", tamano=12,
                 color="texto", negrita=True).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.n_binario = ctk.CTkEntry(binario.contenido, height=38, font=fuente_mono(14))
        self.n_binario.insert(0, "11110011")
        self.n_binario.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        boton_secundario(binario.contenido, "Convertir a decimal",
                         self.convertir_binario).grid(row=2, column=0, sticky="ew")

        self.n_resultado = Panel(marco, titulo="Resultado",
            descripcion="La equivalencia y el procedimiento aparecerán aquí al realizar una conversión.")
        self.n_resultado.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=(8, 5))
        self.n_resultado.contenido.grid_columnconfigure(0, weight=1)
        self.n_resultado.contenido.grid_remove()

    def convertir_decimal(self):
        """Muestra forma posicional en base 10 y su conversión exacta a base 2."""
        try:
            texto = self.n_decimal.get().strip()
            valor = _leer_entero(texto, "El valor decimal")
            decimal, binario = descomponer_decimal(valor), decimal_a_binario(valor)
        except ValueError as error:
            self._mostrar_error(error)
            return
        signo = "El signo se conserva; las potencias se aplican al valor absoluto.\n" if valor < 0 else ""
        texto = (f"Base de origen: 10\n{signo}({valor})₁₀ = {decimal['descomposicion']}\n"
                 f"Suma posicional = {valor}\n\nBase del resultado: 2\n"
                 f"({valor})₁₀ = ({binario['binario']})₂\n"
                 f"Comprobación: la conversión inversa produce {binario['equivalente']}₁₀.")
        self._presentar_resultado_notacion(
            "Conversión decimal → binario", binario["binario"],
            f"({valor})₁₀ = ({binario['binario']})₂",
            f"Base de origen: 10 · Base de destino: 2 · Valor original: {valor}", texto,
        )

    def convertir_binario(self):
        """Muestra la expansión binaria y su suma posicional decimal."""
        try:
            datos = binario_a_decimal(self.n_binario.get())
        except ValueError as error:
            self._mostrar_error(error)
            return
        signo = "El signo se conserva y la expansión se realiza sobre el valor absoluto.\n" if datos["decimal"] < 0 else ""
        suma = " + ".join(str(valor) for valor in datos["parciales"])
        if datos["decimal"] < 0:
            suma = f"-({suma})"
        # Sin ceros a la izquierda: es lo que devuelve de verdad la conversión inversa.
        inverso = ("-" if datos["decimal"] < 0 else "") + format(abs(datos["decimal"]), "b")
        texto = (f"Base de origen: 2\n{signo}({datos['binario']})₂ = {datos['descomposicion']}\n"
                 f"= {suma} = ({datos['decimal']})₁₀\n"
                 f"Comprobación: decimal a binario devuelve {inverso}.")
        self._presentar_resultado_notacion(
            "Conversión binario → decimal", str(datos["decimal"]),
            f"({datos['binario']})₂ = ({datos['decimal']})₁₀",
            f"Base de origen: 2 · Base de destino: 10 · Dígitos: {len(datos['binario'].lstrip('+-'))}", texto,
        )

    def _presentar_resultado_notacion(self, titulo, valor, equivalencia, detalles, procedimiento):
        """Separa el valor convertido de su desarrollo, conservando el texto calculado."""
        contenido = self.n_resultado.contenido
        for widget in contenido.winfo_children():
            widget.destroy()
        tarjeta = TarjetaResultado(
            contenido, titulo, valor, equivalencia,
            estado=("Conversión realizada", "success"),
        )
        tarjeta.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tarjeta.valor.configure(font=fuente_mono(20, negrita=True), wraplength=780)
        etiqueta(contenido, detalles, tamano=11, color="gris", anchor="w",
                 justify="left", wraplength=820).grid(row=1, column=0, sticky="w", pady=(0, 8))
        desarrollo = Panel(contenido, titulo="Desarrollo posicional",
            descripcion="Descomposición, suma y comprobación de la conversión.")
        desarrollo.grid(row=2, column=0, sticky="nsew")
        desarrollo.contenido.grid_columnconfigure(0, weight=1)
        caja = ctk.CTkTextbox(
            desarrollo.contenido, height=150, wrap="word",
            font=fuente_mono(12), fg_color=COLOR["suave"],
            text_color=COLOR["texto"], border_width=1,
            border_color=COLOR["borde"], corner_radius=10,
        )
        caja.grid(row=0, column=0, sticky="nsew")
        caja.insert("1.0", procedimiento)
        caja.configure(state="disabled")
        self.n_resultado.contenido.grid()

    def _crear_errores(self, parent):
        marco = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        marco.grid_columnconfigure(0, weight=1)
        etiqueta(marco, "Errores numéricos", tamano=19, negrita=True,
                 color="texto").grid(row=0, column=0, sticky="w", padx=6, pady=(2, 0))
        etiqueta(marco, "Compara valores y estudia cómo las aproximaciones afectan los cálculos.",
                 tamano=12, color="gris", anchor="w", justify="left",
                 wraplength=900).grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 10))

        punto = analizar_punto_flotante()
        flotante = Panel(
            marco, titulo="Representación en punto flotante",
            descripcion="Ejemplos reproducibles de precisión finita; los valores se generan con el análisis existente.",
        )
        flotante.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        cuerpo_float = flotante.contenido
        cuerpo_float.grid_columnconfigure((0, 1, 2), weight=1, uniform="errores_float")
        ejemplos = (
            ("0.1 + 0.2", f"{punto['suma']!r} · igual a 0.3: {punto['igual_a_03']}"),
            ("Diferencia respecto a 0.3", f"{punto['diferencia']:.18g}"),
            ("Épsilon de máquina", f"{punto['epsilon']:.17g}"),
            ("Overflow · 1e308 × 1e308", str(punto["overflow"])),
            ("Underflow · 1e-300 × 1e-300", str(punto["underflow"])),
            ("Pérdida · 1e16 + 1 − 1e16", str(punto["perdida"])),
        )
        for indice, (titulo, valor) in enumerate(ejemplos):
            fila, columna = divmod(indice, 3)
            metrica = TarjetaResultado(cuerpo_float, titulo, valor)
            metrica.grid(row=fila, column=columna, sticky="ew", padx=4, pady=4)
        etiqueta(cuerpo_float, punto["epsilon_explicacion"], tamano=11,
                 color="gris", anchor="w", justify="left", wraplength=900).grid(
            row=2, column=0, columnspan=3, sticky="ew", padx=4, pady=(6, 2)
        )
        etiqueta(cuerpo_float,
                 "Overflow: la magnitud supera el rango representable y aquí produce infinito. "
                 "Underflow: la magnitud cae por debajo del rango y aquí se redondea a cero. "
                 f"{punto['razon_binaria']}", tamano=11, color="texto", anchor="w",
                 justify="left", wraplength=900).grid(
            row=3, column=0, columnspan=3, sticky="ew", padx=4, pady=(2, 8)
        )
        definiciones = Panel(cuerpo_float, titulo="Tipos de error",
                             descripcion="Distinciones conceptuales incluidas en el módulo.")
        definiciones.grid(row=4, column=0, columnspan=3, sticky="ew", padx=4, pady=(4, 2))
        for fila, (nombre, descripcion) in enumerate(resumen_tipos_error()):
            etiqueta(definiciones.contenido, nombre, tamano=12, negrita=True,
                     color="texto").grid(row=fila, column=0, sticky="nw", padx=(0, 10), pady=3)
            etiqueta(definiciones.contenido, descripcion, tamano=11, color="gris",
                     justify="left", anchor="w", wraplength=780).grid(
                row=fila, column=1, sticky="ew", pady=3
            )
        definiciones.contenido.grid_columnconfigure(1, weight=1)

        panel_error = Panel(
            marco, titulo="Error entre valor verdadero y aproximado",
            descripcion="Calcula error absoluto, relativo y porcentual. Si el valor verdadero es cero, el relativo y el porcentual quedan sin definir.",
        )
        panel_error.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        entrada_error = panel_error.contenido
        entrada_error.grid_columnconfigure((0, 1), weight=1, uniform="errores_campos")
        self.e_verdadero = self._campo_error(entrada_error, "Valor verdadero", "10", 0)
        self.e_aproximado = self._campo_error(entrada_error, "Valor aproximado", "9.8", 1)
        boton_primario(entrada_error, "Calcular errores", self.calcular_errores).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self.e_resultado = Panel(marco, titulo="Resultados de la comparación",
                                 descripcion="Los errores y su sustitución aparecerán al calcular.")
        self.e_resultado.grid(row=4, column=0, sticky="ew", padx=5, pady=(0, 8))
        self.e_resultado.contenido.grid_columnconfigure((0, 1, 2), weight=1, uniform="errores_resultado")
        self.e_resultado.contenido.grid_remove()

        panel_propagacion = Panel(
            marco, titulo="Propagación general de errores",
            descripcion="Introduce una función y una incertidumbre absoluta para cada variable; selecciona error máximo o incertidumbre estadística. Para una variable, especifica su Perturbación Δx.",
        )
        panel_propagacion.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        entrada_propagacion = panel_propagacion.contenido
        entrada_propagacion.grid_columnconfigure((0, 1, 2), weight=1, uniform="propagacion_general")
        etiqueta(entrada_propagacion, "Función f(variables)", tamano=11, color="gris").grid(
            row=0, column=0, sticky="w", padx=5, pady=(3, 0)
        )
        self.pe_funcion = ctk.CTkEntry(entrada_propagacion, height=36, font=fuente_mono(13))
        self.pe_funcion.insert(0, "sin(x) + x**2")
        self.pe_funcion.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 5))
        etiqueta(entrada_propagacion, "Método de propagación", tamano=11, color="gris").grid(
            row=2, column=0, sticky="w", padx=5, pady=(2, 0)
        )
        self.pe_selector_metodo = ctk.CTkSegmentedButton(
            entrada_propagacion, values=("Error máximo", "Incertidumbre estadística")
        )
        self.pe_selector_metodo.grid(row=3, column=0, columnspan=3, sticky="w", padx=5, pady=(3, 7))
        self.pe_selector_metodo.set("Error máximo")
        self.pe_estado_variables = ctk.CTkLabel(
            entrada_propagacion, text="", text_color=COLOR["gris"], anchor="w", justify="left",
            font=ctk.CTkFont(size=11),
        )
        self.pe_estado_variables.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 3))
        self.pe_marco_variables = ctk.CTkFrame(entrada_propagacion, fg_color="transparent")
        self.pe_marco_variables.grid(row=5, column=0, columnspan=3, sticky="ew", padx=2)
        for columna in range(3):
            self.pe_marco_variables.grid_columnconfigure(columna, weight=1, uniform="campos_variable")
        self.pe_campos_variables = {}
        self.pe_funcion.bind("<KeyRelease>", self._actualizar_campos_propagacion, add="+")
        self._actualizar_campos_propagacion()
        fila_botones_propagacion = ctk.CTkFrame(entrada_propagacion, fg_color="transparent")
        fila_botones_propagacion.grid(row=6, column=0, columnspan=3, sticky="w", padx=5, pady=(5, 2))
        boton_primario(fila_botones_propagacion, "Calcular propagación", self.calcular_propagacion_general).pack(
            side="left", padx=(0, 6)
        )
        boton_secundario(fila_botones_propagacion, "Ejemplo", self.ejemplo_propagacion_general).pack(
            side="left", padx=(0, 6)
        )
        boton_secundario(fila_botones_propagacion, "Limpiar", self.limpiar_propagacion_general).pack(side="left")
        self.e_resultado_propagacion = Panel(
            marco, titulo="Resultados de propagación",
            descripcion="Cambios observados y linealización calculada para los datos ingresados.",
        )
        self.e_resultado_propagacion.grid(row=6, column=0, sticky="ew", padx=5, pady=(0, 8))
        self.e_resultado_propagacion.contenido.grid_columnconfigure((0, 1, 2), weight=1, uniform="propagacion_resultado")
        self.e_resultado_propagacion.contenido.grid_remove()

    @staticmethod
    def _campo_error(parent, titulo, inicial, columna):
        grupo = ctk.CTkFrame(parent, fg_color="transparent")
        grupo.grid(row=0, column=columna, sticky="ew", padx=5, pady=3)
        etiqueta(grupo, titulo, tamano=11, color="gris").pack(anchor="w", pady=(0, 3))
        campo = ctk.CTkEntry(grupo, height=36, font=fuente_mono(13))
        campo.insert(0, inicial)
        campo.pack(fill="x", expand=True)
        return campo

    @staticmethod
    def _limpiar_panel_error(panel):
        for widget in panel.contenido.winfo_children():
            widget.destroy()

    @staticmethod
    def _tarjeta_error(parent, titulo, valor, detalle=None):
        tarjeta = TarjetaResultado(parent, titulo, valor, detalle)
        return tarjeta

    def calcular_errores(self):
        """Calcula y presenta errores absoluto, relativo y porcentual."""
        try:
            datos = calcular_errores(self.e_verdadero.get(), self.e_aproximado.get())
        except ValueError as error:
            self._mostrar_error(error)
            return
        relativo = "No definido porque el valor verdadero es cero." if datos["relativo"] is None else f"{datos['relativo']:.10g}"
        porcentaje = "No definido." if datos["porcentual"] is None else f"{datos['porcentual']:.10g}%"
        panel = self.e_resultado
        contenido = panel.contenido
        self._limpiar_panel_error(panel)
        valores = (
            ("Valor verdadero", str(datos["verdadero"])),
            ("Valor aproximado", str(datos["aproximado"])),
            ("Error absoluto", str(datos["absoluto"])),
            ("Error relativo", relativo),
            ("Error porcentual", porcentaje),
        )
        for indice, (titulo, valor) in enumerate(valores):
            fila, columna = divmod(indice, 3)
            self._tarjeta_error(contenido, titulo, valor).grid(
                row=fila, column=columna, sticky="ew", padx=4, pady=4
            )
        detalle = (
            f"Error absoluto = |{datos['verdadero']} − {datos['aproximado']}| = {datos['absoluto']}\n"
            f"Error relativo = {relativo}\nError porcentual = {porcentaje}"
        )
        self._procedimiento_error(contenido, "Cálculo de errores", detalle, 2, 3)
        contenido.grid()

    def calcular_propagacion(self):
        """Calcula cambio real, aproximación lineal y su diferencia absoluta."""
        try:
            datos = propagar_error(self.e_x.get(), self.e_dx.get())
        except (ValueError, OverflowError) as error:
            self._mostrar_error(error)
            return
        texto = (
            f"f(x) = {datos['f_x']:.12g}\n"
            f"f(x + Δx) = {datos['f_perturbado']:.12g}\n"
            f"Cambio real Δy = f(x+Δx) − f(x) = {datos['delta_y_real']:.12g}\n"
            f"f'(x) = cos(x) + 2x = {datos['derivada']:.12g}\n"
            f"Cambio aproximado Δy ≈ f'(x)·Δx = {datos['delta_y_aproximado']:.12g}\n"
            f"Diferencia absoluta = {datos['diferencia_absoluta']:.12g}\n"
            "La derivada proporciona una linealización de primer orden; suele aproximar mejor para perturbaciones pequeñas."
        )
        panel = self.e_resultado_propagacion
        contenido = panel.contenido
        self._limpiar_panel_error(panel)
        valores = (
            ("f(x)", f"{datos['f_x']:.12g}"),
            ("f(x + Δx)", f"{datos['f_perturbado']:.12g}"),
            ("Cambio real · Δy", f"{datos['delta_y_real']:.12g}"),
            ("Cambio aproximado · Δy", f"{datos['delta_y_aproximado']:.12g}"),
            ("Diferencia absoluta", f"{datos['diferencia_absoluta']:.12g}"),
            ("Derivada · f'(x)", f"{datos['derivada']:.12g}"),
        )
        for indice, (titulo, valor) in enumerate(valores):
            fila, columna = divmod(indice, 3)
            self._tarjeta_error(contenido, titulo, valor).grid(
                row=fila, column=columna, sticky="ew", padx=4, pady=4
            )
        self._procedimiento_error(contenido, "Desarrollo de la propagación", texto, 2, 3)
        contenido.grid()

    def _actualizar_campos_propagacion(self, _evento=None):
        """Sincroniza campos con variables de una expresión válida y conserva valores coincidentes."""
        expresion = self.pe_funcion.get().strip()
        try:
            variables = identificar_variables(expresion)
        except ValueError as error:
            self.pe_estado_variables.configure(
                text=f"Completa una expresión válida para actualizar las variables. {error}",
                text_color=COLOR["advertencia"],
            )
            return False
        anteriores = {
            nombre: {clave: campo.get() for clave, campo in campos.items()}
            for nombre, campos in self.pe_campos_variables.items()
        }
        for widget in self.pe_marco_variables.winfo_children():
            widget.destroy()
        self.pe_campos_variables = {}
        for columna, titulo in enumerate(("Variable", "Valor", "Incertidumbre absoluta")):
            etiqueta(self.pe_marco_variables, titulo, tamano=11, negrita=True, color="texto").grid(
                row=0, column=columna, sticky="w", padx=5, pady=(2, 4)
            )
        for fila, nombre in enumerate(variables, start=1):
            etiqueta(self.pe_marco_variables, nombre, tamano=12, color="texto").grid(
                row=fila, column=0, sticky="w", padx=5, pady=3
            )
            valor = ctk.CTkEntry(self.pe_marco_variables, height=32, font=fuente_mono(12))
            delta = ctk.CTkEntry(self.pe_marco_variables, height=32, font=fuente_mono(12))
            valor_inicial, delta_inicial = ("0.5", "0.01") if nombre == "x" else ("0", "0.01")
            valor.insert(0, anteriores.get(nombre, {}).get("valor", valor_inicial))
            delta.insert(0, anteriores.get(nombre, {}).get("incertidumbre", delta_inicial))
            valor.grid(row=fila, column=1, sticky="ew", padx=5, pady=3)
            delta.grid(row=fila, column=2, sticky="ew", padx=5, pady=3)
            self.pe_campos_variables[nombre] = {"valor": valor, "incertidumbre": delta}
        self.pe_estado_variables.configure(
            text=(f"Variables detectadas: {', '.join(variables)}." if variables else
                  "La expresión es constante; no requiere valores ni incertidumbres."),
            text_color=COLOR["gris"],
        )
        return True

    def ejemplo_propagacion_general(self):
        self.pe_funcion.delete(0, "end")
        self.pe_funcion.insert(0, "x**2*y + 3*y")
        self._actualizar_campos_propagacion()
        for nombre, valor, delta in (("x", "2", "0.1"), ("y", "3", "0.2")):
            campos = self.pe_campos_variables.get(nombre)
            if campos:
                campos["valor"].delete(0, "end")
                campos["valor"].insert(0, valor)
                campos["incertidumbre"].delete(0, "end")
                campos["incertidumbre"].insert(0, delta)
        self._limpiar_resultado_propagacion_general()

    def limpiar_propagacion_general(self):
        self.pe_funcion.delete(0, "end")
        for widget in self.pe_marco_variables.winfo_children():
            widget.destroy()
        self.pe_campos_variables = {}
        self.pe_selector_metodo.set("Error máximo")
        self.pe_estado_variables.configure(text="Formulario limpiado.", text_color=COLOR["gris"])
        self._limpiar_resultado_propagacion_general()

    def _limpiar_resultado_propagacion_general(self):
        self._limpiar_panel_error(self.e_resultado_propagacion)

    def calcular_propagacion_general(self):
        """Valida entradas por variable y muestra ambas estimaciones de propagación."""
        try:
            if not self._actualizar_campos_propagacion():
                raise ValueError("Corrige la función antes de calcular.")
            valores = {
                nombre: campos["valor"].get()
                for nombre, campos in self.pe_campos_variables.items()
            }
            incertidumbres = {
                nombre: campos["incertidumbre"].get()
                for nombre, campos in self.pe_campos_variables.items()
            }
            seleccion = self.pe_selector_metodo.get()
            metodo = "estadistico" if seleccion == "Incertidumbre estadística" else "maximo"
            datos = propagar_errores(self.pe_funcion.get(), valores, incertidumbres, metodo)
        except (ValueError, OverflowError) as error:
            self.pe_estado_variables.configure(text="No se pudo calcular la propagación.", text_color=COLOR["mal"])
            self._mostrar_error(error)
            return
        self._mostrar_resultado_propagacion_general(datos)

    def _mostrar_resultado_propagacion_general(self, datos):
        self.pe_estado_variables.configure(
            text=f"Cálculo completado con el método: {datos['nombre_metodo']}.",
            text_color=COLOR["ok"],
        )
        contenido = self.e_resultado_propagacion.contenido
        self._limpiar_panel_error(self.e_resultado_propagacion)
        selector = ctk.CTkSegmentedButton(
            contenido,
            values=("Resumen", "Datos", "Procedimiento", "Contribuciones"),
            command=self._cambiar_vista_propagacion_general,
        )
        selector.grid(row=0, column=0, columnspan=3, pady=(2, 7))
        area = ctk.CTkFrame(contenido, fg_color="transparent")
        area.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=4, pady=3)
        contenido.grid_rowconfigure(1, weight=1)
        contenido.grid_columnconfigure(0, weight=1)
        textos = {
            "Resumen": self._resumen_propagacion_general(datos),
            "Datos": self._datos_propagacion_general(datos),
            "Procedimiento": self._procedimiento_propagacion_general(datos),
            "Contribuciones": self._contribuciones_propagacion_general(datos),
        }
        self.pe_paneles_resultado = {}
        area.grid_rowconfigure(0, weight=1)
        area.grid_columnconfigure(0, weight=1)
        for nombre, texto in textos.items():
            panel = ctk.CTkFrame(area, fg_color="transparent")
            panel.grid(row=0, column=0, sticky="nsew")
            caja = ctk.CTkTextbox(
                panel, height=190, wrap="word", font=fuente_mono(12),
                fg_color=COLOR["suave"], text_color=COLOR["texto"],
                border_width=1, border_color=COLOR["borde"], corner_radius=10,
            )
            caja.pack(fill="both", expand=True, padx=4, pady=4)
            caja.insert("1.0", texto)
            caja.configure(state="disabled")
            self.pe_paneles_resultado[nombre] = panel
        self.pe_selector_resultado = selector
        selector.set("Resumen")
        self._cambiar_vista_propagacion_general("Resumen")
        contenido.grid()

    def _cambiar_vista_propagacion_general(self, nombre):
        panel = getattr(self, "pe_paneles_resultado", {}).get(nombre)
        if panel is not None:
            panel.tkraise()

    @staticmethod
    def _resumen_propagacion_general(datos):
        inferior, superior = datos["intervalo"]
        relativa = ("No definida porque f = 0." if datos["error_relativo_porcentual"] is None
                    else f"{datos['error_relativo_porcentual']:.10g}%")
        variables_texto = ", ".join(
            "{}={:.10g} ± {:.10g}".format(
                nombre, datos["valores"][nombre], datos["incertidumbres"][nombre]
            )
            for nombre in datos["variables"]
        ) or "ninguna"
        return "\n".join((
            f"Función: f = {datos['expresion']}",
            f"Variables: {variables_texto}",
            f"Método: {datos['nombre_metodo']}",
            f"Valor de la función: f = {_formatear_numero(datos['valor_funcion'])}",
            f"Error máximo de primer orden: {_formatear_numero(datos['error_maximo'])}",
            f"Incertidumbre estadística: {_formatear_numero(datos['incertidumbre_estadistica'])}",
            f"Resultado: f ≈ {_formatear_numero(datos['valor_funcion'])} ± {_formatear_numero(datos['incertidumbre_resultado'])}",
            f"Intervalo aproximado: [{_formatear_numero(inferior)}, {_formatear_numero(superior)}]",
            f"Error relativo porcentual del método seleccionado: {relativa}",
            "Conclusión: estimación lineal de primer orden; el intervalo no es un intervalo de confianza.",
            datos["interpretacion"],
        ))

    @staticmethod
    def _datos_propagacion_general(datos):
        lineas = [f"Función: f = {datos['expresion']}", f"Método: {datos['nombre_metodo']}"]
        lineas.extend(
            f"{nombre} = {_formatear_numero(datos['valores'][nombre])} ± "
            f"{_formatear_numero(datos['incertidumbres'][nombre])}"
            for nombre in datos["variables"]
        )
        return "\n".join(lineas)

    @staticmethod
    def _procedimiento_propagacion_general(datos):
        lineas = [
            "Fórmula de error máximo: Δf ≈ Σ |∂f/∂xᵢ| Δxᵢ",
            "Fórmula estadística (variables independientes): σf ≈ √Σ (∂f/∂xᵢ · σxᵢ)²",
            f"Función original: f = {datos['expresion']}",
        ]
        expresion_sustituida = datos["expresion"]
        for nombre in datos["variables"]:
            valor = datos["valores"][nombre]
            delta = datos["incertidumbres"][nombre]
            expresion_sustituida = re.sub(
                rf"\b{re.escape(nombre)}\b", f"({valor:.10g})", expresion_sustituida
            )
            lineas.append(f"{nombre} = {valor:.10g}; incertidumbre absoluta = {delta:.10g}")
        lineas.append(f"Sustitución en f: {expresion_sustituida} = {_formatear_numero(datos['valor_funcion'])}")
        for fila in datos["contribuciones"]:
            nombre = fila["variable"]
            lineas.extend((
                f"\n∂f/∂{nombre} = {fila['derivada']}",
                f"Evaluación en los datos = {fila['derivada_evaluada']:.10g}",
                f"Contribución máxima = |{fila['derivada_evaluada']:.10g}|·{fila['incertidumbre']:.10g} = {fila['contribucion_maxima']:.10g}",
                f"Contribución estadística = |{fila['derivada_evaluada']:.10g}|·{fila['incertidumbre']:.10g} = {fila['contribucion_estadistica']:.10g}",
            ))
        if datos["metodo"] == "maximo":
            suma = " + ".join(f"{fila['contribucion_maxima']:.10g}" for fila in datos["contribuciones"]) or "0"
            lineas.append(f"\nΔf ≈ Σ contribuciones = {suma} = {datos['error_maximo']:.10g}")
        else:
            suma = " + ".join(f"({fila['contribucion_estadistica']:.10g})²" for fila in datos["contribuciones"]) or "0"
            lineas.append(f"\nσf ≈ √({suma}) = {datos['incertidumbre_estadistica']:.10g}")
        lineas.append(
            f"Resultado: {_formatear_numero(datos['valor_funcion'])} ± "
            f"{_formatear_numero(datos['incertidumbre_resultado'])}"
        )
        lineas.append(datos["interpretacion"])
        return "\n".join(lineas)

    @staticmethod
    def _contribuciones_propagacion_general(datos):
        lineas = ["Variable | Valor | Incertidumbre | Derivada parcial | Evaluada | Error máx. | Estadística"]
        for fila in datos["contribuciones"]:
            lineas.extend((
                f"{fila['variable']} = {fila['valor']:.10g} ± {fila['incertidumbre']:.10g}",
                f"  ∂f/∂{fila['variable']} = {fila['derivada']}",
                f"  Evaluada = {fila['derivada_evaluada']:.10g}",
                f"  Contribución máx. = {fila['contribucion_maxima']:.10g}",
                f"  Contribución estadística = {fila['contribucion_estadistica']:.10g}",
                "",
            ))
        return "\n".join(lineas)

    @staticmethod
    def _procedimiento_error(parent, titulo, texto, fila, columnas):
        panel = Panel(parent, titulo=titulo, descripcion="Procedimiento y valores reportados por el cálculo.")
        panel.grid(row=fila, column=0, columnspan=columnas, sticky="ew", pady=(6, 2))
        panel.contenido.grid_columnconfigure(0, weight=1)
        caja = ctk.CTkTextbox(panel.contenido, height=120, wrap="word",
                              font=fuente_mono(12), fg_color=COLOR["suave"],
                              text_color=COLOR["texto"])
        caja.grid(row=0, column=0, sticky="ew")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    @staticmethod
    def _poner(caja, texto):
        reemplazar_texto(caja, texto)

    @staticmethod
    def _mostrar_error(error):
        from tkinter import messagebox
        messagebox.showerror("Revisa los datos", str(error))
