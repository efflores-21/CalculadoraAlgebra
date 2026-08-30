import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
import tkinter.messagebox as messagebox
from fractions import Fraction

from backend.matriz import MatrizAumentada, formatear_valor
from backend.eliminacion import EliminacionGaussiana
from backend.clasificador import Clasificador


class InterfazCalculadora:
    """Interfaz gráfica con Tkinter para la calculadora de sistemas lineales."""

    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Álgebra Lineal - Eliminación Gaussiana")
        self.root.geometry("1100x820")
        self.root.resizable(True, True)
        self.root.configure(bg="#edf3ff")

        self._aplicar_estilo()

        # Variables de control
        self.m = tk.IntVar(value=2)
        self.n = tk.IntVar(value=2)
        self.matriz_entries = []  # lista de listas de Entry

        self._crear_widgets()

    def _aplicar_estilo(self):
        """Configura un tema visual limpio para la interfaz."""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#edf3ff")
        style.configure("TLabelframe", background="#edf3ff", foreground="#173a5e")
        style.configure("TLabelframe.Label", background="#edf3ff", foreground="#173a5e", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.map("TButton", background=[("active", "#dfeeff")], foreground=[("active", "#0f172a")])
        style.configure("TEntry", fieldbackground="#ffffff", foreground="#0f172a")
        style.configure("TLabel", background="#edf3ff", foreground="#1f2937")

    def _crear_widgets(self):
        """Crea todos los elementos de la interfaz."""
        main_frame = ttk.Frame(self.root, padding="16")
        main_frame.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(main_frame, text="Calculadora de Álgebra Lineal", font=("Segoe UI", 18, "bold"), foreground="#173a5e")
        titulo.pack(anchor=tk.W, pady=(0, 10))

        subtitulo = ttk.Label(main_frame, text="Solución de sistemas lineales por eliminación por filas", foreground="#44576a")
        subtitulo.pack(anchor=tk.W, pady=(0, 12))

        # --- Frame: Dimensiones ---
        dim_frame = ttk.LabelFrame(main_frame, text="Dimensiones del sistema", padding="10")
        dim_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dim_frame, text="Número de ecuaciones (m):", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        ttk.Entry(dim_frame, textvariable=self.m, width=6, font=("Segoe UI", 10)).grid(row=0, column=1, padx=5, pady=8, sticky=tk.W)
        ttk.Label(dim_frame, text="Número de variables (n):", font=("Segoe UI", 10)).grid(row=0, column=2, padx=15, pady=8, sticky=tk.W)
        ttk.Entry(dim_frame, textvariable=self.n, width=6, font=("Segoe UI", 10)).grid(row=0, column=3, padx=5, pady=8, sticky=tk.W)
        ttk.Button(dim_frame, text="Generar tabla", command=self._generar_tabla, style="Accent.TButton").grid(row=0, column=4, padx=15, pady=8)

        # --- Frame: Matriz aumentada ---
        self.tabla_frame = ttk.LabelFrame(main_frame, text="Matriz aumentada [A | b]", padding="10")
        self.tabla_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Canvas con scroll para la tabla
        self.tabla_canvas = tk.Canvas(self.tabla_frame, bg="#ffffff", highlightthickness=1, highlightbackground="#d8e5f5")
        self.tabla_scroll_y = ttk.Scrollbar(self.tabla_frame, orient="vertical", command=self.tabla_canvas.yview)
        self.tabla_scroll_x = ttk.Scrollbar(self.tabla_frame, orient="horizontal", command=self.tabla_canvas.xview)
        self.tabla_canvas.configure(yscrollcommand=self.tabla_scroll_y.set, xscrollcommand=self.tabla_scroll_x.set)

        self.tabla_interior = ttk.Frame(self.tabla_canvas)
        self.tabla_canvas.create_window((0, 0), window=self.tabla_interior, anchor="nw")

        self.tabla_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tabla_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tabla_interior.bind("<Configure>",
                                 lambda e: self.tabla_canvas.configure(scrollregion=self.tabla_canvas.bbox("all")))

        # --- Botones ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Resolver sistema", command=self._resolver).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._limpiar).pack(side=tk.LEFT, padx=5)

        # --- Frame: Resultados ---
        result_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=14, wrap=tk.WORD, font=("Consolas", 10), bg="#ffffff", fg="#0f172a")
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Inicializar tabla vacía
        self._generar_tabla()

    def _generar_tabla(self):
        """Crea la tabla de entradas según m y n."""
        for widget in self.tabla_interior.winfo_children():
            widget.destroy()
        self.matriz_entries = []

        m = self.m.get()
        n = self.n.get()
        if m <= 0 or n <= 0:
            messagebox.showwarning("Dimensiones inválidas", "Ingrese valores positivos para m y n.")
            return

        # Encabezados
        for j in range(n):
            ttk.Label(self.tabla_interior, text=f"x{j+1}", font=('Segoe UI', 10, 'bold'), foreground="#173a5e").grid(row=0, column=j, padx=4, pady=6, sticky=tk.EW)
        ttk.Label(self.tabla_interior, text="|", font=('Segoe UI', 10, 'bold'), foreground="#173a5e").grid(row=0, column=n, padx=8, pady=6)
        ttk.Label(self.tabla_interior, text="b", font=('Segoe UI', 10, 'bold'), foreground="#173a5e").grid(row=0, column=n+1, padx=4, pady=6, sticky=tk.EW)

        # Entradas
        for i in range(m):
            fila_entries = []
            for j in range(n+1):
                entry = ttk.Entry(self.tabla_interior, width=10, justify=tk.CENTER)
                entry.grid(row=i+1, column=j, padx=4, pady=4)
                fila_entries.append(entry)
            self.matriz_entries.append(fila_entries)

        for j in range(n+2):
            self.tabla_interior.columnconfigure(j, weight=1, uniform="col")

    def _leer_matriz(self):
        """Lee los valores de la tabla y retorna una MatrizAumentada."""
        m = self.m.get()
        n = self.n.get()
        datos = []
        try:
            for i in range(m):
                fila = []
                for j in range(n+1):
                    val = self.matriz_entries[i][j].get().strip()
                    if val == "":
                        raise ValueError(f"Celda vacía en fila {i+1}, columna {j+1}")
                    valor = val.replace(',', '.')
                    fila.append(Fraction(valor))
                datos.append(fila)
        except (ValueError, ZeroDivisionError) as e:
            messagebox.showerror("Error de entrada", f"Revise los datos ingresados.\n{e}")
            return None
        return MatrizAumentada(datos)

    def _resolver(self):
        """Ejecuta la eliminación y muestra resultados."""
        mat_original = self._leer_matriz()
        if mat_original is None:
            return

        resultado = ""

        # Mostrar matriz original
        resultado += "=== Matriz aumentada original ===\n"
        resultado += mat_original.mostrar() + "\n\n"

        # Crear eliminador y escalonar
        eliminador = EliminacionGaussiana(mat_original)
        try:
            mat_escalonada = eliminador.escalonar(mostrar_pasos=False)
        except Exception as e:
            messagebox.showerror("Error en eliminación", f"Ocurrió un error: {e}")
            return

        resultado += "=== Matriz escalonada ===\n"
        resultado += mat_escalonada.mostrar() + "\n\n"

        # Clasificar
        clasif = Clasificador(mat_escalonada)
        tipo, sol, libres = clasif.clasificar()

        if tipo == 'inconsistente':
            resultado += "Clasificación: **Sistema Inconsistente** (Sin solución)\n"
            resultado += "Se detectó una fila del tipo [0 ... 0 | k] con k ≠ 0.\n"
        elif tipo == 'determinado':
            resultado += "Clasificación: **Sistema Consistente Determinado** (Solución única)\n"
            resultado += "Solución:\n"
            for i, val in enumerate(sol):
                valor_texto = formatear_valor(val)
                valor_lineas = valor_texto.split("\n")
                resultado += f"  x{i+1} = {valor_lineas[0]}\n"
                for linea in valor_lineas[1:]:
                    resultado += f"          {linea}\n"
            errores = Clasificador.verificar_solucion(mat_original, sol)
            if errores is not None:
                resultado += "\nVerificación (error absoluto por ecuación):\n"
                for i, err in enumerate(errores):
                    valor_texto = formatear_valor(err)
                    valor_lineas = valor_texto.split("\n")
                    resultado += f"  Ec {i+1}: {valor_lineas[0]}\n"
                    for linea in valor_lineas[1:]:
                        resultado += f"          {linea}\n"
        else:  # indeterminado
            resultado += "Clasificación: **Sistema Consistente Indeterminado** (Infinitas soluciones)\n"
            resultado += "Variables libres (índices): " + ", ".join(f"x{idx+1}" for idx in libres) + "\n"
            resultado += "\n(Solución paramétrica no calculada automáticamente)\n"

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, resultado)

    def _limpiar(self):
        """Limpia el área de resultados y las entradas de la tabla."""
        self.result_text.delete(1.0, tk.END)
        for fila in self.matriz_entries:
            for entry in fila:
                entry.delete(0, tk.END)
