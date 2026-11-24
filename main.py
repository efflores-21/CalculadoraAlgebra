"""Ventana principal y navegación de Calculadora de Álgebra Lineal."""

import importlib
import os
import subprocess
import sys
import unicodedata
from tkinter import TclError

# Permite ejecutar main.py desde cualquier carpeta (o con doble clic).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _asegurar_customtkinter():
    """Instala CustomTkinter con pip la primera vez, si hace falta."""
    try:
        importlib.import_module("customtkinter")
        return
    except ImportError:
        pass
    print("CustomTkinter no está instalado. Instalándolo (solo la primera vez)...")
    comando = [sys.executable, "-m", "pip", "install", "customtkinter"]
    if subprocess.call(comando) != 0:
        subprocess.call(comando + ["--user"])
    importlib.invalidate_caches()
    try:
        importlib.import_module("customtkinter")
    except ImportError:
        mensaje = (
            "No se pudo instalar CustomTkinter automáticamente.\n"
            "Revisa la conexión a internet o ejecuta:\n\n"
            f"  {sys.executable} -m pip install customtkinter"
        )
        print(mensaje)
        try:
            from tkinter import Tk, messagebox
            raiz = Tk()
            raiz.withdraw()
            messagebox.showerror("Calculadora de Álgebra Lineal", mensaje)
        except Exception:
            input("Presiona Enter para salir...")
        sys.exit(1)


_asegurar_customtkinter()

import customtkinter as ctk  # noqa: E402

from modulos._comun import (  # noqa: E402
    COLOR,
    ESPACIADO,
    RADIO,
    TAMANO_TEXTO,
    boton_texto,
    etiqueta,
    fuente,
    tarjeta,
)
from modulos.modulo_determinantes import ModuloDeterminantes  # noqa: E402
from modulos.modulo_iterativos import ModuloIterativos  # noqa: E402
from modulos.modulo_lu import ModuloLU  # noqa: E402
from modulos.modulo_matrices import ModuloMatrices  # noqa: E402
from modulos.modulo_metodos_numericos import ModuloMetodosNumericos  # noqa: E402
from modulos.modulo_operaciones_vectores import ModuloOperacionesVectores  # noqa: E402
from modulos.modulo_propiedades import ModuloPropiedades  # noqa: E402
from modulos.modulo_sistemas import ModuloSistemas  # noqa: E402
from modulos.modulo_transformaciones import ModuloTransformaciones  # noqa: E402
from modulos.modulo_vectores import ModuloVectores  # noqa: E402
from modulos._diagnostico_ui import (
    ACTIVO as DIAGNOSTICO_UI,
    configurar_variante_scroll_inicio,
    instalar_raiz,
    instrumentar_inicio,
    medir_navegacion,
    registrar,
)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "modulos", "tema_minimalista.json")
)

# (clave, título, descripción) de cada módulo.
MODULOS = (
    ("sistemas", "Sistemas de ecuaciones", "Resuelve Ax = b con Gauss o Gauss-Jordan y comprueba la solución."),
    ("operaciones_vectores", "Operaciones con vectores", "Suma, resta, escalares y combinación lineal de vectores."),
    ("vectores", "Independencia lineal", "Decide si un conjunto de vectores es linealmente independiente."),
    ("matrices", "Operaciones con matrices", "Suma, resta, producto, traspuesta e inversa de matrices."),
    ("determinantes", "Determinantes", "Calcula det(A) paso a paso y analiza si A tiene inversa."),
    ("lu", "Factorización LU", "Factoriza A = LU y resuelve sistemas mediante sustituciones."),
    ("propiedades", "Propiedades de matrices", "Explora productos, transposición, inversas y determinantes."),
    ("transformaciones", "Transformaciones lineales", "Calcula núcleo, imagen, rango y nulidad."),
    ("metodos_numericos", "Métodos numéricos", "Bisección, gráficas, notación posicional y errores numéricos."),
    ("iterativos", "Jacobi y Gauss-Seidel", "Resuelve Ax = b con métodos iterativos y compara convergencia."),
)

