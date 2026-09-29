"""Componentes y validaciones comunes para las ventanas CustomTkinter."""

import customtkinter as ctk
from tkinter import messagebox

from backend.matriz import _a_fraction, formatear_valor
from modulos.teoremas.resumen_teoremas import obtener_resumen


DIMENSION_MAXIMA = 12


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
    try:
        return _a_fraction(entry.get().strip() or "0")
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f"{etiqueta} no es un número válido.") from error


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


def crear_logo(parent, texto, height=70):
    """Muestra el logotipo ASCII del módulo en una caja Courier New de solo lectura."""
    caja = ctk.CTkTextbox(
        parent,
        height=height,
        font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
        wrap="none",
    )
    caja.pack(fill="x", padx=12, pady=(12, 4))
    caja.insert("1.0", texto)
    caja.configure(state="disabled")
    return caja


def crear_resultado(parent, height=250):
    """Crea un área monoespaciada para presentar cálculos algebraicos."""
    salida = ctk.CTkTextbox(
        parent,
        height=height,
        font=ctk.CTkFont(family="Courier New", size=12),
        wrap="none",
    )
    salida.pack(fill="both", expand=True, padx=12, pady=8)
    return salida


def reemplazar_texto(caja, texto):
    """Sustituye todo el texto visible sin acumular resultados anteriores."""
    caja.configure(state="normal")
    caja.delete("1.0", "end")
    caja.insert("1.0", texto)
    caja.see("1.0")


def mensaje_error(error):
    """Muestra al usuario un error de validación de forma explícita."""
    messagebox.showerror("Error", str(error))


def mostrar_teoremas(parent, modulo, titulo):
    """Abre una ventana independiente con los teoremas del módulo."""
    contenedor = parent.winfo_toplevel()
    ventana = ctk.CTkToplevel(contenedor)
    ventana.title("Teoremas clave - " + titulo)
    ventana.geometry("720x520")
    ventana.minsize(520, 380)
    ctk.CTkLabel(
        ventana,
        text="Teoremas clave: " + titulo,
        font=ctk.CTkFont(size=20, weight="bold"),
    ).pack(padx=16, pady=(16, 4), anchor="w")
    texto = ctk.CTkTextbox(
        ventana,
        font=ctk.CTkFont(family="Courier New", size=13),
        wrap="word",
    )
    texto.pack(fill="both", expand=True, padx=16, pady=12)
    texto.insert("1.0", obtener_resumen(modulo))
    texto.configure(state="disabled")
    ventana.transient(contenedor)
    ventana.focus()
    return ventana


def entrada_numero(parent, ancho=68):
    """Crea una celda numérica centrada y seleccionable al recibir el foco."""
    entry = ctk.CTkEntry(parent, width=ancho, justify="center")
    entry.insert(0, "0")
    entry.bind("<FocusIn>", lambda evento, celda=entry: celda.select_range(0, "end"))
    return entry
