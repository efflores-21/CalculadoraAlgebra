"""Estilo visual, componentes y validaciones comunes para todos los módulos."""

import sys
from types import SimpleNamespace

import customtkinter as ctk
from tkinter import messagebox

from backend.matriz import _a_fraction, formatear_valor, subindice
from modulos.teoremas.resumen_teoremas import obtener_resumen


DIMENSION_MAXIMA = 12

# Paleta en blanco y negro: fondo gris muy claro, tarjetas blancas y acentos negros.
COLOR = {
    "fondo": "#F4F4F4",
    "tarjeta": "#FFFFFF",
    "suave": "#F7F7F7",
    "borde": "#E4E4E4",
    "borde_fuerte": "#D4D4D4",
    "texto": "#111111",
    "gris": "#737373",
    "negro": "#111111",
    "hover": "#2E2E2E",
    "hover_claro": "#EFEFEF",
}

if sys.platform.startswith("win"):
    _FAMILIA_MONO = "Consolas"
elif sys.platform == "darwin":
    _FAMILIA_MONO = "Menlo"
else:
    _FAMILIA_MONO = "DejaVu Sans Mono"


def fuente(tamano=13, negrita=False):
    """Fuente principal de la interfaz (la familia la define el tema)."""
    return ctk.CTkFont(size=tamano, weight="bold" if negrita else "normal")


def fuente_mono(tamano=13, negrita=False):
    """Fuente monoespaciada para matrices, resultados y logotipos ASCII."""
    return ctk.CTkFont(
        family=_FAMILIA_MONO, size=tamano, weight="bold" if negrita else "normal"
    )


# ----------------------------------------------------------------------------
# Validaciones y formato
# ----------------------------------------------------------------------------

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
        raise ValueError(f"{etiqueta} no puede quedar vacío.")
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


def formatear_matriz(matriz):
    """Presenta una matriz alineada, equivalente a mostrar sus filas y columnas."""
    if not matriz:
        return "[ ]"
    textos = [[formatear_valor(valor) for valor in fila] for fila in matriz]
    anchos = [
        max(len(fila[j]) for fila in textos)
        for j in range(len(textos[0]))
    ]
    return "\n".join(
        "[ " + "  ".join(
            fila[j].rjust(anchos[j]) for j in range(len(fila))
        ) + " ]"
        for fila in textos
    )


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


# ----------------------------------------------------------------------------
# Componentes básicos
# ----------------------------------------------------------------------------

def tarjeta(parent, **opciones):
    """Superficie blanca con esquinas redondeadas y borde fino."""
    return ctk.CTkFrame(
        parent,
        fg_color=COLOR["tarjeta"],
        corner_radius=18,
        border_width=1,
        border_color=COLOR["borde"],
        **opciones,
    )


def boton_primario(parent, texto, comando, **opciones):
    """Botón negro para la acción principal."""
    opciones.setdefault("height", 40)
    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        corner_radius=10,
        fg_color=COLOR["negro"],
        hover_color=COLOR["hover"],
        text_color="#FFFFFF",
        font=fuente(14, negrita=True),
        **opciones,
    )


def boton_secundario(parent, texto, comando, **opciones):
    """Botón blanco con borde, para acciones de apoyo."""
    opciones.setdefault("height", 36)
    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        corner_radius=10,
        fg_color=COLOR["tarjeta"],
        hover_color=COLOR["hover_claro"],
        border_width=1,
        border_color=COLOR["borde_fuerte"],
        text_color=COLOR["texto"],
        font=fuente(13),
        **opciones,
    )


def boton_texto(parent, texto, comando, **opciones):
    """Botón sin fondo, como un enlace discreto."""
    opciones.setdefault("height", 32)
    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        corner_radius=10,
        fg_color="transparent",
        hover_color=COLOR["borde"],
        text_color=COLOR["texto"],
        font=fuente(13),
        **opciones,
    )


