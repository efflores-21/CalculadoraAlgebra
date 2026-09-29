"""Menú principal que navega entre módulos dentro de una sola ventana."""

import customtkinter as ctk

from modulos.modulo_determinantes import ModuloDeterminantes
from modulos.modulo_matrices import ModuloMatrices
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

        ctk.CTkLabel(
            self.menu_frame,
            text="CALCULADORA DE ÁLGEBRA LINEAL",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(padx=20, pady=(50, 8))
        ctk.CTkLabel(
            self.menu_frame,
            text="Selecciona un módulo. La calculadora permanecerá en esta ventana.",
            font=ctk.CTkFont(size=15),
            text_color="#AAB7C4",
        ).pack(padx=20, pady=(0, 30))

        botones = (
            ("Módulo 1 - Sistemas de ecuaciones", "sistemas"),
            ("Módulo 2 - Vectores e independencia lineal", "vectores"),
            ("Módulo 3 - Álgebra de matrices", "matrices"),
            ("Módulo 4 - Determinantes", "determinantes"),
        )
        for etiqueta, clave in botones:
            ctk.CTkButton(
                self.menu_frame,
                text=etiqueta,
                height=54,
                font=ctk.CTkFont(size=16, weight="bold"),
                command=lambda modulo=clave: self.mostrar_modulo(modulo),
            ).pack(fill="x", padx=150, pady=8)

        ctk.CTkLabel(
            self.menu_frame,
            text="Cálculos exactos con Fraction. No se utilizan NumPy ni SciPy.",
            font=ctk.CTkFont(size=12),
            text_color="#AAB7C4",
        ).pack(padx=20, pady=(24, 8))
        ctk.CTkButton(
            self.menu_frame,
            text="Salir",
            fg_color="transparent",
            border_width=1,
            command=self.destroy,
        ).pack(padx=150, pady=(8, 35), fill="x")

    def mostrar_modulo(self, nombre):
        """Oculta el menú y presenta el módulo elegido en la ventana principal."""
        clases = {
            "sistemas": ModuloSistemas,
            "vectores": ModuloVectores,
            "matrices": ModuloMatrices,
            "determinantes": ModuloDeterminantes,
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