CATEGORIAS = (
    ("Sistemas lineales", ("sistemas", "lu", "iterativos")),
    ("Matrices", ("matrices", "determinantes", "propiedades")),
    ("Vectores y transformaciones", ("operaciones_vectores", "vectores", "transformaciones")),
    ("Métodos numéricos", ("metodos_numericos",)),
)

CLASES_MODULOS = {
    "sistemas": ModuloSistemas,
    "operaciones_vectores": ModuloOperacionesVectores,
    "vectores": ModuloVectores,
    "matrices": ModuloMatrices,
    "lu": ModuloLU,
    "determinantes": ModuloDeterminantes,
    "propiedades": ModuloPropiedades,
    "transformaciones": ModuloTransformaciones,
    "metodos_numericos": ModuloMetodosNumericos,
    "iterativos": ModuloIterativos,
}


def _normalizar(texto):
    """Prepara texto para búsquedas sin distinguir mayúsculas ni tildes."""
    return "".join(
        caracter for caracter in unicodedata.normalize("NFD", texto.casefold())
        if unicodedata.category(caracter) != "Mn"
    )


def buscar_modulos(consulta=""):
    """Devuelve las herramientas cuyo título, descripción o categoría coincide."""
    termino = _normalizar(consulta.strip())
    categorias_por_modulo = {
        clave: categoria
        for categoria, claves in CATEGORIAS
        for clave in claves
    }
    return tuple(
        modulo for modulo in MODULOS
        if not termino or termino in _normalizar(
            " ".join((modulo[1], modulo[2], categorias_por_modulo[modulo[0]]))
        )
    )


