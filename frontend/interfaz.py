"""
Interfaz gráfica moderna para la calculadora de matrices utilizando CustomTkinter.
"""

import customtkinter as ctk
from tkinter import messagebox
from fractions import Fraction

from backend.matriz import crear_matriz_aumentada, formatear_valor, subindice, _a_fraction
from backend.eliminacion import resolver_sistema
from backend.clasificador import clasificar_sistema
from backend.vectores import (
    suma_vectores,
    resta_vectores,
    multiplicar_escalar_vector,
    es_combinacion_lineal,
)
from backend.operaciones_matriciales import (
    suma_matrices,
    resta_matrices,
    multiplicar_escalar_matriz,
    multiplicar_matrices,
)

# Configuración del tema visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Límites razonables para el tamaño del sistema (evita matrices absurdas o vacías)
DIM_MINIMA = 1
DIM_MAXIMA = 12
DIM_POR_DEFECTO = 3


class InterfazCalculadora(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora de Álgebra Lineal")
        self.geometry("1100x850")
        self.minsize(950, 700)

        # Variables de control
        self.m_var = ctk.IntVar(value=DIM_POR_DEFECTO)
        self.n_var = ctk.IntVar(value=DIM_POR_DEFECTO)
        self.metodo_var = ctk.StringVar(value="Gauss-Jordan")

        self.entradas_coef = []
        self.entradas_b = []

        self.vec_n_var = ctk.IntVar(value=DIM_POR_DEFECTO)
        self.vec_k_var = ctk.IntVar(value=2)
        self.entradas_vectores = []
        self.entradas_b_vec = []

        self.mat_am_var = ctk.IntVar(value=2)
        self.mat_an_var = ctk.IntVar(value=3)
        self.mat_bm_var = ctk.IntVar(value=3)
        self.mat_bn_var = ctk.IntVar(value=2)
        self.entradas_A = []
        self.entradas_B = []

        self._configurar_grid()
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.tabs.add("Sistemas lineales")
        self.tabs.add("Vectores")
        self.tabs.add("Matrices")

        self._construir_pestana_sistemas()
        self._construir_pestana_vectores()
        self._construir_pestana_matrices()

    def _configurar_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _construir_pestana_sistemas(self):
        padre = self.tabs.tab("Sistemas lineales")
        padre.grid_columnconfigure(1, weight=1)
        padre.grid_rowconfigure(0, weight=1)
        self._crear_sidebar(padre)
        self._crear_panel_matriz(padre)
        self._crear_panel_resultados()
        self.actualizar_tabla()

    # ------------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------------
    def _crear_sidebar(self, padre):
        sidebar = ctk.CTkFrame(padre, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_rowconfigure(9, weight=1)

        # Encabezado
        lbl_titulo = ctk.CTkLabel(
            sidebar,
            text="Álgebra Lineal",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        lbl_titulo.grid(row=0, column=0, padx=20, pady=(25, 15))

        # --- Ecuaciones (m): ahora es un campo de texto editable, no un menú fijo ---
        ctk.CTkLabel(sidebar, text="Ecuaciones (m):", anchor="w").grid(
            row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.entry_m = ctk.CTkEntry(sidebar, justify="center")
        self.entry_m.insert(0, str(DIM_POR_DEFECTO))
        self.entry_m.grid(row=2, column=0, padx=20, pady=(2, 10), sticky="ew")
        self.entry_m.bind("<Return>", self._on_dimension_enter)
        self.entry_m.bind("<FocusOut>", self._on_dimension_enter)

        # --- Variables (n): mismo tratamiento ---
        ctk.CTkLabel(sidebar, text="Variables (n):", anchor="w").grid(
            row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.entry_n = ctk.CTkEntry(sidebar, justify="center")
        self.entry_n.insert(0, str(DIM_POR_DEFECTO))
        self.entry_n.grid(row=4, column=0, padx=20, pady=(2, 5), sticky="ew")
        self.entry_n.bind("<Return>", self._on_dimension_enter)
        self.entry_n.bind("<FocusOut>", self._on_dimension_enter)

        lbl_ayuda_dim = ctk.CTkLabel(
            sidebar,
            text=f"Entero entre {DIM_MINIMA} y {DIM_MAXIMA}. Presiona Enter.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            wraplength=210,
            justify="left",
        )
        lbl_ayuda_dim.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="w")

        # Algoritmo de resolución
        ctk.CTkLabel(sidebar, text="Método:", anchor="w").grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        combo_metodo = ctk.CTkOptionMenu(
            sidebar,
            variable=self.metodo_var,
            values=["Gauss-Jordan", "Gauss"]
        )
        combo_metodo.grid(row=7, column=0, padx=20, pady=(2, 25), sticky="ew")

        # Acciones
        btn_resolver = ctk.CTkButton(
            sidebar,
            text="⚡ Resolver Sistema",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.resolver
        )
        btn_resolver.grid(row=8, column=0, padx=20, pady=10, sticky="ew")

        btn_limpiar = ctk.CTkButton(
            sidebar,
            text="Limpiar Matriz",
            fg_color="transparent",
            border_width=1,
            command=self.limpiar
        )
        btn_limpiar.grid(row=9, column=0, padx=20, pady=10, sticky="n")

        lbl_tip = ctk.CTkLabel(
            sidebar,
            text="Tip: puedes pegar (Ctrl+V) una\nmatriz copiada desde Excel.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            justify="left",
        )
        lbl_tip.grid(row=10, column=0, padx=20, pady=(0, 15), sticky="sw")

    # ------------------------------------------------------------------
    # VALIDACIÓN DE DIMENSIONES
    # ------------------------------------------------------------------
    def _validar_entero(self, texto, minimo=DIM_MINIMA, maximo=DIM_MAXIMA):
        """Devuelve el entero si es válido dentro del rango, o None si no lo es."""
        texto = texto.strip()
        if not texto.lstrip("-").isdigit():
            return None
        valor = int(texto)
        if valor < minimo or valor > maximo:
            return None
        return valor

    def _on_dimension_enter(self, event=None):
        """Valida y aplica m y n cuando el usuario presiona Enter o sale del campo."""
        nuevo_m = self._validar_entero(self.entry_m.get())
        nuevo_n = self._validar_entero(self.entry_n.get())

        hubo_error = False
        if nuevo_m is None:
            hubo_error = True
            self.entry_m.delete(0, "end")
            self.entry_m.insert(0, str(self.m_var.get()))
        if nuevo_n is None:
            hubo_error = True
            self.entry_n.delete(0, "end")
            self.entry_n.insert(0, str(self.n_var.get()))

        if hubo_error:
            messagebox.showwarning(
                "Dimensión inválida",
                f"Ingresa un número entero entre {DIM_MINIMA} y {DIM_MAXIMA} "
                "para las ecuaciones y las variables."
            )
            return

        # Solo reconstruir la tabla si el valor realmente cambió
        if nuevo_m != self.m_var.get() or nuevo_n != self.n_var.get():
            self.m_var.set(nuevo_m)
            self.n_var.set(nuevo_n)
            self.actualizar_tabla()

    # ------------------------------------------------------------------
    # PANEL DE MATRIZ (entrada de datos)
    # ------------------------------------------------------------------
    def _crear_panel_matriz(self, padre):
        self.main_frame = ctk.CTkFrame(padre, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=2)

        lbl_matriz = ctk.CTkLabel(
            self.main_frame,
            text="Matriz Aumentada [ A | b ]",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_matriz.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.scroll_matriz = ctk.CTkScrollableFrame(self.main_frame)
        self.scroll_matriz.grid(row=1, column=0, sticky="nsew", pady=(0, 20))

    def _crear_panel_resultados(self):
        lbl_res = ctk.CTkLabel(
            self.main_frame,
            text="Procedimiento y Resultado",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_res.grid(row=2, column=0, sticky="w", pady=(0, 10))

        self.txt_resultados = ctk.CTkTextbox(
            self.main_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            activate_scrollbars=True
        )
        self.txt_resultados.grid(row=3, column=0, sticky="nsew")

    def actualizar_tabla(self):
        for widget in self.scroll_matriz.winfo_children():
            widget.destroy()

        self.entradas_coef = []
        self.entradas_b = []

        m = self.m_var.get()
        n = self.n_var.get()

        # Encabezados de columnas (Variables)
        for j in range(n):
            lbl = ctk.CTkLabel(
                self.scroll_matriz,
                text=f"x{subindice(j + 1)}",
                font=ctk.CTkFont(weight="bold")
            )
            lbl.grid(row=0, column=j, padx=5, pady=5)

        lbl_b = ctk.CTkLabel(
            self.scroll_matriz,
            text="│  b",
            font=ctk.CTkFont(weight="bold"),
            text_color="#3B82F6"
        )
        lbl_b.grid(row=0, column=n, padx=10, pady=5)

        # Generación de celdas (más grandes y con navegación tipo hoja de cálculo)
        for i in range(m):
            fila_entries = []
            for j in range(n):
                entry = ctk.CTkEntry(
                    self.scroll_matriz, width=64, height=32, justify="center",
                    font=ctk.CTkFont(family="Consolas", size=13),
                )
                entry.grid(row=i + 1, column=j, padx=3, pady=3)
                entry.insert(0, "0")
                self._configurar_celda(entry, i, j, es_b=False)
                fila_entries.append(entry)
            self.entradas_coef.append(fila_entries)

            entry_b = ctk.CTkEntry(
                self.scroll_matriz, width=64, height=32, justify="center",
                font=ctk.CTkFont(family="Consolas", size=13),
                fg_color="#1E293B"
            )
            entry_b.grid(row=i + 1, column=n, padx=10, pady=3)
            entry_b.insert(0, "0")
            self._configurar_celda(entry_b, i, n, es_b=True)
            self.entradas_b.append(entry_b)

    # ------------------------------------------------------------------
    # ENTRADA DE DATOS MÁS ÁGIL: navegación, autoselección y pegado
    # ------------------------------------------------------------------
    def _configurar_celda(self, entry, i, j, es_b):
        """Añade atajos de teclado a cada celda para escribir la matriz más rápido:
        - Al enfocar una celda, selecciona todo su contenido (basta con teclear para
          sobrescribir el 0 inicial, sin borrar a mano).
        - Enter mueve el foco a la misma columna en la fila siguiente (como en Excel).
        - Ctrl + flechas mueve el foco en esa dirección sin romper la edición normal
          de texto con las flechas simples.
        - Ctrl+V pega una matriz copiada de Excel/Sheets (separada por tabs y saltos
          de línea) empezando en la celda enfocada.
        """
        entry.bind("<FocusIn>", lambda e: entry.select_range(0, "end"))
        entry.bind("<Return>", lambda e: self._mover_foco(i, j, es_b, 1, 0))
        entry.bind("<Control-Up>", lambda e: self._mover_foco(i, j, es_b, -1, 0))
        entry.bind("<Control-Down>", lambda e: self._mover_foco(i, j, es_b, 1, 0))
        entry.bind("<Control-Left>", lambda e: self._mover_foco(i, j, es_b, 0, -1))
        entry.bind("<Control-Right>", lambda e: self._mover_foco(i, j, es_b, 0, 1))
        entry.bind("<Control-v>", lambda e: self._pegar_matriz(i, j))

    def _celda(self, i, j, es_b):
        n = self.n_var.get()
        if es_b or j >= n:
            return self.entradas_b[i] if 0 <= i < len(self.entradas_b) else None
        return self.entradas_coef[i][j]

    def _mover_foco(self, i, j, es_b, delta_fila, delta_col):
        """Mueve el foco a la celda vecina, si existe, respetando los límites de la tabla."""
        m = self.m_var.get()
        n = self.n_var.get()

        col_actual = n if es_b else j
        nueva_fila = i + delta_fila
        nueva_col = col_actual + delta_col

        if not (0 <= nueva_fila < m):
            return "break"
        if not (0 <= nueva_col <= n):
            return "break"

        if nueva_col == n:
            destino = self.entradas_b[nueva_fila]
        else:
            destino = self.entradas_coef[nueva_fila][nueva_col]

        destino.focus_set()
        return "break"

    def _pegar_matriz(self, i, j):
        """Pega texto del portapapeles (filas separadas por salto de línea,
        columnas por tabulador, coma o espacios) empezando en la celda (i, j)."""
        try:
            contenido = self.clipboard_get()
        except Exception:
            return "break"

        filas_pegadas = [f for f in contenido.strip("\n").split("\n") if f.strip() != ""]
        m = self.m_var.get()
        n = self.n_var.get()

        for di, fila_txt in enumerate(filas_pegadas):
            fila_destino = i + di
            if fila_destino >= m:
                break
            valores = [v.strip() for v in fila_txt.replace(",", "\t").split("\t") if v.strip() != ""]
            for dj, valor in enumerate(valores):
                col_destino = j + dj
                if col_destino > n:
                    break
                if col_destino == n:
                    self.entradas_b[fila_destino].delete(0, "end")
                    self.entradas_b[fila_destino].insert(0, valor)
                else:
                    self.entradas_coef[fila_destino][col_destino].delete(0, "end")
                    self.entradas_coef[fila_destino][col_destino].insert(0, valor)
        return "break"

    # ------------------------------------------------------------------
    # LECTURA Y RESOLUCIÓN
    # ------------------------------------------------------------------
    def leer_datos(self):
        m = self.m_var.get()
        n = self.n_var.get()
        coeficientes = []
        terminos = []
        try:
            for i in range(m):
                fila = []
                for j in range(n):
                    texto = self.entradas_coef[i][j].get().strip() or "0"
                    fila.append(Fraction(texto))
                coeficientes.append(fila)

                texto_b = self.entradas_b[i].get().strip() or "0"
                terminos.append(Fraction(texto_b))
        except Exception as e:
            messagebox.showerror(
                "Error de Formato",
                f"Entrada inválida: {e}\nUtiliza enteros, decimales o fracciones (ej. -2/3)."
            )
            return None, None, None, None
        return m, n, coeficientes, terminos

    def formatear_matriz(self, matriz):
        """Dibuja la matriz con corchetes grandes reales que abarcan todas las filas,
        en vez de repetir un corchete pequeño en cada línea."""
        if not matriz:
            return "[ ]"

        filas_str = [[formatear_valor(val) for val in fila] for fila in matriz]
        anchos = [max(len(fila[j]) for fila in filas_str) for j in range(len(matriz[0]))]
        n_filas = len(filas_str)

        lineas = []
        for idx, fila in enumerate(filas_str):
            contenido = "  ".join(f"{val:>{anchos[j]}}" for j, val in enumerate(fila))

            if n_filas == 1:
                izq, der = "[", "]"
            elif idx == 0:
                izq, der = "⎡", "⎤"
            elif idx == n_filas - 1:
                izq, der = "⎣", "⎦"
            else:
                izq, der = "⎢", "⎥"

            lineas.append(f"  {izq} {contenido} {der}")

        return "\n".join(lineas)

    def _formatear_expresion(self, constante, terminos):
        partes = []
        if constante != 0 or not terminos:
            partes.append(formatear_valor(constante))
        for variable, coeficiente in sorted(terminos.items()):
            signo = "+" if coeficiente >= 0 else "-"
            valor = abs(coeficiente)
            factor = "" if valor == 1 else f"{formatear_valor(valor)}·"
            termino = f"{factor}t{subindice(variable + 1)}"
            partes.append(f"{signo} {termino}")
        return " ".join(partes).replace("+ -", "- ")

    def _insertar_verificacion(self, coeficientes, terminos, soluciones, variables_libres):
        self.txt_resultados.insert("end", "\nVERIFICACIÓN PASO A PASO:\n")
        self.txt_resultados.insert("end", "Se asigna 0 a las variables libres para comprobar una solución.\n\n")

        valores = {}
        for variable, expresion in soluciones.items():
            valores[variable] = expresion[0]

        for i, fila in enumerate(coeficientes):
            acumulado = Fraction(0, 1)
            partes = []
            for j, coeficiente in enumerate(fila):
                valor = valores.get(j, Fraction(0, 1))
                producto = coeficiente * valor
                acumulado += producto
                partes.append(
                    f"{formatear_valor(coeficiente)}·({formatear_valor(valor)})"
                    f" = {formatear_valor(producto)}"
                )
                self.txt_resultados.insert(
                    "end",
                    f"  Ecuación {i + 1}, término x{subindice(j + 1)}: "
                    f"{partes[-1]}; acumulado = {formatear_valor(acumulado)}\n"
                )

            esperado = terminos[i]
            estado = "[OK]" if acumulado == esperado else "[ERROR]"
            self.txt_resultados.insert(
                "end",
                f"  Ecuación {i + 1}: {formatear_valor(acumulado)} = "
                f"{formatear_valor(esperado)} {estado}\n\n"
            )

    def _insertar_solucion_general(self, resultado, n):
        soluciones = resultado["soluciones_generales"]
        libres = resultado["variables_libres"]
        self.txt_resultados.insert("end", "\nSOLUCIÓN GENERAL PARAMETRIZADA:\n")

        if libres:
            nombres = ", ".join(f"t{subindice(v + 1)}" for v in libres)
            self.txt_resultados.insert("end", f"Parámetros libres: {nombres}\n")
        else:
            self.txt_resultados.insert("end", "No hay parámetros libres.\n")

        self.txt_resultados.insert("end", "\nDespeje paso a paso:\n")
        for paso, (variable, constante, terminos) in enumerate(resultado["pasos_solucion"], 1):
            expresion = self._formatear_expresion(constante, terminos)
            self.txt_resultados.insert(
                "end",
                f"  Paso {paso}: x{subindice(variable + 1)} = {expresion}\n"
            )

        self.txt_resultados.insert("end", "\nForma final:\n")
        for variable in range(n):
            constante, terminos = soluciones.get(
                variable, (Fraction(0, 1), {})
            )
            expresion = self._formatear_expresion(constante, terminos)
            self.txt_resultados.insert(
                "end",
                f"  x{subindice(variable + 1)} = {expresion}\n"
            )

    def resolver(self):
        self.txt_resultados.configure(state="normal")
        self.txt_resultados.delete("1.0", "end")

        datos = self.leer_datos()
        if datos[0] is None:
            return

        m, n, coeficientes, terminos = datos
        metodo = self.metodo_var.get()

        try:
            matriz_aum = crear_matriz_aumentada(m, n, coeficientes, terminos)
            resultado = resolver_sistema(matriz_aum, metodo=metodo)

            self.txt_resultados.insert("end", f"=== MÉTODO SELECCIONADO: {metodo.upper()} ===\n\n")

            for i, paso in enumerate(resultado['pasos']):
                self.txt_resultados.insert("end", f"Paso {i + 1}: {paso['descripcion']}\n")
                self.txt_resultados.insert("end", self.formatear_matriz(paso['matriz']) + "\n\n")

            clasificacion = clasificar_sistema(resultado['matriz_escalonada'], resultado['rango'])

            self.txt_resultados.insert("end", "═" * 60 + "\n")
            self.txt_resultados.insert("end", f"DIAGNÓSTICO: {clasificacion['tipo']}\n")
            self.txt_resultados.insert("end", f"DETALLE: {clasificacion['descripcion']}\n")
            self.txt_resultados.insert("end", "═" * 60 + "\n\n")

            if clasificacion['tipo'] != 'Inconsistente':
                self.txt_resultados.insert("end", "SOLUCIÓN DEL SISTEMA:\n")
                soluciones = resultado['soluciones']
                for var in range(n):
                    if var in resultado['variables_libres']:
                        self.txt_resultados.insert("end", f"  • x{subindice(var + 1)} = t_{var + 1} (Variable libre)\n")
                    else:
                        val = soluciones.get(var, Fraction(0, 1))
                        self.txt_resultados.insert("end", f"  • x{subindice(var + 1)} = {formatear_valor(val)}\n")

                self._insertar_solucion_general(resultado, n)
                self._insertar_verificacion(
                    coeficientes,
                    terminos,
                    resultado["soluciones_generales"],
                    resultado["variables_libres"],
                )

                self.txt_resultados.see("end")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error en el cálculo: {e}")

    def limpiar(self):
        self.txt_resultados.configure(state="normal")
        self.txt_resultados.delete("1.0", "end")
        for fila in self.entradas_coef:
            for entry in fila:
                entry.delete(0, "end")
                entry.insert(0, "0")
        for entry in self.entradas_b:
            entry.delete(0, "end")
            entry.insert(0, "0")

    # ------------------------------------------------------------------
    # PESTAÑA VECTORES
    # ------------------------------------------------------------------
    def _construir_pestana_vectores(self):
        padre = self.tabs.tab("Vectores")
        padre.grid_columnconfigure(0, weight=1)
        padre.grid_rowconfigure(2, weight=1)
        padre.grid_rowconfigure(4, weight=2)

        controles = ctk.CTkFrame(padre, fg_color="transparent")
        controles.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        ctk.CTkLabel(controles, text="Dimensión n:").grid(row=0, column=0, padx=(0, 6))
        self.entry_vec_n = ctk.CTkEntry(controles, width=70, justify="center")
        self.entry_vec_n.insert(0, str(self.vec_n_var.get()))
        self.entry_vec_n.grid(row=0, column=1, padx=(0, 16))
        self.entry_vec_n.bind("<Return>", self._on_dim_vectores)
        self.entry_vec_n.bind("<FocusOut>", self._on_dim_vectores)

        ctk.CTkLabel(controles, text="Número de vectores k:").grid(row=0, column=2, padx=(0, 6))
        self.entry_vec_k = ctk.CTkEntry(controles, width=70, justify="center")
        self.entry_vec_k.insert(0, str(self.vec_k_var.get()))
        self.entry_vec_k.grid(row=0, column=3, padx=(0, 16))
        self.entry_vec_k.bind("<Return>", self._on_dim_vectores)
        self.entry_vec_k.bind("<FocusOut>", self._on_dim_vectores)

        ctk.CTkLabel(controles, text="Escalar k:").grid(row=0, column=4, padx=(0, 6))
        self.entry_vec_escalar = ctk.CTkEntry(controles, width=80, justify="center")
        self.entry_vec_escalar.insert(0, "2")
        self.entry_vec_escalar.grid(row=0, column=5, padx=(0, 16))

        ctk.CTkLabel(
            padre,
            text="Escribe k vectores de Rⁿ (columnas) y el vector b. Suma/resta usan v₁ y v₂.",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 6))

        self.scroll_vectores = ctk.CTkScrollableFrame(padre, height=180)
        self.scroll_vectores.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        botones = ctk.CTkFrame(padre, fg_color="transparent")
        botones.grid(row=3, column=0, sticky="ew", padx=10, pady=8)
        ctk.CTkButton(botones, text="Suma v₁+v₂", command=self._op_suma_vectores).grid(
            row=0, column=0, padx=4, pady=4
        )
        ctk.CTkButton(botones, text="Resta v₁−v₂", command=self._op_resta_vectores).grid(
            row=0, column=1, padx=4, pady=4
        )
        ctk.CTkButton(botones, text="Escalar · v₁", command=self._op_escalar_vector).grid(
            row=0, column=2, padx=4, pady=4
        )
        ctk.CTkButton(
            botones,
            text="¿b es combinación lineal?",
            command=self._op_combinacion_lineal,
        ).grid(row=0, column=3, padx=4, pady=4)

        ctk.CTkLabel(
            padre,
            text="Resultado",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=4, column=0, sticky="nw", padx=10)
        self.txt_vectores = ctk.CTkTextbox(
            padre,
            font=ctk.CTkFont(family="Consolas", size=13),
            activate_scrollbars=True,
        )
        self.txt_vectores.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 10))
        padre.grid_rowconfigure(5, weight=2)

        self._actualizar_tabla_vectores()

    def _on_dim_vectores(self, event=None):
        nuevo_n = self._validar_entero(self.entry_vec_n.get())
        nuevo_k = self._validar_entero(self.entry_vec_k.get())
        if nuevo_n is None or nuevo_k is None:
            self.entry_vec_n.delete(0, "end")
            self.entry_vec_n.insert(0, str(self.vec_n_var.get()))
            self.entry_vec_k.delete(0, "end")
            self.entry_vec_k.insert(0, str(self.vec_k_var.get()))
            messagebox.showwarning(
                "Dimensión inválida",
                f"n y k deben ser enteros entre {DIM_MINIMA} y {DIM_MAXIMA}.",
            )
            return
        if nuevo_n != self.vec_n_var.get() or nuevo_k != self.vec_k_var.get():
            self.vec_n_var.set(nuevo_n)
            self.vec_k_var.set(nuevo_k)
            self._actualizar_tabla_vectores()

    def _actualizar_tabla_vectores(self):
        for widget in self.scroll_vectores.winfo_children():
            widget.destroy()

        n = self.vec_n_var.get()
        k = self.vec_k_var.get()
        self.entradas_vectores = [[] for _ in range(k)]
        self.entradas_b_vec = []

        for j in range(k):
            ctk.CTkLabel(
                self.scroll_vectores,
                text=f"v{subindice(j + 1)}",
                font=ctk.CTkFont(weight="bold"),
            ).grid(row=0, column=j, padx=5, pady=5)

        ctk.CTkLabel(
            self.scroll_vectores,
            text="│  b",
            font=ctk.CTkFont(weight="bold"),
            text_color="#3B82F6",
        ).grid(row=0, column=k, padx=10, pady=5)

        for i in range(n):
            for j in range(k):
                entry = ctk.CTkEntry(
                    self.scroll_vectores,
                    width=64,
                    height=32,
                    justify="center",
                    font=ctk.CTkFont(family="Consolas", size=13),
                )
                entry.grid(row=i + 1, column=j, padx=3, pady=3)
                entry.insert(0, "0")
                entry.bind("<FocusIn>", lambda e, ent=entry: ent.select_range(0, "end"))
                self.entradas_vectores[j].append(entry)

            entry_b = ctk.CTkEntry(
                self.scroll_vectores,
                width=64,
                height=32,
                justify="center",
                font=ctk.CTkFont(family="Consolas", size=13),
                fg_color="#1E293B",
            )
            entry_b.grid(row=i + 1, column=k, padx=10, pady=3)
            entry_b.insert(0, "0")
            entry_b.bind("<FocusIn>", lambda e, ent=entry_b: ent.select_range(0, "end"))
            self.entradas_b_vec.append(entry_b)

    def _leer_escalar(self, entry):
        texto = entry.get().strip() or "0"
        return _a_fraction(texto)

    def _leer_vectores_tab(self):
        n = self.vec_n_var.get()
        k = self.vec_k_var.get()
        vectores = []
        for j in range(k):
            vector = []
            for i in range(n):
                texto = self.entradas_vectores[j][i].get().strip() or "0"
                vector.append(_a_fraction(texto))
            vectores.append(vector)
        b = []
        for i in range(n):
            texto = self.entradas_b_vec[i].get().strip() or "0"
            b.append(_a_fraction(texto))
        return vectores, b

    def _formatear_vector(self, vector):
        interiores = ", ".join(formatear_valor(v) for v in vector)
        return f"({interiores})"

    def _mostrar_en(self, textbox, texto):
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("end", texto)

    def _formatear_matriz_corchetes(self, matriz):
        """Muestra una matriz con corchetes [ ] alineados por columnas."""
        if not matriz:
            return "[ ]"
        filas_str = [[formatear_valor(val) for val in fila] for fila in matriz]
        anchos = [max(len(fila[j]) for fila in filas_str) for j in range(len(matriz[0]))]
        lineas = []
        for fila in filas_str:
            contenido = "   ".join(f"{val:>{anchos[j]}}" for j, val in enumerate(fila))
            lineas.append(f"[ {contenido} ]")
        return "\n".join(lineas)

    def _op_suma_vectores(self):
        try:
            vectores, _b = self._leer_vectores_tab()
            if len(vectores) < 2:
                raise ValueError("Se necesitan al menos dos vectores (k ≥ 2) para v₁ + v₂.")
            resultado = suma_vectores(vectores[0], vectores[1])
            self._mostrar_en(
                self.txt_vectores,
                "SUMA DE VECTORES  v₁ + v₂\n"
                "Algebraicamente: (u + v)_i = u_i + v_i\n\n"
                f"v₁ = {self._formatear_vector(vectores[0])}\n"
                f"v₂ = {self._formatear_vector(vectores[1])}\n"
                f"v₁ + v₂ = {self._formatear_vector(resultado)}\n",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _op_resta_vectores(self):
        try:
            vectores, _b = self._leer_vectores_tab()
            if len(vectores) < 2:
                raise ValueError("Se necesitan al menos dos vectores (k ≥ 2) para v₁ − v₂.")
            resultado = resta_vectores(vectores[0], vectores[1])
            self._mostrar_en(
                self.txt_vectores,
                "RESTA DE VECTORES  v₁ − v₂\n"
                "Algebraicamente: (u − v)_i = u_i − v_i\n\n"
                f"v₁ = {self._formatear_vector(vectores[0])}\n"
                f"v₂ = {self._formatear_vector(vectores[1])}\n"
                f"v₁ − v₂ = {self._formatear_vector(resultado)}\n",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _op_escalar_vector(self):
        try:
            vectores, _b = self._leer_vectores_tab()
            escalar = self._leer_escalar(self.entry_vec_escalar)
            resultado = multiplicar_escalar_vector(escalar, vectores[0])
            self._mostrar_en(
                self.txt_vectores,
                "MULTIPLICACIÓN POR ESCALAR  k · v₁\n"
                "Algebraicamente: (k·v)_i = k · v_i\n\n"
                f"k = {formatear_valor(escalar)}\n"
                f"v₁ = {self._formatear_vector(vectores[0])}\n"
                f"k · v₁ = {self._formatear_vector(resultado)}\n",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _op_combinacion_lineal(self):
        try:
            vectores, b = self._leer_vectores_tab()
            matriz_aum = es_combinacion_lineal(b, vectores)
            resultado = resolver_sistema(matriz_aum, metodo="Gauss-Jordan")
            clasificacion = clasificar_sistema(
                resultado["matriz_escalonada"], resultado["rango"]
            )

            lineas = [
                "¿b ES COMBINACIÓN LINEAL DE {v₁, ..., vₖ}?",
                "Se resuelve A·c = b, donde las columnas de A son los vectores dados.",
                "",
                "Matriz aumentada [A | b]:",
                self._formatear_matriz_corchetes(matriz_aum),
                "",
            ]

            if clasificacion["tipo"] == "Inconsistente":
                lineas.append("b NO es combinación lineal")
                lineas.append(clasificacion["descripcion"])
            else:
                lineas.append("b SÍ es combinación lineal")
                lineas.append(clasificacion["descripcion"])
                lineas.append("")
                lineas.append("Coeficientes:")
                k = len(vectores)
                soluciones = resultado["soluciones"]
                libres = set(resultado["variables_libres"])
                for j in range(k):
                    if j in libres:
                        lineas.append(f"  c{subindice(j + 1)} = t{subindice(j + 1)}  (libre)")
                    else:
                        val = soluciones.get(j, Fraction(0, 1))
                        lineas.append(f"  c{subindice(j + 1)} = {formatear_valor(val)}")

                if resultado.get("soluciones_generales"):
                    lineas.append("")
                    lineas.append("Solución general (si hay parámetros):")
                    for j in range(k):
                        constante, terminos = resultado["soluciones_generales"].get(
                            j, (Fraction(0, 1), {})
                        )
                        expresion = self._formatear_expresion(constante, terminos)
                        lineas.append(f"  c{subindice(j + 1)} = {expresion}")

            self._mostrar_en(self.txt_vectores, "\n".join(lineas) + "\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------
    # PESTAÑA MATRICES
    # ------------------------------------------------------------------
    def _construir_pestana_matrices(self):
        padre = self.tabs.tab("Matrices")
        padre.grid_columnconfigure(0, weight=1)
        padre.grid_columnconfigure(1, weight=1)
        padre.grid_rowconfigure(2, weight=1)
        padre.grid_rowconfigure(5, weight=2)

        controles = ctk.CTkFrame(padre, fg_color="transparent")
        controles.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        ctk.CTkLabel(controles, text="A (m×n):").grid(row=0, column=0, padx=(0, 4))
        self.entry_am = ctk.CTkEntry(controles, width=50, justify="center")
        self.entry_am.insert(0, str(self.mat_am_var.get()))
        self.entry_am.grid(row=0, column=1)
        ctk.CTkLabel(controles, text="×").grid(row=0, column=2, padx=4)
        self.entry_an = ctk.CTkEntry(controles, width=50, justify="center")
        self.entry_an.insert(0, str(self.mat_an_var.get()))
        self.entry_an.grid(row=0, column=3, padx=(0, 16))

        ctk.CTkLabel(controles, text="B (filas×cols):").grid(row=0, column=4, padx=(0, 4))
        self.entry_bm = ctk.CTkEntry(controles, width=50, justify="center")
        self.entry_bm.insert(0, str(self.mat_bm_var.get()))
        self.entry_bm.grid(row=0, column=5)
        ctk.CTkLabel(controles, text="×").grid(row=0, column=6, padx=4)
        self.entry_bn = ctk.CTkEntry(controles, width=50, justify="center")
        self.entry_bn.insert(0, str(self.mat_bn_var.get()))
        self.entry_bn.grid(row=0, column=7, padx=(0, 16))

        ctk.CTkLabel(controles, text="Escalar k:").grid(row=0, column=8, padx=(0, 4))
        self.entry_mat_escalar = ctk.CTkEntry(controles, width=70, justify="center")
        self.entry_mat_escalar.insert(0, "2")
        self.entry_mat_escalar.grid(row=0, column=9)

        for entry in (self.entry_am, self.entry_an, self.entry_bm, self.entry_bn):
            entry.bind("<Return>", self._on_dim_matrices)
            entry.bind("<FocusOut>", self._on_dim_matrices)

        ctk.CTkLabel(
            padre,
            text="A+B y A−B requieren el mismo tamaño. A·B requiere columnas(A) = filas(B). "
            "La ecuación Ax = b se resuelve en la pestaña Sistemas lineales.",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
            wraplength=900,
            justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 6))

        self.scroll_A = ctk.CTkScrollableFrame(padre, height=200)
        self.scroll_A.grid(row=2, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.scroll_B = ctk.CTkScrollableFrame(padre, height=200)
        self.scroll_B.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=5)

        botones = ctk.CTkFrame(padre, fg_color="transparent")
        botones.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=8)
        ctk.CTkButton(botones, text="A+B", command=self._op_suma_matrices).grid(
            row=0, column=0, padx=4, pady=4
        )
        ctk.CTkButton(botones, text="A−B", command=self._op_resta_matrices).grid(
            row=0, column=1, padx=4, pady=4
        )
        ctk.CTkButton(botones, text="k·A", command=self._op_escalar_matriz).grid(
            row=0, column=2, padx=4, pady=4
        )
        ctk.CTkButton(botones, text="A·B", command=self._op_multiplicar_matrices).grid(
            row=0, column=3, padx=4, pady=4
        )

        ctk.CTkLabel(
            padre,
            text="Resultado",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=10)
        self.txt_matrices = ctk.CTkTextbox(
            padre,
            font=ctk.CTkFont(family="Consolas", size=13),
            activate_scrollbars=True,
        )
        self.txt_matrices.grid(
            row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10)
        )

        self._actualizar_tablas_matrices()

    def _on_dim_matrices(self, event=None):
        am = self._validar_entero(self.entry_am.get())
        an = self._validar_entero(self.entry_an.get())
        bm = self._validar_entero(self.entry_bm.get())
        bn = self._validar_entero(self.entry_bn.get())
        if None in (am, an, bm, bn):
            self.entry_am.delete(0, "end")
            self.entry_am.insert(0, str(self.mat_am_var.get()))
            self.entry_an.delete(0, "end")
            self.entry_an.insert(0, str(self.mat_an_var.get()))
            self.entry_bm.delete(0, "end")
            self.entry_bm.insert(0, str(self.mat_bm_var.get()))
            self.entry_bn.delete(0, "end")
            self.entry_bn.insert(0, str(self.mat_bn_var.get()))
            messagebox.showwarning(
                "Dimensión inválida",
                f"Las dimensiones deben ser enteros entre {DIM_MINIMA} y {DIM_MAXIMA}.",
            )
            return
        if (
            am != self.mat_am_var.get()
            or an != self.mat_an_var.get()
            or bm != self.mat_bm_var.get()
            or bn != self.mat_bn_var.get()
        ):
            self.mat_am_var.set(am)
            self.mat_an_var.set(an)
            self.mat_bm_var.set(bm)
            self.mat_bn_var.set(bn)
            self._actualizar_tablas_matrices()

    def _construir_tabla_matriz(self, scroll, filas, columnas, titulo):
        for widget in scroll.winfo_children():
            widget.destroy()
        ctk.CTkLabel(
            scroll,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=max(columnas, 1), sticky="w", padx=4, pady=(0, 6))
        entradas = []
        for i in range(filas):
            fila_entries = []
            for j in range(columnas):
                entry = ctk.CTkEntry(
                    scroll,
                    width=64,
                    height=32,
                    justify="center",
                    font=ctk.CTkFont(family="Consolas", size=13),
                )
                entry.grid(row=i + 1, column=j, padx=3, pady=3)
                entry.insert(0, "0")
                entry.bind("<FocusIn>", lambda e, ent=entry: ent.select_range(0, "end"))
                fila_entries.append(entry)
            entradas.append(fila_entries)
        return entradas

    def _actualizar_tablas_matrices(self):
        self.entradas_A = self._construir_tabla_matriz(
            self.scroll_A,
            self.mat_am_var.get(),
            self.mat_an_var.get(),
            f"Matriz A  ({self.mat_am_var.get()}×{self.mat_an_var.get()})",
        )
        self.entradas_B = self._construir_tabla_matriz(
            self.scroll_B,
            self.mat_bm_var.get(),
            self.mat_bn_var.get(),
            f"Matriz B  ({self.mat_bm_var.get()}×{self.mat_bn_var.get()})",
        )

    def _leer_matriz_entries(self, entradas):
        matriz = []
        for fila in entradas:
            fila_vals = []
            for entry in fila:
                texto = entry.get().strip() or "0"
                fila_vals.append(_a_fraction(texto))
            matriz.append(fila_vals)
        return matriz

    def _op_suma_matrices(self):
        try:
            A = self._leer_matriz_entries(self.entradas_A)
            B = self._leer_matriz_entries(self.entradas_B)
            resultado = suma_matrices(A, B)
            self._mostrar_en(
                self.txt_matrices,
                "SUMA DE MATRICES  A + B\n"
                "Algebraicamente: (A + B)[i][j] = A[i][j] + B[i][j]\n\n"
                "A =\n"
                f"{self._formatear_matriz_corchetes(A)}\n\n"
                "B =\n"
                f"{self._formatear_matriz_corchetes(B)}\n\n"
                "A + B =\n"
                f"{self._formatear_matriz_corchetes(resultado)}\n",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _op_resta_matrices(self):
        try:
            A = self._leer_matriz_entries(self.entradas_A)
            B = self._leer_matriz_entries(self.entradas_B)
            resultado = resta_matrices(A, B)
            self._mostrar_en(
                self.txt_matrices,
                "RESTA DE MATRICES  A − B\n"
                "Algebraicamente: (A − B)[i][j] = A[i][j] − B[i][j]\n\n"
                "A =\n"
                f"{self._formatear_matriz_corchetes(A)}\n\n"
                "B =\n"
                f"{self._formatear_matriz_corchetes(B)}\n\n"
                "A − B =\n"
                f"{self._formatear_matriz_corchetes(resultado)}\n",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _op_escalar_matriz(self):
        try:
            A = self._leer_matriz_entries(self.entradas_A)
            escalar = self._leer_escalar(self.entry_mat_escalar)
            resultado = multiplicar_escalar_matriz(escalar, A)
            self._mostrar_en(
                self.txt_matrices,
                "MULTIPLICACIÓN POR ESCALAR  k · A\n"
                "Algebraicamente: (k·A)[i][j] = k · A[i][j]\n\n"
                f"k = {formatear_valor(escalar)}\n\n"
                "A =\n"
                f"{self._formatear_matriz_corchetes(A)}\n\n"
                "k · A =\n"
                f"{self._formatear_matriz_corchetes(resultado)}\n",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _op_multiplicar_matrices(self):
        try:
            A = self._leer_matriz_entries(self.entradas_A)
            B = self._leer_matriz_entries(self.entradas_B)
            resultado = multiplicar_matrices(A, B)
            self._mostrar_en(
                self.txt_matrices,
                "PRODUCTO DE MATRICES  A · B\n"
                "Algebraicamente: C[i][j] = Σ_k A[i][k] · B[k][j]\n\n"
                "A =\n"
                f"{self._formatear_matriz_corchetes(A)}\n\n"
                "B =\n"
                f"{self._formatear_matriz_corchetes(B)}\n\n"
                "A · B =\n"
                f"{self._formatear_matriz_corchetes(resultado)}\n",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))