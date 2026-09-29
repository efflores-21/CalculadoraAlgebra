"""Menú principal que navega entre módulos dentro de una sola ventana."""

import customtkinter as ctk

from modulos.modulo_determinantes import ModuloDeterminantes
from modulos.modulo_matrices import ModuloMatrices
from modulos.modulo_operaciones_vectores import ModuloOperacionesVectores
from modulos.modulo_propiedades import ModuloPropiedades
from modulos.modulo_sistemas import ModuloSistemas
from modulos.modulo_vectores import ModuloVectores

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MenuPrincipal(ctk.CTk):
    """Contenedor único para el menú y los paneles de cada módulo."""

    def __init__(self):
        """Prepara la ventana, el menú inicial y el contenedor de módulos."""
        super().__init__()
        self.title("Calculadora de Álgebra Lineal")
        self.geometry("1100x850")
        self.minsize(900, 680)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.paneles = {}
        self._construir_menu()

    def _construir_menu(self):
        """Crea la pantalla de inicio con opciones que cambian el panel visible."""
        self.menu_frame = ctk.CTkFrame(self, corner_radius=16)
        self.menu_frame.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.menu_frame,
            text="CALCULADORA DE ÁLGEBRA LINEAL",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(24, 8))
        ctk.CTkLabel(
            self.menu_frame,
            text="Selecciona un módulo para comenzar.",
            font=ctk.CTkFont(size=15),
            text_color="#AAB7C4",
        ).grid(row=1, column=0, padx=20, pady=(0, 10))

        botones = (
            ("1. Sistemas de ecuaciones", "sistemas"),
            ("2. Operaciones con vectores y combinación lineal", "operaciones_vectores"),
            ("3. Independencia lineal de vectores", "vectores"),
            ("4. Operaciones con matrices", "matrices"),
            ("5. Determinantes", "determinantes"),
            ("6. Propiedades del producto matriz-vector", "propiedades"),
        )
        lista_modulos = ctk.CTkScrollableFrame(
            self.menu_frame,
            label_text="Módulos disponibles",
            fg_color="transparent",
        )
        lista_modulos.grid(row=2, column=0, sticky="nsew", padx=50, pady=4)
        lista_modulos.grid_columnconfigure(0, weight=1)
        for etiqueta, clave in botones:
            ctk.CTkButton(
                lista_modulos,
                text=etiqueta,
                height=48,
                font=ctk.CTkFont(size=15, weight="bold"),
                command=lambda modulo=clave: self.mostrar_modulo(modulo),
            ).pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            self.menu_frame,
            text="Cálculos exactos con Fraction. No se utilizan NumPy ni SciPy.",
            font=ctk.CTkFont(size=12),
            text_color="#AAB7C4",
        ).grid(row=3, column=0, padx=20, pady=(6, 4))
        ctk.CTkButton(
            self.menu_frame,
            text="Salir",
            fg_color="transparent",
            border_width=1,
            command=self.destroy,
        ).grid(row=4, column=0, padx=60, pady=(4, 16), sticky="ew")

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
        self.paneles[nombre].grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

    def mostrar_menu(self):
        """Oculta el módulo activo y regresa a la pantalla principal."""
        for panel in self.paneles.values():
            panel.grid_forget()
        self.menu_frame.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)


if __name__ == "__main__":
    aplicacion = MenuPrincipal()
    aplicacion.mainloop()
