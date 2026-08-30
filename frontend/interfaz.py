"""
Módulo de interfaz gráfica de usuario (GUI) usando tkinter.
Permite ingresar los datos, resolver y mostrar resultados con fracciones.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction

from backend.matriz import crear_matriz_aumentada
from backend.eliminacion import resolver_sistema
from backend.clasificador import clasificar_sistema


class InterfazCalculadora:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Álgebra Lineal")
        self.root.geometry("1000x750")

        # Variables para dimensiones
        self.m_var = tk.IntVar(value=2)
        self.n_var = tk.IntVar(value=2)

        # Contenedores para entradas
        self.entradas_coef = []   # lista de listas de Entry
        self.entradas_b = []      # lista de Entry

        self.crear_widgets()
        self.actualizar_tabla()

    def crear_widgets(self):
        # Frame superior: dimensiones
        frame_dim = ttk.LabelFrame(self.root, text="Dimensiones del sistema")
        frame_dim.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(frame_dim, text="Ecuaciones (m):").grid(row=0, column=0, padx=5, pady=5)
        spin_m = ttk.Spinbox(frame_dim, from_=1, to=10, textvariable=self.m_var, width=5,
                             command=self.actualizar_tabla)
        spin_m.grid(row=0, column=1, padx=5)

        ttk.Label(frame_dim, text="Variables (n):").grid(row=0, column=2, padx=5, pady=5)
        spin_n = ttk.Spinbox(frame_dim, from_=1, to=10, textvariable=self.n_var, width=5,
                             command=self.actualizar_tabla)
        spin_n.grid(row=0, column=3, padx=5)

        # Frame para la tabla de coeficientes (con scroll)
        self.frame_tabla = ttk.LabelFrame(self.root, text="Matriz aumentada [A | b] (ingrese fracciones o decimales)")
        self.frame_tabla.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_tabla)
        self.scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Botones
        frame_botones = ttk.Frame(self.root)
        frame_botones.pack(pady=10)

        ttk.Button(frame_botones, text="Resolver", command=self.resolver).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_botones, text="Limpiar", command=self.limpiar).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_botones, text="Salir", command=self.root.quit).pack(side=tk.LEFT, padx=10)

        # Área de resultados (texto)
        self.text_resultados = tk.Text(self.root, height=18, width=100, state=tk.DISABLED)
        self.text_resultados.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def actualizar_tabla(self):
        """Reconstruye la tabla de entradas según m y n."""
        # Limpiar frame anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entradas_coef = []
        self.entradas_b = []

        m = self.m_var.get()
        n = self.n_var.get()

        # Encabezados
        for j in range(n):
            ttk.Label(self.scrollable_frame, text=f"x{j+1}", font=('Arial', 10, 'bold')).grid(
                row=0, column=j, padx=2, pady=2)
        ttk.Label(self.scrollable_frame, text="|  b", font=('Arial', 10, 'bold')).grid(
            row=0, column=n, padx=5, pady=2)

        # Filas de entrada
        for i in range(m):
            fila_entries = []
            for j in range(n):
                entry = ttk.Entry(self.scrollable_frame, width=10)
                entry.grid(row=i+1, column=j, padx=2, pady=2)
                entry.insert(0, "0")
                fila_entries.append(entry)
            self.entradas_coef.append(fila_entries)

            entry_b = ttk.Entry(self.scrollable_frame, width=10)
            entry_b.grid(row=i+1, column=n, padx=5, pady=2)
            entry_b.insert(0, "0")
            self.entradas_b.append(entry_b)

    def leer_datos(self):
        """Lee los valores de las entradas y los convierte a Fraction."""
        m = self.m_var.get()
        n = self.n_var.get()
        coeficientes = []
        terminos = []

        try:
            for i in range(m):
                fila = []
                for j in range(n):
                    texto = self.entradas_coef[i][j].get().strip()
                    if texto == "":
                        texto = "0"
                    # Convertir a Fraction (acepta "1/2", "0.5", etc.)
                    fila.append(Fraction(texto))
                coeficientes.append(fila)

                texto_b = self.entradas_b[i].get().strip()
                if texto_b == "":
                    texto_b = "0"
                terminos.append(Fraction(texto_b))
        except Exception as e:
            messagebox.showerror("Error de entrada", f"Dato inválido: {e}\nUse fracciones como 1/2 o decimales.")
            return None, None, None, None

        return m, n, coeficientes, terminos

    def resolver(self):
        """Ejecuta la resolución y muestra los resultados."""
        self.text_resultados.config(state=tk.NORMAL)
        self.text_resultados.delete(1.0, tk.END)

        datos = self.leer_datos()
        if datos[0] is None:
            self.text_resultados.config(state=tk.DISABLED)
            return

        m, n, coeficientes, terminos = datos

        try:
            matriz_aum = crear_matriz_aumentada(m, n, coeficientes, terminos)
            resultado = resolver_sistema(matriz_aum)
            clasificacion = clasificar_sistema(resultado['matriz_escalonada'], resultado['rango'])

            self.mostrar_resultados(clasificacion, resultado, coeficientes, terminos)

        except Exception as e:
            messagebox.showerror("Error", f"Error al resolver: {e}")

        self.text_resultados.config(state=tk.DISABLED)

    def mostrar_resultados(self, clasificacion, resultado, coeficientes, terminos):
        """Vuelca la información en el área de texto."""
        texto = self.text_resultados
        texto.insert(tk.END, "="*70 + "\n")
        texto.insert(tk.END, "CLASIFICACIÓN DEL SISTEMA\n")
        texto.insert(tk.END, f"Tipo: {clasificacion['tipo']}\n")
        texto.insert(tk.END, f"Descripción: {clasificacion['descripcion']}\n")
        texto.insert(tk.END, "="*70 + "\n\n")

        if clasificacion['tipo'] != 'Inconsistente':
            texto.insert(tk.END, "SOLUCIÓN:\n")
            soluciones = resultado['soluciones']
            n = len(coeficientes[0])
            for var in range(n):
                if var in resultado['variables_libres']:
                    texto.insert(tk.END, f"  x{var+1} = t_{var+1} (variable libre)\n")
                else:
                    valor = soluciones.get(var, Fraction(0,1))
                    # Si el denominador es 1, mostrar solo el numerador
                    if valor.denominator == 1:
                        texto.insert(tk.END, f"  x{var+1} = {valor.numerator}\n")
                    else:
                        texto.insert(tk.END, f"  x{var+1} = {valor}\n")
            texto.insert(tk.END, "\n")

            # Verificación
            texto.insert(tk.END, "VERIFICACIÓN (sustituyendo en el sistema original):\n")
            sols_verif = soluciones.copy()
            for var in resultado['variables_libres']:
                sols_verif[var] = Fraction(0, 1)

            todas_ok = True
            for i, fila in enumerate(coeficientes):
                suma = Fraction(0, 1)
                for j, coef in enumerate(fila):
                    suma += coef * sols_verif.get(j, Fraction(0, 1))
                esperado = terminos[i]
                ok = (suma == esperado)
                if not ok:
                    todas_ok = False
                texto.insert(tk.END, f"  Ecuación {i+1}: {suma} = {esperado}  {'[OK]' if ok else '[ERROR]'}\n")
            texto.insert(tk.END, f"\nResultado de la verificación: {'TODAS LAS ECUACIONES OK' if todas_ok else 'ALGUNAS ECUACIONES NO COINCIDEN'}\n")

            # Mostrar matriz escalonada
            texto.insert(tk.END, "\nMATRIZ ESCALONADA FINAL:\n")
            for fila in resultado['matriz_escalonada']:
                fila_str = "  ".join(str(elem) for elem in fila)
                texto.insert(tk.END, f"  {fila_str}\n")
        else:
            texto.insert(tk.END, "No hay solución que verificar.\n")

        texto.insert(tk.END, "\n" + "="*70 + "\n")

    def limpiar(self):
        """Limpia el área de resultados y reinicia las entradas a 0."""
        self.text_resultados.config(state=tk.NORMAL)
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.config(state=tk.DISABLED)

        # Reiniciar entradas a 0
        for fila in self.entradas_coef:
            for entry in fila:
                entry.delete(0, tk.END)
                entry.insert(0, "0")
        for entry in self.entradas_b:
            entry.delete(0, tk.END)
            entry.insert(0, "0")