class Selector(ctk.CTkFrame):
    """Interruptor de opciones (por ejemplo Gauss / Gauss-Jordan) en blanco y negro."""

    def __init__(self, parent, valores, inicial=None):
        super().__init__(parent, fg_color=COLOR["hover_claro"], corner_radius=12)
        self._botones = {}
        for indice, valor in enumerate(valores):
            boton = ctk.CTkButton(
                self,
                text=valor,
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
                fg_color=COLOR["negro"] if activo else "transparent",
                hover_color=COLOR["hover"] if activo else COLOR["borde"],
                text_color="#FFFFFF" if activo else COLOR["texto"],
            )

    def get(self):
        """Devuelve la opción seleccionada."""
        return self._valor


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
        self.interior.bind("<Configure>", lambda evento: self._actualizar())
        self._lienzo.bind("<Configure>", lambda evento: self._actualizar())
        self.bind("<Enter>", lambda evento: self._activar_rueda(True))
        self.bind("<Leave>", self._al_salir)

    def _al_salir(self, evento):
        """Desactiva la rueda solo si el puntero salió de verdad (no si entró a una celda)."""
        x, y = self.winfo_pointerxy()
        debajo = self.winfo_containing(x, y)
        if debajo is not None and str(debajo).startswith(str(self)):
            return
        self._activar_rueda(False)

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

    def _activar_rueda(self, activa):
        """La rueda del mouse solo mueve esta área mientras el puntero está encima."""
        if activa:
            self.bind_all("<MouseWheel>", self._rueda)
            self.bind_all("<Shift-MouseWheel>", self._rueda_horizontal)
            # Linux entrega la rueda como botones 4 (arriba) y 5 (abajo).
            self.bind_all("<Button-4>", lambda evento: self._desplazar_v(-1))
            self.bind_all("<Button-5>", lambda evento: self._desplazar_v(1))
        else:
            for secuencia in ("<MouseWheel>", "<Shift-MouseWheel>", "<Button-4>", "<Button-5>"):
                self.unbind_all(secuencia)

    def _pasos_rueda(self, evento):
        # Windows entrega múltiplos de 120; macOS, valores pequeños.
        if abs(evento.delta) >= 120:
            return int(-evento.delta / 120)
        return -1 if evento.delta > 0 else 1

    def _desplazar_v(self, pasos):
        if self._barra_v.winfo_ismapped():
            self._lienzo.yview_scroll(pasos, "units")

    def _rueda(self, evento):
        self._desplazar_v(self._pasos_rueda(evento))

    def _rueda_horizontal(self, evento):
        if self._barra_h.winfo_ismapped():
            self._lienzo.xview_scroll(self._pasos_rueda(evento), "units")


def entrada_numero(parent, ancho=62):
    """Celda numérica centrada que selecciona su contenido al recibir el foco."""
    entry = ctk.CTkEntry(
        parent,
        width=ancho,
        height=36,
        justify="center",
        corner_radius=8,
        border_width=1,
        border_color=COLOR["borde_fuerte"],
        fg_color=COLOR["tarjeta"],
        font=fuente(14),
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
    """Título de una sección dentro de una tarjeta."""
    return ctk.CTkLabel(
        parent, text=texto, font=fuente(15, negrita=True), text_color=COLOR["texto"]
    )


def campo(parent, texto, valor, ancho=70, al_enter=None):
    """
    Crea un campo con su etiqueta encima y lo devuelve.

    Devuelve (marco, entry): el marco se coloca con pack/grid y el entry se
    usa para leer el valor. Si se da `al_enter`, pulsar Enter lo ejecuta.
    """
    marco = ctk.CTkFrame(parent, fg_color="transparent")
    etiqueta(marco, texto).pack(anchor="w", pady=(0, 2))
    entry = ctk.CTkEntry(
        marco,
        width=ancho,
        height=36,
        justify="center",
        corner_radius=8,
        border_width=1,
        border_color=COLOR["borde_fuerte"],
        font=fuente(14),
    )
    entry.insert(0, valor)
    entry.pack(anchor="w")
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
        caja.pack(side="left", padx=(0, 12), anchor="s")
        entradas[clave] = entry
    if texto_boton:
        boton_secundario(marco, texto_boton, al_aplicar, width=110).pack(
            side="left", anchor="s"
        )
    return marco, entradas


def reiniciar_celdas(*grupos):
    """Pone en 0 cada celda de las listas (o listas de listas) recibidas."""
    for grupo in grupos:
        for elemento in grupo:
            celdas = elemento if isinstance(elemento, list) else [elemento]
            for celda in celdas:
                celda.delete(0, "end")
                celda.insert(0, "0")


# ----------------------------------------------------------------------------
# Área de resultados
# ----------------------------------------------------------------------------

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


def matriz_en_linea(matriz):
    """Escribe una matriz pequeña en una línea: [1  2 ; 3  4]."""
    return "[" + " ; ".join(
        "  ".join(formatear_valor(valor) for valor in fila) for fila in matriz
    ) + "]"


# ----------------------------------------------------------------------------
# Estructura de cada módulo
# ----------------------------------------------------------------------------

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
            fg_color=COLOR["negro"],
            text_color="#FFFFFF",
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
    etiqueta(encabezado, f"MÓDULO {numero}", tamano=11, negrita=True).grid(
        row=0, column=0, sticky="w"
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
        fg_color=COLOR["negro"],
        text_color="#FFFFFF",
        corner_radius=12,
        font=fuente(15, negrita=True),
        anchor="w",
        justify="left",
        height=48,
    )
    respuesta.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12), ipadx=14)
    respuesta.bind(
        "<Configure>",
        lambda evento: respuesta.configure(
            wraplength=evento.width / ctk.ScalingTracker.get_widget_scaling(respuesta) - 40
        ),
    )
    resultado = ctk.CTkTextbox(
        derecha,
        font=fuente_mono(13),
        wrap="none",
        corner_radius=12,
        fg_color=COLOR["suave"],
        text_color=COLOR["texto"],
    )
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
