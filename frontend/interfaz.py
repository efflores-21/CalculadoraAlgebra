"""
Módulo de interfaz gráfica de usuario (GUI) usando tkinter.
Permite ingresar los datos, elegir el método y mostrar paso a paso.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction

from backend.matriz import crear_matriz_aumentada, formatear_valor, subindice
from backend.eliminacion import resolver_sistema
from backend.clasificador import clasificar_sistema


class InterfazCalculadora:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Álgebra Lineal")
        self.root.geometry("1100x800")

        self.m_var = tk.IntVar(value=2)
        self.n_var = tk.IntVar(value=2)
        self.metodo_var = tk.StringVar(value="Gauss")

        self.entradas_coef = []
        self.entradas_b = []

        self.crear_widgets()
        self.actualizar_tabla()

    def crear_widgets(self):
        frame_sup = ttk.LabelFrame(self.root, text="Configuración")
        frame_sup.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(frame_sup, text="Ecuaciones (m):").grid(row=0, column=0, padx=5, pady=5)
        spin_m = ttk.Spinbox(frame_sup, from_=1, to=10, textvariable=self.m_var, width=5,
                             command=self.actualizar_tabla)
        spin_m.grid(row=0, column=1, padx=5)

        ttk.Label(frame_sup, text="Variables (n):").grid(row=0, column=2, padx=5, pady=5)
        spin_n = ttk.Spinbox(frame_sup, from_=1, to=10, textvariable=self.n_var, width=5,
                             command=self.actualizar_tabla)
        spin_n.grid(row=0, column=3, padx=5)

        ttk.Label(frame_sup, text="Método:").grid(row=0, column=4, padx=10, pady=5)
        combo_metodo = ttk.Combobox(frame_sup, textvariable=self.metodo_var,
                                    values=["Gauss", "Gauss-Jordan"], state="readonly", width=12)
        combo_metodo.grid(row=0, column=5, padx=5)
        combo_metodo.current(0)

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

        frame_botones = ttk.Frame(self.root)
        frame_botones.pack(pady=10)

        ttk.Button(frame_botones, text="Resolver", command=self.resolver).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_botones, text="Limpiar", command=self.limpiar).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_botones, text="Salir", command=self.root.quit).pack(side=tk.LEFT, padx=10)

        frame_resultados = ttk.LabelFrame(self.root, text="Resultados y pasos")
        frame_resultados.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.text_resultados = tk.Text(frame_resultados, height=22, width=120, state=tk.DISABLED,
                                       wrap=tk.WORD, font=("Courier New", 10))
        scroll_y = ttk.Scrollbar(frame_resultados, orient="vertical", command=self.text_resultados.yview)
        self.text_resultados.configure(yscrollcommand=scroll_y.set)

        self.text_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def actualizar_tabla(self):
        """Reconstruye la tabla de entradas según m y n."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entradas_coef = []
        self.entradas_b = []

        m = self.m_var.get()
        n = self.n_var.get()

        for j in range(n):
            lbl = ttk.Label(self.scrollable_frame, text=f"x{subindice(j + 1)}", font=('Arial', 10, 'bold'))
            lbl.grid(row=0, column=j, padx=2, pady=2)
        ttk.Label(self.scrollable_frame, text="|  b", font=('Arial', 10, 'bold')).grid(row=0, column=n, padx=5, pady=2)

        for i in range(m):
            fila_entries = []
            for j in range(n):
                entry = ttk.Entry(self.scrollable_frame, width=10)
                entry.grid(row=i + 1, column=j, padx=2, pady=2)
                entry.insert(0, "0")
                fila_entries.append(entry)
            self.entradas_coef.append(fila_entries)

            entry_b = ttk.Entry(self.scrollable_frame, width=10)
            entry_b.grid(row=i + 1, column=n, padx=5, pady=2)
            entry_b.insert(0, "0")
            self.entradas_b.append(entry_b)

    def leer_datos(self):
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
                    fila.append(Fraction(texto))
                coeficientes.append(fila)

                texto_b = self.entradas_b[i].get().strip()
                if texto_b == "":
                    texto_b = "0"
                terminos.append(Fraction(texto_b))
        except Exception as e:
            messagebox.showerror("Error", f"Dato inválido: {e}\nUse fracciones como 1/2 o decimales.")
            return None, None, None, None
        return m, n, coeficientes, terminos

    def formatear_matriz(self, matriz, with_brackets=True):
        """Devuelve una cadena con la matriz formateada y alineada."""
        if not matriz:
            return "[]"

        filas_str = []
        for fila in matriz:
            filas_str.append([formatear_valor(val) for val in fila])

        cols = len(matriz[0])
        anchos = [0] * cols
        for fila in filas_str:
            for j, val in enumerate(fila):
                anchos[j] = max(anchos[j], len(val))

        lineas = []
        for fila in filas_str:
            if with_brackets:
                linea = "[ " + "  ".join(f"{val:>{anchos[j]}}" for j, val in enumerate(fila)) + " ]"
            else:
                linea = "  ".join(f"{val:>{anchos[j]}}" for j, val in enumerate(fila))
            lineas.append(linea)
        return "\n".join(lineas)

    def resolver(self):
        self.text_resultados.config(state=tk.NORMAL)
        self.text_resultados.delete(1.0, tk.END)

        datos = self.leer_datos()
        if datos[0] is None:
            self.text_resultados.config(state=tk.DISABLED)
            return

        m, n, coeficientes, terminos = datos
        metodo = self.metodo_var.get()

        try:
            matriz_aum = crear_matriz_aumentada(m, n, coeficientes, terminos)
            resultado = resolver_sistema(matriz_aum, metodo=metodo)

            self.text_resultados.insert(tk.END, f"MÉTODO: {metodo.upper()}\n")
            self.text_resultados.insert(tk.END, "=" * 80 + "\n\n")

            for i, paso in enumerate(resultado['pasos']):
                self.text_resultados.insert(tk.END, f"Paso {i + 1}: {paso['descripcion']}\n")
                self.text_resultados.insert(tk.END, self.formatear_matriz(paso['matriz']) + "\n\n")

            clasificacion = clasificar_sistema(resultado['matriz_escalonada'], resultado['rango'])
            self.text_resultados.insert(tk.END, "=" * 80 + "\n")
            self.text_resultados.insert(tk.END, f"CLASIFICACIÓN: {clasificacion['tipo']}\n")
            self.text_resultados.insert(tk.END, f"{clasificacion['descripcion']}\n")

            if clasificacion['tipo'] != 'Inconsistente':
                self.text_resultados.insert(tk.END, "\nSOLUCIÓN:\n")
                soluciones = resultado['soluciones']
                for var in range(n):
                    if var in resultado['variables_libres']:
                        self.text_resultados.insert(tk.END, f"  x{subindice(var + 1)} = t_{var + 1} (libre)\n")
                    else:
                        val = soluciones.get(var, Fraction(0, 1))
                        self.text_resultados.insert(tk.END, f"  x{subindice(var + 1)} = {formatear_valor(val)}\n")

                self.text_resultados.insert(tk.END, "\nVERIFICACIÓN (sustituyendo en el sistema original):\n")
                sols_verif = soluciones.copy()
                for v in resultado['variables_libres']:
                    sols_verif[v] = Fraction(0, 1)

                for i, fila in enumerate(coeficientes):
                    suma = Fraction(0, 1)
                    expr = ""
                    for j, coef in enumerate(fila):
                        val = sols_verif.get(j, Fraction(0, 1))
                        suma += coef * val
                        if j == 0:
                            expr += f"{formatear_valor(coef)}·x{subindice(j + 1)}"
                        else:
                            if coef >= 0:
                                expr += f" + {formatear_valor(coef)}·x{subindice(j + 1)}"
                            else:
                                expr += f" - {formatear_valor(abs(coef))}·x{subindice(j + 1)}"
                    esperado = terminos[i]
                    ok = (suma == esperado)
                    self.text_resultados.insert(tk.END, f"  Ec{i + 1}: {expr} = {formatear_valor(suma)}  (esperado {formatear_valor(esperado)}) {'[OK]' if ok else '[ERROR]'}\n")

                self.text_resultados.insert(tk.END, "\nMatriz escalonada final:\n")
                self.text_resultados.insert(tk.END, self.formatear_matriz(resultado['matriz_escalonada']) + "\n")
            else:
                self.text_resultados.insert(tk.END, "\nNo hay solución (sistema inconsistente).\n")

        except Exception as e:
            messagebox.showerror("Error", f"Error al resolver: {e}")

        self.text_resultados.config(state=tk.DISABLED)

    def limpiar(self):
        self.text_resultados.config(state=tk.NORMAL)
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.config(state=tk.DISABLED)

        for fila in self.entradas_coef:
            for entry in fila:
                entry.delete(0, tk.END)
                entry.insert(0, "0")
        for entry in self.entradas_b:
            entry.delete(0, tk.END)
            entry.insert(0, "0")

