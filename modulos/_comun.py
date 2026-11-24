"""
Estilo visual, componentes compartidos y validaciones de la interfaz.

Proyecto integrador: estructura común de todas las pantallas.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import re
import sys
import weakref
from types import SimpleNamespace

import customtkinter as ctk
from tkinter import TclError, messagebox

from backend.matriz import _a_fraction, formatear_valor, subindice
from modulos.teoremas.resumen_teoremas import obtener_resumen


DIMENSION_MAXIMA = 12

# Tokens visuales compartidos. Las claves históricas se conservan porque las
# pantallas actuales las importan directamente desde este módulo.
COLOR = {
    "fondo": "#10151D",
    "fondo_secundario": "#151C26",
    "tarjeta": "#18212C",
    "suave": "#202B38",
    "interaccion": "#293449",
    "borde": "#293342",
    "borde_fuerte": "#354255",
    "texto": "#EDF3FA",
    "gris": "#A6B4C5",
    "deshabilitado": "#718096",
    "acento": "#43B3D5",
    "texto_acento": "#10202A",
    "hover": "#64C7E3",
    "hover_claro": "#293449",
    "marca": "#718096",
    "titulo_fondo": "#293449",
    "paso": "#9B8CF4",
    "ok": "#55C69A",
    "mal": "#E87983",
    "primario": "#43B3D5",
    "primario_hover": "#64C7E3",
    "primario_deshabilitado": "#354255",
    "violeta": "#9B8CF4",
    "verde": "#55C69A",
    "advertencia": "#F0B45E",
    "advertencia_hover": "#F5C77F",
    "error": "#E87983",
    "error_hover": "#EE929B",
    "informacion": "#43B3D5",
    "neutral": "#A6B4C5",
}

ESPACIADO = {"xxs": 4, "xs": 8, "sm": 12, "md": 16, "lg": 24, "xl": 32}
RADIO = {"sm": 8, "md": 10, "lg": 12, "xl": 16}
TAMANO_TEXTO = {"ayuda": 12, "cuerpo": 14, "subtitulo": 16, "titulo": 24}

# Marca discreta de cada módulo, en el orden de entrega de los programas del curso.
MARCAS = {
    "sistemas": "P1 · P2",
    "operaciones_vectores": "P3",
    "vectores": "P4",
    "matrices": "P3 · P5 · P6",
    "determinantes": "P5",
    "lu": "P6",
    "propiedades": "P3 · P5",
    "transformaciones": "P7",
    "metodos_numericos": "P7",
    "iterativos": "P8",
}

if sys.platform.startswith("win"):
    _FAMILIA_UI = "Segoe UI"
    _FAMILIA_MONO = "Consolas"
elif sys.platform == "darwin":
    _FAMILIA_UI = "Helvetica Neue"
    _FAMILIA_MONO = "Menlo"
else:
    _FAMILIA_UI = "DejaVu Sans"
    _FAMILIA_MONO = "DejaVu Sans Mono"


def fuente(tamano=13, negrita=False):
    """Fuente de interfaz con familia coherente y tamaño escalable por CTk."""
    return ctk.CTkFont(
        family=_FAMILIA_UI, size=tamano, weight="bold" if negrita else "normal"
    )


def fuente_mono(tamano=13, negrita=False):
    """Fuente monoespaciada para matrices, resultados y logotipos ASCII."""
    return ctk.CTkFont(
        family=_FAMILIA_MONO, size=tamano, weight="bold" if negrita else "normal"
    )


def leer_entero(entry, etiqueta, minimo=1, maximo=DIMENSION_MAXIMA):
    """Valida una dimensión entera, equivalente a fijar el orden del objeto."""
    texto = entry.get().strip()
    try:
        valor = int(texto)
    except ValueError as error:
        raise ValueError(f"{etiqueta} debe ser un número entero.") from error
    if valor < minimo or valor > maximo:
        raise ValueError(f"{etiqueta} debe estar entre {minimo} y {maximo}.")
    return valor


def leer_fraccion(entry, etiqueta):
    """Convierte un campo numérico a Fraction, equivalente a leer un escalar exacto."""
    texto = entry.get().strip()
    if not texto:
        # «Falta escribir …» sirve para «la entrada» y «el escalar» sin errores de género.
        raise ValueError(f"Falta escribir {etiqueta[:1].lower() + etiqueta[1:]}.")
    try:
        return _a_fraction(texto)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(
            f"{etiqueta} no es un número válido. Usa enteros, decimales o "
            "fracciones como 3, -2.5 o 1/3."
        ) from error


def formatear_vector(vector):
    """Presenta las componentes de un vector como una tupla ordenada."""
    return "(" + ", ".join(formatear_valor(valor) for valor in vector) + ")"


def formatear_matriz(matriz, separar=None, sangria=""):
    """Presenta una matriz alineada; `separar` dibuja │ antes de esa columna (para [A | I])."""
    if not matriz:
        return "[ ]"
    textos = [[formatear_valor(valor) for valor in fila] for fila in matriz]
    anchos = [
        max(len(fila[j]) for fila in textos)
        for j in range(len(textos[0]))
    ]

    def celda(fila, j):
        texto = fila[j].rjust(anchos[j])
        return ("│  " + texto) if j == separar else texto

    return "\n".join(
        sangria + "[ " + "  ".join(celda(fila, j) for j in range(len(fila))) + " ]"
        for fila in textos
    )


def formatear_paso_explicado(paso, incluir_estado=True):
    """Renderiza un paso pedagógico estructurado; reutilizable entre módulos."""
    lineas = [f"Objetivo: {paso['objetivo']}", f"Fundamento: {paso['fundamento']}",
              f"Procedimiento: {paso['procedimiento']}", f"Resultado: {paso['resultado']}"]
    if incluir_estado and paso.get("matriz") is not None:
        lineas.append(formatear_matriz(paso["matriz"]))
    return lineas


def matriz_a_texto_portapapeles(matriz):
    """Serializa una matriz en filas tabuladas, compatible con hojas de cálculo."""
    if not matriz or not matriz[0]:
        raise ValueError("No hay una matriz para copiar.")
    columnas = len(matriz[0])
    if any(len(fila) != columnas for fila in matriz):
        raise ValueError("La matriz no es rectangular y no se puede copiar.")
    return "\n".join(
        "\t".join(formatear_valor(_a_fraction(valor)) for valor in fila)
        for fila in matriz
    )


def parsear_matriz_portapapeles(texto):
    """Lee matrices tabuladas, separadas por espacios o en formato alineado."""
    if not texto or not texto.strip():
        raise ValueError("El portapapeles está vacío; copie una matriz primero.")
    filas_texto = []
    for linea in texto.strip().splitlines():
        linea = linea.strip()
        if not linea:
            continue
        # Admite la notación compacta [1 2 ; 3 4] que usa la interfaz.
        filas_texto.extend(parte.strip() for parte in linea.split(";") if parte.strip())
    matriz = []
    for numero_fila, fila_texto in enumerate(filas_texto, 1):
        fila_texto = re.sub(r"^\[\s*|\s*\]$", "", fila_texto).strip()
        if "\t" in fila_texto:
            valores = [valor.strip() for valor in fila_texto.split("\t")]
        elif "," in fila_texto:
            valores = [valor.strip() for valor in fila_texto.split(",")]
        else:
            valores = re.split(r"\s+", fila_texto)
        if not valores or any(not valor for valor in valores):
            raise ValueError(f"La fila {numero_fila} contiene una entrada vacía.")
        for columna, valor in enumerate(valores, 1):
            try:
                _a_fraction(valor)
            except (ValueError, ZeroDivisionError) as error:
                raise ValueError(
                    f"La entrada ({numero_fila},{columna}) no es un número válido: {valor!r}."
                ) from error
        matriz.append(valores)
    if not matriz:
        raise ValueError("No se encontró ninguna fila de matriz en el portapapeles.")
    ancho = len(matriz[0])
    if ancho == 0 or any(len(fila) != ancho for fila in matriz):
        raise ValueError("Las filas de la matriz deben tener la misma cantidad de columnas.")
    return matriz


def copiar_matriz_al_portapapeles(widget, matriz):
    """Copia una matriz numérica como texto TSV al portapapeles del sistema."""
    try:
        texto = matriz_a_texto_portapapeles(matriz)
        widget.clipboard_clear()
        widget.clipboard_append(texto)
    except (ValueError, TclError) as error:
        mensaje_error(error)
        return False
    return True


def copiar_entradas_al_portapapeles(widget, entradas):
    """Lee y copia una cuadrícula de campos numéricos."""
    try:
        matriz = [[_a_fraction(celda.get().strip()) for celda in fila] for fila in entradas]
        return copiar_matriz_al_portapapeles(widget, matriz)
    except (ValueError, ZeroDivisionError) as error:
        mensaje_error(error)
        return False


def pegar_matriz_en_entradas(widget, entradas):
    """Pega en una cuadrícula solo si el formato y sus dimensiones coinciden."""
    try:
        matriz = parsear_matriz_portapapeles(widget.clipboard_get())
        filas_esperadas = len(entradas)
        columnas_esperadas = len(entradas[0]) if entradas else 0
        if len(matriz) != filas_esperadas or any(
            len(fila) != columnas_esperadas for fila in matriz
        ):
            raise ValueError(
                f"La matriz copiada es de {len(matriz)}×{len(matriz[0])}; "
                f"el destino requiere {filas_esperadas}×{columnas_esperadas}. "
                "Ajuste el tamaño o copie una matriz compatible."
            )
    except TclError:
        mensaje_error(ValueError("No se pudo leer el portapapeles; copie una matriz primero."))
        return False
    except ValueError as error:
        mensaje_error(error)
        return False
    for i, fila in enumerate(entradas):
        for j, celda in enumerate(fila):
            celda.delete(0, "end")
            celda.insert(0, matriz[i][j])
    return True


def formatear_expresion(constante, terminos):
    """
    Escribe una solución con parámetros, por ejemplo  2 - t₃  o  -2*t₂ + 1/3*t₄.

    Equivale a expresar una variable básica en función de las variables
    libres: valor = constante + Σ coeficiente·tᵢ.

    Args:
        constante: parte fija (Fraction).
        terminos: dict {índice de la variable libre: coeficiente}.
    """
    partes = []
    for libre, coeficiente in sorted(terminos.items()):
        if coeficiente == 0:
            continue
        magnitud = abs(coeficiente)
        factor = "" if magnitud == 1 else formatear_valor(magnitud) + "*"
        partes.append(("-" if coeficiente < 0 else "+", f"{factor}t{subindice(libre + 1)}"))
    if constante != 0 or not partes:
        texto = formatear_valor(constante)
    else:
        # Sin parte fija: el primer término va sin «0 +» delante.
        signo, termino = partes.pop(0)
        texto = ("-" if signo == "-" else "") + termino
    for signo, termino in partes:
        texto += f" {signo} {termino}"
    return texto


def mensaje_error(error):
    """Muestra al usuario un error de validación de forma explícita."""
    messagebox.showerror("Revisa los datos", str(error))


def tarjeta(parent, **opciones):
    """Superficie compartida; mantiene la firma usada por las pantallas actuales."""
    opciones.setdefault("corner_radius", RADIO["lg"])
    opciones.setdefault("border_width", 1)
    opciones.setdefault("border_color", COLOR["borde"])
    opciones.setdefault("fg_color", COLOR["tarjeta"])
    return ctk.CTkFrame(
        parent,
        **opciones,
    )


_ESTADOS = {
    "success": ("✓", COLOR["ok"]),
    "converged": ("✓", COLOR["ok"]),
    "warning": ("!", COLOR["advertencia"]),
    "error": ("×", COLOR["error"]),
    "info": ("i", COLOR["informacion"]),
    "neutral": ("•", COLOR["neutral"]),
}


def _crear_boton(parent, texto, comando, variante, **opciones):
    """Fabrica botones con colores semanticos, geometria y estados coherentes."""
    estilos = {
        "primary": (COLOR["primario"], COLOR["primario_hover"], COLOR["texto_acento"],
                    0, COLOR["primario"], COLOR["primario_deshabilitado"]),
        "secondary": (COLOR["tarjeta"], COLOR["interaccion"], COLOR["texto"],
                      1, COLOR["borde_fuerte"], COLOR["deshabilitado"]),
        "neutral": (COLOR["interaccion"], COLOR["borde_fuerte"], COLOR["texto"],
                    0, COLOR["interaccion"], COLOR["deshabilitado"]),
        "warning": (COLOR["advertencia"], COLOR["advertencia_hover"], "#2A2114",
                    0, COLOR["advertencia"], "#58431E"),
        "danger": (COLOR["error"], COLOR["error_hover"], "#2B171B",
                   0, COLOR["error"], "#542A31"),
        "text": ("transparent", COLOR["interaccion"], COLOR["texto"],
                 0, COLOR["interaccion"], COLOR["deshabilitado"]),
    }
    fondo, hover, texto_color, borde, color_borde, texto_deshabilitado = estilos[variante]
    opciones.setdefault("height", 40 if variante == "primary" else 36)
    radio = opciones.pop("corner_radius", RADIO["sm"])
    return ctk.CTkButton(
        parent, text=texto, command=comando, corner_radius=radio,
        fg_color=fondo, hover_color=hover, text_color=texto_color,
        text_color_disabled=texto_deshabilitado, border_width=borde,
        border_color=color_borde, font=fuente(14 if variante == "primary" else 13,
                                               negrita=variante == "primary"),
        **opciones,
    )


def boton_primario(parent, texto, comando, **opciones):
    """Botón para la acción principal; conserva la API histórica."""
    return _crear_boton(parent, texto, comando, "primary", **opciones)


def boton_secundario(parent, texto, comando, **opciones):
    """Botón de acción secundaria con superficie y borde sutiles."""
    return _crear_boton(parent, texto, comando, "secondary", **opciones)


def boton_neutral(parent, texto, comando, **opciones):
    """Botón neutral para acciones auxiliares que necesitan más presencia que un enlace."""
    return _crear_boton(parent, texto, comando, "neutral", **opciones)


def boton_advertencia(parent, texto, comando, **opciones):
    """Botón para confirmar una acción que requiere atención."""
    return _crear_boton(parent, texto, comando, "warning", **opciones)


def boton_destructivo(parent, texto, comando, **opciones):
    """Botón para una acción destructiva; usar solo cuando exista tal acción."""
    return _crear_boton(parent, texto, comando, "danger", **opciones)


def boton_texto(parent, texto, comando, **opciones):
    """Botón discreto sin superficie para navegación y acciones de bajo énfasis."""
    opciones.setdefault("height", 32)
    return _crear_boton(parent, texto, comando, "text", **opciones)


def etiqueta_estado(parent, texto, estado="neutral", **opciones):
    """Etiqueta con símbolo y color semántico; el significado no depende del color."""
    simbolo, color = _ESTADOS.get(estado, _ESTADOS["neutral"])
    opciones.setdefault("anchor", "w")
    opciones.setdefault("justify", "left")
    return ctk.CTkLabel(parent, text=f"{simbolo} {texto}", font=fuente(13),
                        text_color=color, **opciones)


def entrada_texto(parent, ancho=180, placeholder=None, justify="left"):
    """Campo de texto de una línea con los mismos tokens que las entradas numéricas."""
    return ctk.CTkEntry(
        parent, width=ancho, height=38, placeholder_text=placeholder, justify=justify,
        corner_radius=RADIO["sm"], border_width=1,
        border_color=COLOR["borde_fuerte"], fg_color=COLOR["suave"],
        text_color=COLOR["texto"], placeholder_text_color=COLOR["deshabilitado"],
        font=fuente(TAMANO_TEXTO["cuerpo"]),
    )


class Panel(ctk.CTkFrame):
    """Panel reutilizable con encabezado opcional y un contenedor de contenido."""

    def __init__(self, parent, titulo=None, descripcion=None, accion=None, **opciones):
        opciones.setdefault("fg_color", COLOR["tarjeta"])
        opciones.setdefault("corner_radius", RADIO["lg"])
        opciones.setdefault("border_width", 1)
        opciones.setdefault("border_color", COLOR["borde"])
        super().__init__(parent, **opciones)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1 if titulo or descripcion or accion else 0, weight=1)

        fila = 0
        if titulo or descripcion or accion:
            self.encabezado = encabezado_seccion(
                self, titulo or "", descripcion=descripcion, accion=accion
            )
            self.encabezado.grid(row=0, column=0, sticky="ew",
                                 padx=ESPACIADO["md"], pady=(ESPACIADO["md"], 0))
            fila = 1
        self.contenido = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.contenido.grid(row=fila, column=0, sticky="nsew",
                            padx=ESPACIADO["md"], pady=ESPACIADO["md"])
        self.contenido.grid_columnconfigure(0, weight=1)


def encabezado_seccion(parent, titulo, descripcion=None, accion=None):
    """Crea un encabezado de sección; `accion` puede ser `(texto, callback)`."""
    marco = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
    marco.grid_columnconfigure(0, weight=1)
    etiqueta(marco, titulo, tamano=TAMANO_TEXTO["subtitulo"], color="texto",
             negrita=True).grid(row=0, column=0, sticky="w")
    if descripcion:
        etiqueta(marco, descripcion, tamano=TAMANO_TEXTO["ayuda"], color="gris",
                 justify="left", anchor="w", wraplength=560).grid(
                     row=1, column=0, sticky="w", pady=(ESPACIADO["xxs"], 0))
    if accion:
        texto, comando = accion
        boton_neutral(marco, texto, comando).grid(row=0, column=1, rowspan=2,
                                                  sticky="e", padx=(ESPACIADO["md"], 0))
    return marco


class TarjetaResultado(ctk.CTkFrame):
    """Tarjeta compacta para un resultado, métrica y estado destacados."""

    def __init__(self, parent, titulo, valor="—", detalle=None, estado=None, **opciones):
        opciones.setdefault("fg_color", COLOR["suave"])
        opciones.setdefault("corner_radius", RADIO["md"])
        opciones.setdefault("border_width", 1)
        opciones.setdefault("border_color", COLOR["borde"])
        super().__init__(parent, **opciones)
        self.grid_columnconfigure(0, weight=1)
        self.titulo = etiqueta(self, titulo, tamano=TAMANO_TEXTO["ayuda"], color="gris")
        self.titulo.grid(row=0, column=0, sticky="w", padx=ESPACIADO["md"],
                         pady=(ESPACIADO["sm"], 0))
        self.valor = ctk.CTkLabel(self, text=str(valor), font=fuente(22, negrita=True),
                                  text_color=COLOR["texto"], anchor="w", justify="left")
        self.valor.grid(row=1, column=0, sticky="ew", padx=ESPACIADO["md"],
                        pady=(ESPACIADO["xxs"], 0))
        self.detalle = etiqueta(self, detalle or "", tamano=TAMANO_TEXTO["ayuda"],
                                color="gris", justify="left", anchor="w", wraplength=440)
        self.detalle.grid(row=2, column=0, sticky="ew", padx=ESPACIADO["md"],
                          pady=(ESPACIADO["xxs"], ESPACIADO["sm"]))
        self.estado = etiqueta_estado(self, estado[0], estado[1]) if estado else None
        if self.estado:
            self.estado.grid(row=3, column=0, sticky="w", padx=ESPACIADO["md"],
                             pady=(0, ESPACIADO["sm"]))

    def actualizar(self, valor, detalle=None, estado=None):
        """Actualiza los datos visibles sin reconstruir la tarjeta."""
        self.valor.configure(text=str(valor))
        if detalle is not None:
            self.detalle.configure(text=detalle)
        if estado is not None:
            if self.estado is None:
                self.estado = etiqueta_estado(self, estado[0], estado[1])
                self.estado.grid(row=3, column=0, sticky="w", padx=ESPACIADO["md"],
                                 pady=(0, ESPACIADO["sm"]))
            else:
                texto, tipo = estado
                simbolo, color = _ESTADOS.get(tipo, _ESTADOS["neutral"])
                self.estado.configure(text=f"{simbolo} {texto}", text_color=color)


class Selector(ctk.CTkFrame):
    """Interruptor de opciones (por ejemplo Gauss / Gauss-Jordan) en blanco y negro."""

    def __init__(self, parent, valores, inicial=None):
        super().__init__(parent, fg_color=COLOR["hover_claro"], corner_radius=12)
        self._botones = {}
        for indice, valor in enumerate(valores):
            boton = ctk.CTkButton(
                self,
                text=valor,
                width=40,
                height=32,
                corner_radius=9,
                font=fuente(13),
                command=lambda v=valor: self.set(v),
            )
            boton.grid(row=0, column=indice, padx=3, pady=3)
            self._botones[valor] = boton
        self.set(inicial or valores[0])

    def set(self, valor):
        """Marca `valor` como la opción seleccionada."""
        self._valor = valor
        for nombre, boton in self._botones.items():
            activo = nombre == valor
            boton.configure(
                fg_color=COLOR["acento"] if activo else "transparent",
                hover_color=COLOR["hover"] if activo else COLOR["borde"],
                text_color=COLOR["texto_acento"] if activo else COLOR["texto"],
            )

    def get(self):
        """Devuelve la opción seleccionada."""
        return self._valor


class _GestorRueda:
    """Enruta la rueda al MarcoDesplazable que contiene el widget del evento."""

    _SECUENCIAS = (
        "<MouseWheel>",
        "<Shift-MouseWheel>",
        "<Button-4>",
        "<Button-5>",
    )

    def __init__(self, raiz):
        self._contenedores = weakref.WeakSet()
        for secuencia in self._SECUENCIAS:
            raiz.bind_all(
                secuencia,
                lambda evento, actual=secuencia: self._despachar(evento, actual),
                add="+",
            )

    def registrar(self, contenedor):
        self._contenedores.add(contenedor)

    def desregistrar(self, contenedor):
        self._contenedores.discard(contenedor)

    def _contenedor_del_evento(self, evento):
        widget = getattr(evento, "widget", None)
        while widget is not None:
            if widget in self._contenedores:
                try:
                    if widget.winfo_ismapped():
                        return widget
                except TclError:
                    self._contenedores.discard(widget)
                    return None
            widget = getattr(widget, "master", None)
        return None

    def _despachar(self, evento, secuencia):
        contenedor = self._contenedor_del_evento(evento)
        if contenedor is None:
            return None
        if secuencia == "<Shift-MouseWheel>":
            contenedor._rueda_horizontal(evento)
        elif secuencia == "<MouseWheel>":
            contenedor._rueda(evento)
        elif secuencia == "<Button-4>":
            contenedor._desplazar_v(-1)
        else:
            contenedor._desplazar_v(1)
        return "break"


def _gestor_rueda(parent):
    raiz = parent.winfo_toplevel()
    gestor = getattr(raiz, "_gestor_rueda_marco_desplazable", None)
    if gestor is None:
        gestor = _GestorRueda(raiz)
        raiz._gestor_rueda_marco_desplazable = gestor
    return gestor


class MarcoDesplazable(ctk.CTkFrame):
    """
    Área con desplazamiento vertical y horizontal para tablas grandes.

    Los widgets se colocan dentro de `self.interior`. Cada barra solo aparece
    cuando el contenido no cabe. Rueda del mouse: vertical; Shift + rueda:
    horizontal.
    """

    def __init__(self, parent, color=None):
        color = color or COLOR["tarjeta"]
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._lienzo = ctk.CTkCanvas(self, bg=color, highlightthickness=0, bd=0)
        self._lienzo.grid(row=0, column=0, sticky="nsew")
        self._barra_v = ctk.CTkScrollbar(self, orientation="vertical", command=self._lienzo.yview)
        self._barra_h = ctk.CTkScrollbar(self, orientation="horizontal", command=self._lienzo.xview)
        self._barra_v.grid(row=0, column=1, sticky="ns")
        self._barra_h.grid(row=1, column=0, sticky="ew")
        self._lienzo.configure(
            yscrollcommand=self._barra_v.set, xscrollcommand=self._barra_h.set
        )
        self.interior = ctk.CTkFrame(self._lienzo, fg_color=color, corner_radius=0)
        self._ventana = self._lienzo.create_window(0, 0, window=self.interior, anchor="nw")
        self.interior.bind(
            "<Configure>", lambda evento: self._diagnostico_configure(evento, "interior")
        )
        self._lienzo.bind(
            "<Configure>", lambda evento: self._diagnostico_configure(evento, "canvas")
        )
        self._gestor_rueda = _gestor_rueda(parent)
        self._gestor_rueda.registrar(self)
        from modulos._diagnostico_ui import ACTIVO, instrumentar_scroll
        self._diagnostico_medidor = instrumentar_scroll(self) if ACTIVO else None
        if self._diagnostico_medidor is not None:
            # CTkScrollbar dibuja el thumb en un Canvas interno: los eventos
            # llegan a ese Canvas, no al Frame contenedor.
            canvas_barra = getattr(self._barra_v, "_canvas", self._barra_v)
            canvas_barra.bind("<ButtonPress-1>", self._diagnostico_arrastre_inicio, add="+")
            canvas_barra.bind("<B1-Motion>", self._diagnostico_arrastre_movimiento, add="+")
            canvas_barra.bind("<ButtonRelease-1>", self._diagnostico_arrastre_fin, add="+")

    def _diagnostico_configure(self, evento, origen):
        """Registra Configure si está activado; conserva el ajuste habitual."""
        from modulos._diagnostico_ui import registrar_configure
        registrar_configure(self, origen)

    def _diagnostico_arrastre_inicio(self, evento):
        """Registra todo press y clasifica el elemento Canvas bajo el cursor."""
        lienzo = getattr(self._barra_v, "_canvas", None)
        if lienzo is None or self._diagnostico_medidor is None:
            return
        try:
            elementos = lienzo.find_withtag("current")
            elemento = elementos[-1] if elementos else None
            tags = lienzo.gettags(elemento) if elemento is not None else ()
            error_identificacion = None
        except Exception as error:
            elemento, tags = None, ()
            error_identificacion = f"error_identificando_elemento:{error}"
        reconocido = "scrollbar_parts" in tags
        motivo = None if reconocido else error_identificacion or (
            "sin_elemento_current" if elemento is None else "elemento_actual_sin_tag_scrollbar_parts"
        )
        info = self._diagnostico_medidor.registrar_press(
            evento, elemento, tags, reconocido, motivo
        )
        self._diagnostico_arrastre_activo = True
        self._diagnostico_medidor.iniciar_arrastre(info)

    def _diagnostico_arrastre_movimiento(self, evento):
        if getattr(self, "_diagnostico_arrastre_activo", False):
            self._diagnostico_medidor.mover_arrastre(evento)

    def _diagnostico_arrastre_fin(self, evento):
        if getattr(self, "_diagnostico_arrastre_activo", False):
            self._diagnostico_medidor.terminar_arrastre(
                release_info=self._diagnostico_medidor.info_release(evento)
            )
        elif self._diagnostico_medidor is not None:
            self._diagnostico_medidor.registrar_release_sin_sesion(evento)
        self._diagnostico_arrastre_activo = False

    def _actualizar(self):
        """Ajusta la región desplazable y muestra solo las barras necesarias."""
        self._lienzo.configure(scrollregion=self._lienzo.bbox("all"))
        ancho_contenido = self.interior.winfo_reqwidth()
        alto_contenido = self.interior.winfo_reqheight()
        ancho_visible = self._lienzo.winfo_width()
        alto_visible = self._lienzo.winfo_height()
        # El interior ocupa al menos todo el ancho visible (fondo uniforme).
        self._lienzo.itemconfigure(self._ventana, width=max(ancho_contenido, ancho_visible))
        for barra, sobra, vista in (
            (self._barra_h, ancho_contenido > ancho_visible, self._lienzo.xview_moveto),
            (self._barra_v, alto_contenido > alto_visible, self._lienzo.yview_moveto),
        ):
            if sobra:
                barra.grid()
            else:
                barra.grid_remove()
                vista(0)

    def destroy(self):
        if (self._diagnostico_medidor is not None
                and self._diagnostico_medidor.arrastrando):
            self._diagnostico_medidor.terminar_arrastre("contenedor_destruido")
        self._gestor_rueda.desregistrar(self)
        super().destroy()

    def _pasos_rueda(self, evento):
        # Windows entrega múltiplos de 120; macOS, valores pequeños.
        if abs(evento.delta) >= 120:
            return int(-evento.delta / 120)
        return -1 if evento.delta > 0 else 1

    def _desplazar_v(self, pasos):
        if self._diagnostico_medidor is not None:
            self._diagnostico_medidor.interaccion("rueda_o_boton_vertical")
        if self._barra_v.winfo_ismapped():
            self._lienzo.yview_scroll(pasos, "units")

    def _rueda(self, evento):
        if self._diagnostico_medidor is not None:
            self._diagnostico_medidor.interaccion("rueda_vertical")
        self._desplazar_v(self._pasos_rueda(evento))

    def _rueda_horizontal(self, evento):
        if self._diagnostico_medidor is not None:
            self._diagnostico_medidor.interaccion("rueda_horizontal")
        if self._barra_h.winfo_ismapped():
            self._lienzo.xview_scroll(self._pasos_rueda(evento), "units")


def entrada_numero(parent, ancho=62):
    """Celda numerica centrada que selecciona su contenido al recibir el foco."""
    entry = ctk.CTkEntry(
        parent,
        width=ancho,
        height=38,
        justify="center",
        corner_radius=RADIO["sm"],
        border_width=1,
        border_color=COLOR["borde_fuerte"],
        fg_color=COLOR["suave"],
        text_color=COLOR["texto"],
        font=fuente(TAMANO_TEXTO["cuerpo"]),
    )
    entry.insert(0, "0")
    entry.bind("<FocusIn>", lambda evento, celda=entry: celda.select_range(0, "end"))
    return entry

def etiqueta(parent, texto, tamano=12, color="gris", negrita=False, **opciones):
    """Texto pequeño (en gris por defecto) para encabezados de tablas y ayudas."""
    return ctk.CTkLabel(
        parent,
        text=texto,
        font=fuente(tamano, negrita),
        text_color=COLOR[color],
        **opciones,
    )


def subtitulo(parent, texto):
    """Titulo de una seccion dentro de un panel."""
    return ctk.CTkLabel(
        parent, text=texto,
        font=fuente(TAMANO_TEXTO["subtitulo"], negrita=True),
        text_color=COLOR["texto"],
    )


def campo(parent, texto, valor, ancho=70, al_enter=None, ayuda=None):
    """Crea un campo rotulado; devuelve (marco, entry) como antes."""
    marco = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
    etiqueta(marco, texto, tamano=TAMANO_TEXTO["ayuda"], color="gris").pack(
        anchor="w", pady=(0, ESPACIADO["xxs"])
    )
    entry = entrada_texto(marco, ancho=ancho, justify="center")
    entry.insert(0, valor)
    entry.pack(anchor="w")
    if ayuda:
        etiqueta(marco, ayuda, tamano=TAMANO_TEXTO["ayuda"], color="gris",
                 justify="left", anchor="w", wraplength=max(ancho * 3, 180)).pack(
                     anchor="w", pady=(ESPACIADO["xxs"], 0)
                 )
    if al_enter is not None:
        entry.bind("<Return>", lambda evento: al_enter())
    return marco, entry

def crear_controles(parent, especificacion, al_aplicar, texto_boton="Crear tabla"):
    """
    Fila de campos de tamaño con un botón que (re)construye la tabla.

    Args:
        especificacion: lista de (clave, etiqueta, valor_inicial, ancho) o
            (clave, etiqueta, valor_inicial, ancho, False). El False indica que
            el campo no es un tamaño (por ejemplo un escalar) y Enter no debe
            reconstruir la tabla, para no borrar los datos escritos.
        al_aplicar: función que se ejecuta con el botón o con Enter.

    Returns:
        (marco, dict {clave: entry})
    """
    marco = ctk.CTkFrame(parent, fg_color="transparent")
    entradas = {}
    for clave, texto, valor, ancho, *resto in especificacion:
        es_tamano = resto[0] if resto else True
        caja, entry = campo(
            marco, texto, valor, ancho=ancho, al_enter=al_aplicar if es_tamano else None
        )
        caja.pack(side="left", padx=(0, ESPACIADO["sm"]), anchor="s")
        entradas[clave] = entry
    if texto_boton:
        boton_secundario(marco, texto_boton, al_aplicar, width=110).pack(
            side="left", anchor="s"
        )
    return marco, entradas


def llenar(celdas, valores):
    """Escribe cada valor en su celda (se usa para cargar los ejemplos)."""
    for celda, valor in zip(celdas, valores):
        celda.delete(0, "end")
        celda.insert(0, str(valor))


def reiniciar_celdas(*grupos):
    """Pone en 0 cada celda de las listas (o listas de listas) recibidas."""
    for grupo in grupos:
        for elemento in grupo:
            celdas = elemento if isinstance(elemento, list) else [elemento]
            for celda in celdas:
                celda.delete(0, "end")
                celda.insert(0, "0")


_NOTA = re.compile(r"^\s*(Por qué|Qué se hace|Condición|Idea clave|Significa)\b")


def _estilo_linea(linea):
    """Decide el estilo de una línea del resultado (o None si va normal)."""
    if re.match(r"^Paso \d+", linea):
        return "paso"
    letras = re.findall(r"[^\W\d_]", linea)
    if len(letras) >= 5 and not any(c.islower() for c in letras) or re.match(r"^\d+\) [A-ZÁÉÍÓÚÑ¿]", linea):
        return "titulo"
    if _NOTA.match(linea):
        return "nota"
    if "✗" in linea or re.search(r"NO se cumple|No se cumple|NO coinciden", linea):
        return "mal"
    if "✓" in linea or re.search(r"Se cumple|se cumple|coinciden", linea):
        return "ok"
    return None


def _es_fila_de_matriz(linea):
    """Las filas de una matriz empiezan con «[» (con o sin sangría)."""
    return linea.lstrip().startswith("[")


def _dar_formato(caja, texto):
    """Resalta títulos, pasos, notas y comprobaciones y deja aire entre las partes."""
    # Aire general: cada línea separada y el texto despegado de los bordes.
    caja.configure(spacing1=3, spacing2=4, spacing3=3, padx=10, pady=8)
    # El espacio de arriba del título se pone en la línea anterior: si fuera parte
    # del título, la barra gris se estiraría hacia arriba.
    caja.tag_config("titulo", background=COLOR["titulo_fondo"], foreground=COLOR["texto_acento"],
                    spacing1=8, spacing3=8, lmargin1=6)
    caja.tag_config("antes_de_titulo", spacing3=22)
    caja.tag_config("paso", foreground=COLOR["paso"], spacing1=24, spacing3=4)
    caja.tag_config("nota", foreground=COLOR["gris"], lmargin2=28)
    caja.tag_config("ok", foreground=COLOR["ok"])
    caja.tag_config("mal", foreground=COLOR["mal"])
    # Las filas de una matriz van juntas (para que se vea como matriz) y el bloque
    # completo queda separado del texto de arriba y de abajo.
    caja.tag_config("matriz", spacing1=0, spacing3=0)
    caja.tag_config("matriz_inicio", spacing1=10)
    caja.tag_config("matriz_fin", spacing3=12)
    lineas = texto.split("\n")
    for numero, linea in enumerate(lineas, 1):
        rango = (f"{numero}.0", f"{numero}.0 lineend +1c")
        estilo = _estilo_linea(linea)
        if estilo:
            caja.tag_add(estilo, *rango)
        if estilo == "titulo" and numero > 1:
            caja.tag_add("antes_de_titulo", f"{numero - 1}.0", f"{numero - 1}.0 lineend +1c")
        if _es_fila_de_matriz(linea):
            caja.tag_add("matriz", *rango)
            if numero == 1 or not _es_fila_de_matriz(lineas[numero - 2]):
                caja.tag_add("matriz_inicio", *rango)
            if numero == len(lineas) or not _es_fila_de_matriz(lineas[numero]):
                caja.tag_add("matriz_fin", *rango)


def reemplazar_texto(caja, texto, resumen=None):
    """
    Sustituye todo el texto visible sin acumular resultados anteriores.

    Si se da `resumen`, se muestra arriba en un recuadro negro: es la
    respuesta final en una línea. Si el texto está vacío, en el lugar del
    resultado se muestra la guía "Cómo usar" del módulo.
    """
    caja.configure(state="normal")
    caja.delete("1.0", "end")
    caja.insert("1.0", texto)
    _dar_formato(caja, texto)
    caja.see("1.0")
    # Solo lectura: se puede seleccionar y copiar, pero no editar el resultado.
    caja.configure(state="disabled")
    respuesta = getattr(caja, "respuesta", None)
    if respuesta is not None:
        if resumen and texto.strip():
            respuesta.configure(text=resumen)
            respuesta.grid()
        else:
            respuesta.grid_remove()
    guia = getattr(caja, "guia", None)
    if guia is None:
        return
    if texto.strip():
        guia.grid_remove()
        caja.grid()
    else:
        caja.grid_remove()
        guia.grid()


def _proteger_callbacks_scroll_textbox(caja):
    """Evita que el dibujo de CTkScrollbar reingrese en su callback de scroll."""
    def crear_callback(barra):
        actualizando = False

        def actualizar(inicio, fin):
            nonlocal actualizando
            if actualizando:
                return
            actualizando = True
            try:
                barra.set(inicio, fin)
            finally:
                actualizando = False

        return actualizar

    caja._textbox.configure(
        yscrollcommand=crear_callback(caja._y_scrollbar),
        xscrollcommand=crear_callback(caja._x_scrollbar),
    )


def matriz_en_linea(matriz):
    """Escribe una matriz pequeña en una línea: [1  2 ; 3  4]."""
    return "[" + " ; ".join(
        "  ".join(formatear_valor(valor) for valor in fila) for fila in matriz
    ) + "]"


def _crear_guia(parent, pasos, nota, indicacion):
    """Guía 'Cómo usar': pasos numerados, una nota y qué mostrará el resultado."""
    guia = ctk.CTkFrame(parent, fg_color=COLOR["suave"], corner_radius=12)
    guia.grid_columnconfigure(1, weight=1)
    etiqueta(guia, "CÓMO USAR", tamano=11, negrita=True).grid(
        row=0, column=0, columnspan=2, sticky="w", padx=22, pady=(22, 10)
    )
    textos_pasos = []
    textos_anchos = []
    fila = 1
    for indice, paso in enumerate(pasos, 1):
        ctk.CTkLabel(
            guia,
            text=str(indice),
            width=26,
            height=26,
            corner_radius=13,
            fg_color=COLOR["acento"],
            text_color=COLOR["texto_acento"],
            font=fuente(12, negrita=True),
        ).grid(row=fila, column=0, sticky="nw", padx=(22, 12), pady=7)
        texto = ctk.CTkLabel(
            guia,
            text=paso,
            justify="left",
            anchor="w",
            font=fuente(14),
            text_color=COLOR["texto"],
            wraplength=320,
        )
        texto.grid(row=fila, column=1, sticky="w", padx=(0, 22), pady=7)
        textos_pasos.append(texto)
        fila += 1
    if nota:
        texto = etiqueta(guia, nota, tamano=13, justify="left", anchor="w", wraplength=360)
        texto.grid(row=fila, column=0, columnspan=2, sticky="w", padx=22, pady=(12, 0))
        textos_anchos.append(texto)
        fila += 1
    ctk.CTkFrame(guia, height=1, fg_color=COLOR["borde_fuerte"]).grid(
        row=fila, column=0, columnspan=2, sticky="ew", padx=22, pady=(20, 16)
    )
    fila += 1
    etiqueta(guia, "AL CALCULAR", tamano=11, negrita=True).grid(
        row=fila, column=0, columnspan=2, sticky="w", padx=22
    )
    fila += 1
    texto = etiqueta(guia, indicacion, tamano=13, justify="left", anchor="w", wraplength=360)
    texto.grid(row=fila, column=0, columnspan=2, sticky="w", padx=22, pady=(4, 22))
    textos_anchos.append(texto)

    def ajustar(evento):
        """Reacomoda el texto de la guía al ancho disponible."""
        # evento.width viene en píxeles reales; wraplength se da en unidades de
        # CustomTkinter, que después aplica la escala de la pantalla.
        ancho = evento.width / ctk.ScalingTracker.get_widget_scaling(guia)
        for texto in textos_pasos:
            texto.configure(wraplength=max(ancho - 90, 180))
        for texto in textos_anchos:
            texto.configure(wraplength=max(ancho - 50, 180))

    guia.bind("<Configure>", ajustar)
    return guia


def crear_estructura(
    panel,
    on_back,
    numero,
    titulo,
    descripcion,
    logo,
    pasos,
    clave_teoremas,
    indicacion,
    nota="Puedes escribir enteros, decimales o fracciones: 3, -2.5, 1/3.",
    ejemplo=None,
):
    """
    Arma la pantalla estándar de un módulo y devuelve sus zonas.

    Distribución:
        barra superior  -> volver al menú, "Cómo usar" y
                           "0. Ver Teoremas Clave del Módulo"
        encabezado      -> número, título, descripción y logotipo ASCII
        tarjeta izq.    -> datos de entrada y botones
        tarjeta der.    -> guía "Cómo usar" mientras no hay resultado;
                           después, el resultado paso a paso

    Returns:
        SimpleNamespace con `contenido` (donde van los datos), `acciones`
        (fila de botones) y `resultado` (caja de texto).
    """
    panel.configure(fg_color=COLOR["fondo"], corner_radius=0)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_rowconfigure(2, weight=1)

    barra = ctk.CTkFrame(panel, fg_color="transparent")
    barra.grid(row=0, column=0, sticky="ew", padx=28, pady=(14, 0))
    boton_texto(barra, "←  Menú principal", on_back, width=150).pack(side="left")
    boton_secundario(
        barra,
        "0. Ver Teoremas Clave del Módulo",
        lambda: mostrar_teoremas(panel, clave_teoremas, titulo),
    ).pack(side="right")

    encabezado = ctk.CTkFrame(panel, fg_color="transparent")
    encabezado.grid(row=1, column=0, sticky="ew", padx=34, pady=(0, 16))
    encabezado.grid_columnconfigure(0, weight=1)
    linea_modulo = ctk.CTkFrame(encabezado, fg_color="transparent")
    linea_modulo.grid(row=0, column=0, sticky="w")
    etiqueta(linea_modulo, f"MÓDULO {numero}", tamano=11, negrita=True).pack(side="left")
    if clave_teoremas in MARCAS:
        etiqueta(linea_modulo, MARCAS[clave_teoremas], tamano=10, color="marca").pack(
            side="left", padx=(10, 0)
        )
    ctk.CTkLabel(
        encabezado, text=titulo, font=fuente(28, negrita=True), text_color=COLOR["texto"]
    ).grid(row=1, column=0, sticky="w")
    etiqueta(encabezado, descripcion, tamano=14).grid(row=2, column=0, sticky="w")
    ctk.CTkLabel(
        encabezado,
        text=logo,
        font=fuente_mono(11),
        text_color=COLOR["gris"],
        justify="left",
        fg_color=COLOR["tarjeta"],
        corner_radius=12,
    ).grid(row=0, column=1, rowspan=3, sticky="e", ipadx=14, ipady=8)

    cuerpo = ctk.CTkFrame(panel, fg_color="transparent")
    cuerpo.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 22))
    cuerpo.grid_columnconfigure((0, 1), weight=1, uniform="columnas")
    cuerpo.grid_rowconfigure(0, weight=1)

    izquierda = tarjeta(cuerpo)
    izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    izquierda.grid_columnconfigure(0, weight=1)
    izquierda.grid_rowconfigure(1, weight=1)
    subtitulo(izquierda, "Datos").grid(row=0, column=0, sticky="w", padx=22, pady=(18, 0))
    desplazable = MarcoDesplazable(izquierda)
    desplazable.grid(row=1, column=0, sticky="nsew", padx=(8, 6), pady=0)
    contenido = desplazable.interior
    acciones = ctk.CTkFrame(izquierda, fg_color="transparent")
    acciones.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 18))

    derecha = tarjeta(cuerpo)
    derecha.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    derecha.grid_columnconfigure(0, weight=1)
    derecha.grid_rowconfigure(2, weight=1)
    subtitulo(derecha, "Resultado").grid(row=0, column=0, sticky="w", padx=22, pady=(18, 10))
    respuesta = ctk.CTkLabel(
        derecha,
        text="",
        fg_color=COLOR["acento"],
        text_color=COLOR["texto_acento"],
        corner_radius=12,
        font=fuente(15, negrita=True),
        anchor="w",
        justify="left",
        height=48,
        wraplength=400,
    )
    respuesta.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12), ipadx=14)
    corte = {"actual": 400}

    def ajustar_respuesta(evento):
        """Corta el texto de la respuesta según el ancho de la tarjeta."""
        # Se mide la tarjeta y no la etiqueta: si la etiqueta se midiera a sí misma,
        # un texto largo la agranda, cambia el corte y se repite sin fin (la app se congela).
        ancho = max(int(evento.width / ctk.ScalingTracker.get_widget_scaling(derecha)) - 110, 200)
        if abs(ancho - corte["actual"]) > 4:
            corte["actual"] = ancho
            respuesta.configure(wraplength=ancho)

    derecha.bind("<Configure>", ajustar_respuesta, add="+")
    resultado = ctk.CTkTextbox(
        derecha,
        font=fuente_mono(13),
        wrap="word",
        corner_radius=12,
        fg_color=COLOR["suave"],
        text_color=COLOR["texto"],
    )
    _proteger_callbacks_scroll_textbox(resultado)
    resultado.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
    guia = _crear_guia(derecha, pasos, nota, indicacion)
    guia.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
    resultado.guia = guia
    resultado.respuesta = respuesta
    reemplazar_texto(resultado, "")

    # Vuelve a mostrar la guía en cualquier momento.
    boton_texto(
        barra, "?  Cómo usar", lambda: reemplazar_texto(resultado, ""), width=110
    ).pack(side="right", padx=(0, 8))
    if ejemplo is not None:
        boton_secundario(barra, "Probar con un ejemplo", ejemplo, width=170).pack(
            side="right", padx=(0, 8)
        )

    return SimpleNamespace(contenido=contenido, acciones=acciones, resultado=resultado)


def mostrar_teoremas(parent, modulo, titulo):
    """Abre una ventana independiente con los teoremas del módulo."""
    contenedor = parent.winfo_toplevel()
    ventana = ctk.CTkToplevel(contenedor)
    ventana.title("Teoremas clave - " + titulo)
    ventana.geometry("720x540")
    ventana.minsize(520, 380)
    ventana.configure(fg_color=COLOR["fondo"])
    etiqueta(ventana, "TEOREMAS CLAVE", tamano=11, negrita=True).pack(
        padx=28, pady=(24, 0), anchor="w"
    )
    ctk.CTkLabel(
        ventana, text=titulo, font=fuente(24, negrita=True), text_color=COLOR["texto"]
    ).pack(padx=28, anchor="w")
    caja = tarjeta(ventana)
    caja.pack(fill="both", expand=True, padx=24, pady=16)
    texto = ctk.CTkTextbox(
        caja,
        font=fuente(14),
        wrap="word",
        fg_color=COLOR["tarjeta"],
        text_color=COLOR["texto"],
    )
    texto.pack(fill="both", expand=True, padx=14, pady=14)
    texto.insert("1.0", obtener_resumen(modulo))
    texto.configure(state="disabled")
    boton_primario(ventana, "Cerrar", ventana.destroy, width=120).pack(
        padx=24, pady=(0, 20), anchor="e"
    )
    ventana.transient(contenedor)
    ventana.after(100, ventana.focus)
    return ventana