class MenuPrincipal(ctk.CTk):
    """Ventana única con navegación lateral y un área central dinámica."""

    def __init__(self):
        super().__init__()
        instalar_raiz(self)
        self.title("Calculadora de Álgebra Lineal")
        escala = ctk.ScalingTracker.get_window_scaling(self)
        ancho = int(min(1360, self.winfo_screenwidth() / escala - 40))
        alto = int(min(900, self.winfo_screenheight() / escala - 90))
        self.geometry(f"{ancho}x{alto}")
        self.minsize(min(980, ancho), min(640, alto))
        self.configure(fg_color=COLOR["fondo"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.paneles = {}
        self.inicio = None
        self._consulta_inicio = None
        self.modulo_activo = None
        self.consulta = ctk.StringVar(self, value="")
        self._construir_shell()
        self._mostrar_inicio()
        self.after(0, self._maximizar)

    def _maximizar(self):
        """Solicita maximizar conservando la barra de título del sistema."""
        try:
            if sys.platform.startswith("win") or sys.platform.startswith("linux"):
                self.state("zoomed")
        except (TclError, AttributeError):
            # La geometría inicial sigue siendo utilizable en gestores sin zoom.
            pass

    def _construir_shell(self):
        self.sidebar = ctk.CTkFrame(
            self, width=276, fg_color=COLOR["fondo_secundario"], corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(5, weight=1)

        marca = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        marca.grid(row=0, column=0, sticky="ew", padx=18, pady=(22, 22))
        insignia = ctk.CTkLabel(
            marca, text="CA", width=42, height=42, corner_radius=13,
            fg_color=COLOR["acento"], text_color=COLOR["texto_acento"],
            font=fuente(15, negrita=True),
        )
        insignia.pack(side="left", padx=(0, 11))
        bloque = ctk.CTkFrame(marca, fg_color="transparent")
        bloque.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            bloque, text="Calculadora", font=fuente(15, negrita=True),
            text_color=COLOR["texto"], anchor="w",
        ).pack(anchor="w")
        etiqueta(bloque, "ÁLGEBRA LINEAL", tamano=10, color="gris").pack(anchor="w")

        self.boton_inicio = ctk.CTkButton(
            self.sidebar, text="⌂   Inicio", anchor="w", height=42,
            corner_radius=RADIO["md"], font=fuente(14, negrita=True),
            command=self.mostrar_menu,
        )
        self.boton_inicio.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 18))

        etiqueta(self.sidebar, "HERRAMIENTAS", tamano=10, negrita=True, color="gris").grid(
            row=2, column=0, sticky="w", padx=20, pady=(0, 9)
        )
        self.busqueda = ctk.CTkEntry(
            self.sidebar, textvariable=self.consulta, placeholder_text="Buscar herramienta…",
            height=42, corner_radius=RADIO["md"], border_color=COLOR["borde"],
        )
        self.busqueda.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 10))
        self.busqueda.bind("<KeyRelease>", self._actualizar_navegacion)

        self.navegacion = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent", corner_radius=0,
        )
        self.navegacion.grid(row=4, column=0, rowspan=2, sticky="nsew", padx=8)
        self._actualizar_navegacion()

        pie = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        pie.grid(row=6, column=0, sticky="ew", padx=20, pady=16)
        etiqueta(pie, "Aprende cada paso del cálculo", tamano=11, color="gris").pack(anchor="w")
        boton_texto(pie, "Salir", self.destroy, width=70).pack(anchor="w", pady=(8, 0))

        self.area_principal = ctk.CTkFrame(self, fg_color=COLOR["fondo"], corner_radius=0)
        self.area_principal.grid(row=0, column=1, sticky="nsew")
        self.area_principal.grid_rowconfigure(0, weight=1)
        self.area_principal.grid_columnconfigure(0, weight=1)

    def _actualizar_navegacion(self, evento=None):
        destruidos = sum(contar_widgets_diagnostico(widget) for widget in self.navegacion.winfo_children()) if DIAGNOSTICO_UI else 0
        for widget in self.navegacion.winfo_children():
            widget.destroy()
        encontrados = {modulo[0] for modulo in buscar_modulos(self.consulta.get())}
        for categoria, claves in CATEGORIAS:
            visibles = [clave for clave in claves if clave in encontrados]
            if not visibles:
                continue
            etiqueta(self.navegacion, categoria.upper(), tamano=10, negrita=True, color="gris").pack(
                anchor="w", padx=12, pady=(16, 6)
            )
            for clave in visibles:
                _, titulo, _ = next(modulo for modulo in MODULOS if modulo[0] == clave)
                activo = self.modulo_activo == clave
                boton = ctk.CTkButton(
                    self.navegacion, text=titulo, anchor="w", height=39,
                    corner_radius=RADIO["sm"], font=fuente(13),
                    fg_color=COLOR["interaccion"] if activo else "transparent",
                    text_color=COLOR["texto"], hover_color=COLOR["hover_claro"],
                    command=lambda nombre=clave: self.mostrar_modulo(nombre),
                )
                boton.pack(fill="x", padx=4, pady=2)
        self.boton_inicio.configure(
            fg_color=COLOR["interaccion"] if self.modulo_activo is None else COLOR["primario"],
            text_color=COLOR["texto"] if self.modulo_activo is None else COLOR["texto_acento"],
        )
        if DIAGNOSTICO_UI:
            creados = sum(contar_widgets_diagnostico(widget) for widget in self.navegacion.winfo_children())
            registrar("navegacion_widgets", funcion="_actualizar_navegacion",
                      widgets_destruidos=destruidos, widgets_reconstruidos=creados)

    def _limpiar_area(self):
        ocultos = destruidos = 0
        paneles_existentes = tuple(self.paneles.values())
        contenedor_inicio = getattr(getattr(self, "inicio", None), "_parent_frame", None)
        for widget in self.area_principal.winfo_children():
            if widget is contenedor_inicio:
                self.inicio.grid_remove()
                ocultos += contar_widgets_diagnostico(widget) if DIAGNOSTICO_UI else 1
            elif widget in paneles_existentes:
                widget.grid_remove()
                ocultos += contar_widgets_diagnostico(widget) if DIAGNOSTICO_UI else 1
            else:
                # La vista de Inicio no conserva estado propio; se vuelve a
                # construir al regresar, mientras los módulos quedan en caché.
                destruidos += contar_widgets_diagnostico(widget) if DIAGNOSTICO_UI else 1
                widget.destroy()
        if DIAGNOSTICO_UI:
            registrar("limpieza_area", widgets_ocultos=ocultos, widgets_destruidos=destruidos,
                      modulos_retenidos=len(self.paneles), modulo_activo=self.modulo_activo)

    def _mostrar_inicio(self):
        self.modulo_activo = None
        self._limpiar_area()
        if self.inicio is None:
            self.inicio = ctk.CTkScrollableFrame(self.area_principal, fg_color="transparent")
        configurar_variante_scroll_inicio(self.inicio)
        instrumentar_inicio(self.inicio)
        self.inicio.grid(
            row=0, column=0, sticky="nsew", padx=ESPACIADO["lg"], pady=ESPACIADO["lg"]
        )
        consulta_inicio = self.consulta.get()
        if self._consulta_inicio != consulta_inicio:
            widgets_eliminados = sum(
                contar_widgets_diagnostico(widget) for widget in self.inicio.winfo_children()
            ) if DIAGNOSTICO_UI else 0
            for widget in self.inicio.winfo_children():
                widget.destroy()
            if DIAGNOSTICO_UI:
                registrar("dashboard_contenido_eliminado", widgets=widgets_eliminados,
                          consulta_anterior=self._consulta_inicio, consulta_nueva=consulta_inicio)
            self._construir_contenido_inicio()
            self._consulta_inicio = consulta_inicio
        self._actualizar_navegacion()

    def _construir_contenido_inicio(self):
        antes = sum(contar_widgets_diagnostico(widget) for widget in self.inicio.winfo_children()) if DIAGNOSTICO_UI else 0
        inicio = self.inicio
        contenido = ctk.CTkFrame(inicio, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=8, pady=8)
        etiqueta(contenido, "ESPACIO DE APRENDIZAJE", tamano=11, negrita=True, color="acento").pack(
            anchor="w", pady=(12, 5)
        )
        ctk.CTkLabel(
            contenido, text="¿Qué quieres resolver hoy?",
            font=fuente(TAMANO_TEXTO["titulo"] + 6, negrita=True),
            text_color=COLOR["texto"], anchor="w",
        ).pack(anchor="w")
        descripcion_inicio = etiqueta(
            contenido,
            "Explora el álgebra lineal con procedimientos claros, cálculos exactos y comprobaciones paso a paso.",
            tamano=15, color="gris", wraplength=820, justify="left", anchor="w",
        )
        descripcion_inicio.pack(anchor="w", fill="x", pady=(8, 24))
        contenido.bind(
            "<Configure>",
            lambda evento: descripcion_inicio.configure(wraplength=max(220, evento.width - 20)),
        )

        acceso = tarjeta(contenido)
        acceso.pack(fill="x", pady=(0, 24))
        acceso.grid_columnconfigure((0, 1, 2), weight=1, uniform="accesos")
        destacados = ("sistemas", "matrices", "metodos_numericos")
        for columna, clave in enumerate(destacados):
            modulo = next(item for item in MODULOS if item[0] == clave)
            self._crear_acceso(acceso, modulo).grid(
                row=0, column=columna, sticky="nsew", padx=8, pady=10
            )

        for categoria, claves in CATEGORIAS:
            resultados = [item for item in buscar_modulos(self.consulta.get()) if item[0] in claves]
            if not resultados:
                continue
            cabecera = ctk.CTkFrame(contenido, fg_color="transparent")
            cabecera.pack(fill="x", pady=(8, 7))
            ctk.CTkLabel(
                cabecera, text=categoria, font=fuente(19, negrita=True),
                text_color=COLOR["texto"], anchor="w",
            ).pack(side="left")
            etiqueta(cabecera, f"{len(resultados)} herramientas", tamano=11, color="gris").pack(side="right")
            rejilla = ctk.CTkFrame(contenido, fg_color="transparent")
            rejilla.pack(fill="x", pady=(0, 12))
            rejilla.grid_columnconfigure((0, 1), weight=1, uniform="herramientas")
            for indice, modulo in enumerate(resultados):
                self._crear_acceso(rejilla, modulo).grid(
                    row=indice // 2, column=indice % 2, sticky="nsew",
                    padx=(0, 9) if indice % 2 == 0 else (9, 0), pady=5,
                )
        if DIAGNOSTICO_UI:
            despues = sum(contar_widgets_diagnostico(widget) for widget in self.inicio.winfo_children())
            registrar("dashboard_contenido", widgets_antes=antes, widgets_despues=despues,
                      widgets_creados=max(0, despues - antes), consulta=self.consulta.get())
    def _crear_acceso(self, parent, modulo):
        clave, titulo, descripcion = modulo
        caja = tarjeta(parent)
        caja.grid_columnconfigure(0, weight=1)
        caja.grid_rowconfigure(1, weight=1)

        titulo_etiqueta = ctk.CTkLabel(
            caja, text=titulo, font=fuente(15, negrita=True),
            text_color=COLOR["texto"], anchor="w", justify="left", wraplength=280,
        )
        titulo_etiqueta.grid(row=0, column=0, sticky="ew", padx=16, pady=(15, 5))
        descripcion_etiqueta = ctk.CTkLabel(
            caja, text=descripcion, font=fuente(13), text_color=COLOR["gris"],
            anchor="nw", justify="left", wraplength=280,
        )
        descripcion_etiqueta.grid(row=1, column=0, sticky="new", padx=16, pady=(0, 8))
        accion = ctk.CTkButton(
            caja, text="Abrir herramienta  →", anchor="w", height=30,
            corner_radius=RADIO["sm"], fg_color="transparent",
            hover_color=COLOR["interaccion"], text_color=COLOR["acento"],
            font=fuente(12, negrita=True),
            command=lambda: self.mostrar_modulo(clave),
        )
        accion.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 9))

        def ajustar_texto(evento):
            ancho_texto = max(100, evento.width - 36)
            titulo_etiqueta.configure(wraplength=ancho_texto)
            descripcion_etiqueta.configure(wraplength=ancho_texto)

        caja.bind("<Configure>", ajustar_texto)
        return caja

    def mostrar_modulo(self, nombre):
        """Muestra el módulo en el área central de esta misma ventana."""
        if nombre not in CLASES_MODULOS:
            raise ValueError(f"Módulo desconocido: {nombre}")
        self._limpiar_area()
        if nombre not in self.paneles:
            self.paneles[nombre] = CLASES_MODULOS[nombre](self.area_principal, self.mostrar_menu)
            if DIAGNOSTICO_UI:
                registrar("modulo_construido", modulo=nombre,
                          widgets=contar_widgets_diagnostico(self.paneles[nombre]),
                          modulos_retenidos=len(self.paneles))
        self.modulo_activo = nombre
        self.paneles[nombre].grid(row=0, column=0, sticky="nsew")
        self._actualizar_navegacion()

    def mostrar_menu(self):
        """Regresa al dashboard sin cerrar la ventana ni perder entradas."""
        self._mostrar_inicio()


def contar_widgets_diagnostico(widget):
    from modulos._diagnostico_ui import contar_widgets
    return contar_widgets(widget)


for _nombre_metodo_diagnostico in (
    "_limpiar_area", "_mostrar_inicio", "_construir_contenido_inicio",
    "_actualizar_navegacion", "mostrar_modulo", "mostrar_menu",
):
    setattr(MenuPrincipal, _nombre_metodo_diagnostico,
            medir_navegacion(getattr(MenuPrincipal, _nombre_metodo_diagnostico)))


if __name__ == "__main__":
    aplicacion = MenuPrincipal()
    aplicacion.mainloop()
