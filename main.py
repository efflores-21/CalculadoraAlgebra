"""Menú principal que navega entre módulos dentro de una sola ventana."""

import importlib
import os
import subprocess
import sys

# Permite ejecutar main.py desde cualquier carpeta (o con doble clic):
# los paquetes backend/ y modulos/ se buscan junto a este archivo.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _asegurar_customtkinter():
    """Instala CustomTkinter con pip la primera vez, si la computadora no lo tiene."""
    try:
        importlib.import_module("customtkinter")
        return
    except ImportError:
        pass
    print("CustomTkinter no está instalado. Instalándolo (solo la primera vez)...")
    comando = [sys.executable, "-m", "pip", "install", "customtkinter"]
    if subprocess.call(comando) != 0:
        # Sin permisos de administrador, se reintenta en la carpeta del usuario.
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

from modulos._comun import COLOR, boton_texto, etiqueta, fuente, tarjeta
from modulos.modulo_determinantes import ModuloDeterminantes
from modulos.modulo_matrices import ModuloMatrices
from modulos.modulo_operaciones_vectores import ModuloOperacionesVectores
from modulos.modulo_propiedades import ModuloPropiedades
from modulos.modulo_sistemas import ModuloSistemas
from modulos.modulo_vectores import ModuloVectores

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "modulos", "tema_minimalista.json")
)

# (clave, título, descripción) de cada módulo, en el orden del menú.
MODULOS = (
    ("sistemas", "Sistemas de ecuaciones",
     "Resuelve Ax = b con Gauss o Gauss-Jordan y comprueba la solución."),
    ("operaciones_vectores", "Vectores y combinación lineal",
     "Suma, resta y escalar de vectores. ¿Es b combinación lineal?"),
    ("vectores", "Independencia lineal",
     "Decide si un conjunto de vectores es L.I. o L.D."),
    ("matrices", "Operaciones con matrices",
     "Suma, resta, producto, traspuesta e inversa de matrices."),
    ("determinantes", "Determinantes",
     "Calcula det(A) paso a paso y dice si A tiene inversa."),
    ("propiedades", "Producto matriz-vector",
     "Comprueba A(u + v) = Au + Av y A(cu) = c(Au)."),
)


class MenuPrincipal(ctk.CTk):
    """Contenedor único para el menú y los paneles de cada módulo."""

    def __init__(self):
        """Prepara la ventana, el menú inicial y el contenedor de módulos."""
        super().__init__()
        self.title("Calculadora de Álgebra Lineal")
        # Tamaño cómodo que nunca excede la pantalla (laptops pequeñas incluidas).
        escala = ctk.ScalingTracker.get_window_scaling(self)
        ancho = int(min(1280, self.winfo_screenwidth() / escala - 40))
        alto = int(min(860, self.winfo_screenheight() / escala - 90))
        self.geometry(f"{ancho}x{alto}")
        self.minsize(min(980, ancho), min(640, alto))
        self.configure(fg_color=COLOR["fondo"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.paneles = {}
        self._construir_menu()

    def _construir_menu(self):
        """Crea la pantalla de inicio: una tarjeta por módulo, en dos columnas."""
        self.menu_frame = ctk.CTkFrame(self, fg_color=COLOR["fondo"], corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nsew")
        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        encabezado.grid(row=0, column=0, pady=(48, 28))
        etiqueta(encabezado, "ÁLGEBRA LINEAL", tamano=12, negrita=True).pack()
        ctk.CTkLabel(
            encabezado,
            text="Calculadora",
            font=fuente(40, negrita=True),
            text_color=COLOR["texto"],
        ).pack()
        etiqueta(
            encabezado,
            "Elige qué quieres calcular. Cada módulo te guía paso a paso.",
            tamano=15,
        ).pack(pady=(4, 0))

        rejilla = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        rejilla.grid(row=1, column=0, sticky="n", padx=40)
        rejilla.grid_columnconfigure((0, 1), weight=1, uniform="tarjetas")
        for indice, (clave, titulo, descripcion) in enumerate(MODULOS):
            self._crear_tarjeta_modulo(rejilla, indice + 1, clave, titulo, descripcion).grid(
                row=indice // 2, column=indice % 2, padx=10, pady=10, sticky="nsew"
            )

        pie = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        pie.grid(row=2, column=0, pady=(10, 28))
        etiqueta(
            pie, "Resultados exactos con fracciones  ·  Sin NumPy ni SciPy", tamano=12
        ).pack()
        boton_texto(pie, "Salir", self.destroy, width=90).pack(pady=(8, 0))

    def _crear_tarjeta_modulo(self, parent, numero, clave, titulo, descripcion):
        """Tarjeta clicable: número, título, descripción corta y 'Abrir'."""
        caja = tarjeta(parent, width=440, height=150, cursor="hand2")
        caja.grid_propagate(False)
        caja.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            caja,
            text=f"{numero:02d}",
            width=44,
            height=44,
            corner_radius=12,
            fg_color=COLOR["negro"],
            text_color="#FFFFFF",
            font=fuente(15, negrita=True),
        ).grid(row=0, column=0, rowspan=2, sticky="nw", padx=(22, 16), pady=22)
        ctk.CTkLabel(
            caja, text=titulo, font=fuente(17, negrita=True), text_color=COLOR["texto"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(0, 22), pady=(20, 0))
        etiqueta(
            caja, descripcion, tamano=13, justify="left", anchor="w", wraplength=320
        ).grid(row=1, column=1, sticky="nw", padx=(0, 22), pady=(2, 0))
        etiqueta(caja, "Abrir  →", tamano=13, color="texto", negrita=True).grid(
            row=2, column=1, sticky="w", padx=(0, 22), pady=(0, 18)
        )
        caja.grid_rowconfigure(1, weight=1)

        def abrir(evento=None):
            self.mostrar_modulo(clave)

        def resaltar(activo):
            caja.configure(border_color=COLOR["negro"] if activo else COLOR["borde"])

        for widget in [caja] + caja.winfo_children():
            widget.bind("<Button-1>", abrir)
            widget.bind("<Enter>", lambda evento: resaltar(True))
            widget.bind("<Leave>", lambda evento: resaltar(False))
            widget.configure(cursor="hand2")
        return caja

    def mostrar_modulo(self, nombre):
        """Oculta el menú y presenta el módulo elegido en la ventana principal."""
        clases = {
            "sistemas": ModuloSistemas,
            "operaciones_vectores": ModuloOperacionesVectores,
            "vectores": ModuloVectores,
            "matrices": ModuloMatrices,
            "determinantes": ModuloDeterminantes,
            "propiedades": ModuloPropiedades,
        }
        if nombre not in clases:
            raise ValueError(f"Módulo desconocido: {nombre}")

        self.menu_frame.grid_remove()
        if nombre not in self.paneles:
            self.paneles[nombre] = clases[nombre](self, self.mostrar_menu)
        for panel in self.paneles.values():
            panel.grid_forget()
        self.paneles[nombre].grid(row=0, column=0, sticky="nsew")

    def mostrar_menu(self):
        """Oculta el módulo activo y regresa a la pantalla principal."""
        for panel in self.paneles.values():
            panel.grid_forget()
        self.menu_frame.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    aplicacion = MenuPrincipal()
    aplicacion.mainloop()
