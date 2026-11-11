"""Pantalla integrada de bisección, gráficas, notación posicional y errores numéricos."""

import re
import tkinter as tk

import customtkinter as ctk

from backend.biseccion import resolver_biseccion
from backend.errores_numericos import (
    analizar_punto_flotante,
    calcular_errores,
    propagar_error,
    resumen_tipos_error,
)
from backend.graficador import muestrear_funcion
from backend.notacion_posicional import binario_a_decimal, decimal_a_binario, descomponer_decimal
from modulos._comun import (
    COLOR,
    boton_primario,
    boton_secundario,
    boton_texto,
    etiqueta,
    reemplazar_texto,
    mostrar_teoremas,
)


def _leer_entero(texto, nombre):
    """Convierte un campo a entero con un mensaje en español (int() da uno técnico en inglés)."""
    texto = texto.strip()
    if not re.fullmatch(r"[+-]?\d+", texto):
        raise ValueError(f"{nombre} debe ser un número entero, sin decimales ni letras.")
    if len(texto.lstrip("+-")) > 30:
        raise ValueError(f"{nombre} puede tener como máximo 30 cifras.")
    return int(texto)


def _leer_real(texto, nombre):
    """Convierte un campo a número real con un mensaje en español."""
    try:
        return float(texto)
    except ValueError as error:
        raise ValueError(f"{nombre} debe ser un número real.") from error


def _fila_tabla(valores):
    """Alinea una fila de la tabla de bisección en columnas de ancho fijo."""
    k, *resto = valores
    return f"{str(k):>3} " + "".join(f"{str(valor):>13}" for valor in resto)


class ModuloMetodosNumericos(ctk.CTkFrame):
    """Agrupa las cuatro actividades de la Tarea 7 en pestañas de una misma pantalla."""

    def __init__(self, master, on_back):
        """Construye las pestañas e inicializa el estado compartido de bisección/gráfica."""
        super().__init__(master, fg_color=COLOR["fondo"])
        self.on_back = on_back
        self.ultimo_resultado = None
        self.ultima_muestra = None
        self._construir_interfaz()

    def _construir_interfaz(self):
        """Crea barra superior, pestañas y formularios de cada funcionalidad."""
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=28, pady=(14, 4))
        boton_secundario(barra, "←  Menú principal", self.on_back, width=160).pack(side="left")
        ctk.CTkLabel(barra, text="MÉTODOS NUMÉRICOS", font=ctk.CTkFont(size=27, weight="bold"),
                     text_color=COLOR["texto"]).pack(side="left", padx=20)
        boton_secundario(
            barra, "0. Teoremas clave",
            lambda: mostrar_teoremas(self, "metodos_numericos", "Métodos numéricos"),
        ).pack(side="right")
        boton_texto(barra, "? Cómo usar", self.mostrar_guia, width=110).pack(side="right", padx=8)
        etiqueta(self, "Bisección · Graficador · Notación posicional · Errores numéricos", tamano=14).pack(
            anchor="w", padx=34, pady=(0, 8))
        self.pestanas = ctk.CTkTabview(self, fg_color=COLOR["tarjeta"])
        self.pestanas.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        for nombre in ("Bisección", "Graficador", "Notación posicional", "Errores numéricos"):
            self.pestanas.add(nombre)
        self._crear_biseccion(self.pestanas.tab("Bisección"))
        self._crear_graficador(self.pestanas.tab("Graficador"))
        self._crear_notacion(self.pestanas.tab("Notación posicional"))
        self._crear_errores(self.pestanas.tab("Errores numéricos"))

    @staticmethod
    def _entrada(parent, titulo, inicial, ancho=150):
        """Crea una etiqueta y un campo de texto sencillo."""
        grupo = ctk.CTkFrame(parent, fg_color="transparent")
        grupo.pack(side="left", padx=(0, 12), pady=6)
        etiqueta(grupo, titulo, tamano=12, color="texto").pack(anchor="w")
        campo = ctk.CTkEntry(grupo, width=ancho)
        campo.insert(0, str(inicial))
        campo.pack(anchor="w", pady=(3, 0))
        return campo

    @staticmethod
    def _caja_texto(parent, alto=14):
        """Añade una caja monoespaciada desplazable para resultados y tablas."""
        caja = ctk.CTkTextbox(parent, height=alto * 20, wrap="none", font=ctk.CTkFont(family="Consolas", size=12))
        caja.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        return caja

    def _crear_biseccion(self, parent):
        marco = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True)
        etiqueta(marco, "El cambio de signo permite aplicar Bolzano solo si f es continua en todo [a,b].", tamano=13).pack(anchor="w", padx=12, pady=(10, 4))
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(anchor="w", padx=12)
        self.b_expr = self._entrada(fila, "f(x)", "x**3 - 2*x - 5", 240)
        self.b_a = self._entrada(fila, "a", "2", 85)
        self.b_b = self._entrada(fila, "b", "3", 85)
        self.b_tol = self._entrada(fila, "Tolerancia absoluta", "0.0001", 130)
        self.b_max = self._entrada(fila, "Máximo iteraciones", "100", 125)
        acciones = ctk.CTkFrame(marco, fg_color="transparent")
        acciones.pack(anchor="w", padx=12, pady=5)
        boton_primario(acciones, "Resolver por bisección", self.calcular_biseccion, width=205).pack(side="left", padx=(0, 8))
        boton_secundario(acciones, "Graficar este intervalo", self.graficar_intervalo_biseccion, width=195).pack(side="left")
        self.b_resultado = self._caja_texto(marco, 28)

    def calcular_biseccion(self):
        """Calcula la raíz y explica resumen, cota y trazabilidad de cada intervalo."""
        try:
            maximo = _leer_entero(self.b_max.get(), "El máximo de iteraciones")
            datos = resolver_biseccion(self.b_expr.get(), self.b_a.get(), self.b_b.get(), self.b_tol.get(), maximo)
        except (ValueError, OverflowError) as error:
            self._mostrar_error(error)
            return
        self.ultimo_resultado = {
            "expresion": self.b_expr.get().strip(),
            "a": float(self.b_a.get()), "b": float(self.b_b.get()), **datos,
        }
        relativo = datos["tabla"][-1].get("error_relativo_aprox") if datos["tabla"] else None
        lineas = [
            "BISECCIÓN — MÉTODO ITERATIVO",
            f"f(x) = {self.b_expr.get().strip()}   en   [{self.b_a.get().strip()}, {self.b_b.get().strip()}]",
            f"Idea clave: {datos['advertencia']}",
            "RESULTADO",
            f"Raíz aproximada:   xr = {datos['raiz']:.12g}",
            f"f(xr) = {datos['f_raiz']:.6g}",
            f"Iteraciones: {datos['iteraciones']}   (teóricas: {datos['iteraciones_teoricas']})",
            f"Intervalo final: [{datos['intervalo_final'][0]:.12g}, {datos['intervalo_final'][1]:.12g}]",
            f"Cota del error Eb = {datos['cota_error']:.6g}",
            f"Diferencia entre las dos últimas aproximaciones Ea = {self._formato(datos['error_absoluto_aprox'])}",
            f"Error relativo aproximado εa = {self._formato(relativo)}",
            "Significa: εa compara dos aproximaciones seguidas, no la raíz verdadera.",
            f"Terminación: {datos['motivo']}",
            "TABLA DE ITERACIONES",
            "Significa: Eb = (b − a)/2 es la cota del error;  Ea = |xr − xr anterior|;  εa = Ea/|xr|.",
            "",
            _fila_tabla(("k", "a", "b", "f(a)", "f(b)", "xr", "f(xr)", "Eb", "Ea", "εa")),
            "─" * (4 + 13 * 9),
        ]
        for paso in datos["tabla"]:
            lineas.append(_fila_tabla((
                paso["k"], f"{paso['a']:.8g}", f"{paso['b']:.8g}", f"{paso['fa']:.5g}", f"{paso['fb']:.5g}",
                f"{paso['xr']:.10g}", f"{paso['fr']:.5g}", f"{paso['cota_error']:.4g}",
                self._formato(paso["error_absoluto_aprox"]), self._formato(paso["error_relativo_aprox"]),
            )))
            nuevo_a, nuevo_b = paso["intervalo_siguiente"]
            lineas.extend([f"     → {paso['decision']}  Nuevo intervalo: [{nuevo_a:.8g}, {nuevo_b:.8g}]", ""])
        lineas.extend(["", "Nota: la comparación con SciPy se omite por las reglas del proyecto; "
                           "la tabla, los signos y la cota permiten comprobar el cálculo."])
        self._poner(self.b_resultado, "\n".join(lineas))

    def graficar_intervalo_biseccion(self):
        """Copia expresión e intervalo de búsqueda a la pestaña del graficador."""
        for campo, valor in ((self.g_expr, self.b_expr.get()), (self.g_xmin, self.b_a.get()), (self.g_xmax, self.b_b.get())):
            campo.delete(0, "end")
            campo.insert(0, valor)
        self.pestanas.set("Graficador")
        self.dibujar_grafica()

    def mostrar_guia(self):
        """Presenta instrucciones breves y criterios matemáticos de las cuatro pestañas."""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Cómo usar · Métodos numéricos")
        ventana.geometry("720x560")
        # En Windows la ventana nueva a veces queda detrás de la principal.
        ventana.after(150, ventana.lift)
        ventana.after(150, ventana.focus_force)
        caja = ctk.CTkTextbox(ventana, wrap="word", font=ctk.CTkFont(size=14))
        caja.pack(fill="both", expand=True, padx=18, pady=18)
        texto = (
            "BISECCIÓN\n"
            "Escribe f(x), a<b, tolerancia absoluta positiva y un máximo de iteraciones. "
            "Usa ** para potencias. La fila k registra sus extremos antes de actualizar. "
            "Eb=(b-a)/2; el cambio de signo no demuestra continuidad: comprueba que la función "
            "sea continua en todo el intervalo. La comparación con SciPy se omite por las reglas del proyecto.\n\n"
            "GRAFICADOR\n"
            "Escribe la misma sintaxis segura y un intervalo horizontal. Puedes fijar ambos "
            "límites verticales o dejarlos vacíos. Se muestrean 1200 puntos; se excluyen dominios "
            "inválidos y se separan segmentos ante saltos grandes. Tras resolver bisección, "
            "«Graficar este intervalo» pasa la función y el intervalo a esta pestaña.\n\n"
            "NOTACIÓN POSICIONAL\n"
            "Introduce un entero decimal para descomponerlo en potencias de 10 y convertirlo a "
            "binario, o introduce dígitos 0/1 para desarrollar potencias de 2. Si el número es "
            "negativo, el signo se conserva y las potencias se aplican a su valor absoluto.\n\n"
            "ERRORES NUMÉRICOS\n"
            "Revisa los ejemplos de float, épsilon, overflow, underflow y tipos de error. Introduce "
            "valor verdadero/aproximado para calcular errores. Para propagación, x se mide en "
            "radianes y Δy≈f'(x)Δx es una linealización que mejora con perturbaciones pequeñas."
        )
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def _crear_graficador(self, parent):
        marco = ctk.CTkFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True)
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(anchor="w", padx=12, pady=4)
        self.g_expr = self._entrada(fila, "f(x)", "1/x", 220)
        self.g_xmin = self._entrada(fila, "x mínimo", "-5", 90)
        self.g_xmax = self._entrada(fila, "x máximo", "5", 90)
        self.g_ymin = self._entrada(fila, "y mínimo (opcional)", "", 120)
        self.g_ymax = self._entrada(fila, "y máximo (opcional)", "", 120)
        boton_primario(fila, "Graficar", self.dibujar_grafica, width=110).pack(side="left", padx=6, pady=20)
        self.canvas = tk.Canvas(marco, background="#171719", highlightthickness=0, height=400)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        self.canvas.bind("<Configure>", lambda _evento: self._repintar_ultima_grafica())

    def dibujar_grafica(self):
        """Muestrea la función y dibuja cuadrícula, ejes, curva y resultado de bisección."""
        try:
            ymin_txt, ymax_txt = self.g_ymin.get().strip(), self.g_ymax.get().strip()
            if bool(ymin_txt) != bool(ymax_txt):
                raise ValueError("Ingrese ambos límites verticales o deje los dos vacíos.")
            limites = (_leer_real(ymin_txt, "y mínimo"), _leer_real(ymax_txt, "y máximo")) if ymin_txt else None
            self.ultima_muestra = muestrear_funcion(
                self.g_expr.get(), self.g_xmin.get(), self.g_xmax.get(), limites_y=limites
            )
        except (ValueError, OverflowError) as error:
            self._mostrar_error(error)
            return
        self._repintar_ultima_grafica()

    def _repintar_ultima_grafica(self):
        """Dibuja la última muestra usando el tamaño actual del lienzo."""
        if self.ultima_muestra is None:
            return
        muestra, canvas = self.ultima_muestra, self.canvas
        ancho, alto = max(200, canvas.winfo_width()), max(180, canvas.winfo_height())
        margen = 48
        valores = [y for segmento in muestra["segmentos"] for _, y in segmento]
        canvas.delete("all")
        if not valores:
            canvas.create_text(ancho / 2, alto / 2, text="No hay puntos reales finitos en el dominio.", fill="#E4E4E7")
            return
        if muestra["y_min"] is None:
            ymin, ymax = min(valores), max(valores)
            if ymin == ymax:
                ymin, ymax = ymin - 1, ymax + 1
            else:
                espacio = (ymax - ymin) * 0.08
                ymin, ymax = ymin - espacio, ymax + espacio
        else:
            ymin, ymax = muestra["y_min"], muestra["y_max"]
        xmin, xmax = muestra["x_min"], muestra["x_max"]
        px = lambda x: margen + (x - xmin) * (ancho - 2 * margen) / (xmax - xmin)
        py = lambda y: alto - margen - (y - ymin) * (alto - 2 * margen) / (ymax - ymin)
        for indice in range(6):
            gx = margen + indice * (ancho - 2 * margen) / 5
            gy = margen + indice * (alto - 2 * margen) / 5
            canvas.create_line(gx, margen, gx, alto - margen, fill="#303036")
            canvas.create_line(margen, gy, ancho - margen, gy, fill="#303036")
            xv = xmin + indice * (xmax - xmin) / 5
            yv = ymax - indice * (ymax - ymin) / 5
            canvas.create_text(gx, alto - margen + 17, text=f"{xv:.3g}", fill="#B8B8C0")
            canvas.create_text(margen - 24, gy, text=f"{yv:.3g}", fill="#B8B8C0")
        if xmin <= 0 <= xmax:
            canvas.create_line(px(0), margen, px(0), alto - margen, fill="#85858D", width=2)
        if ymin <= 0 <= ymax:
            canvas.create_line(margen, py(0), ancho - margen, py(0), fill="#85858D", width=2)
        for segmento in muestra["segmentos"]:
            coords = [coordenada for x, y in segmento for coordenada in (px(x), py(y))]
            if len(coords) >= 4:
                canvas.create_line(*coords, fill="#66C2A5", width=2, smooth=False)
        canvas.create_text(ancho / 2, 14, text=f"f(x) = {self.g_expr.get()}", fill="#F0F0F2", font=("Segoe UI", 12, "bold"))
        canvas.create_text(ancho / 2, alto - 9, text="x", fill="#E4E4E7")
        canvas.create_text(13, alto / 2, text="f(x)", fill="#E4E4E7", angle=90)
        canvas.create_rectangle(ancho - 160, 18, ancho - 142, 27, fill="#66C2A5", outline="")
        canvas.create_text(ancho - 136, 23, text="f(x)", fill="#E4E4E7", anchor="w")
        resultado = self.ultimo_resultado
        if resultado and resultado["expresion"] == self.g_expr.get().strip():
            xr, fr = resultado["raiz"], resultado["f_raiz"]
            if xmin <= xr <= xmax and ymin <= fr <= ymax:
                canvas.create_oval(px(xr)-5, py(fr)-5, px(xr)+5, py(fr)+5, fill="#F4A261", outline="white")
                canvas.create_text(px(xr)+9, py(fr)-10, text=f"raíz ≈ {xr:.6g}", fill="#F4A261", anchor="w")
                a0, b0 = resultado["a"], resultado["b"]
                if xmin <= a0 <= xmax and xmin <= b0 <= xmax and ymin <= 0 <= ymax:
                    canvas.create_line(px(a0), py(0), px(b0), py(0), fill="#F4A261", width=4)

    def _crear_notacion(self, parent):
        marco = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True)
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(anchor="w", padx=12, pady=12)
        self.n_decimal = self._entrada(fila, "Entero decimal", "84506", 180)
        boton_primario(fila, "Descomponer y convertir", self.convertir_decimal, width=205).pack(side="left", padx=8, pady=18)
        segunda = ctk.CTkFrame(marco, fg_color="transparent")
        segunda.pack(anchor="w", padx=12)
        self.n_binario = self._entrada(segunda, "Número binario", "11110011", 180)
        boton_secundario(segunda, "Convertir a decimal", self.convertir_binario, width=180).pack(side="left", padx=8, pady=18)
        etiqueta(marco, "Los negativos conservan su signo y la descomposición se realiza sobre el valor absoluto.", tamano=13).pack(anchor="w", padx=12, pady=8)
        self.n_resultado = self._caja_texto(marco, 12)

    def convertir_decimal(self):
        """Muestra forma posicional en base 10 y su conversión exacta a base 2."""
        try:
            texto = self.n_decimal.get().strip()
            valor = _leer_entero(texto, "El valor decimal")
            if texto not in (str(valor), f"+{valor}"):
                raise ValueError("El valor decimal debe ser un entero, sin separadores ni parte decimal.")
            decimal, binario = descomponer_decimal(valor), decimal_a_binario(valor)
        except ValueError as error:
            self._mostrar_error(error)
            return
        signo = "El signo se conserva; las potencias se aplican al valor absoluto.\n" if valor < 0 else ""
        self._poner(self.n_resultado, f"Base de origen: 10\n{signo}({valor})₁₀ = {decimal['descomposicion']}\nSuma posicional = {valor}\n\nBase del resultado: 2\n({valor})₁₀ = ({binario['binario']})₂\nComprobación: la conversión inversa produce {binario['equivalente']}₁₀.")

    def convertir_binario(self):
        """Muestra la expansión binaria y su suma posicional decimal."""
        try:
            datos = binario_a_decimal(self.n_binario.get())
        except ValueError as error:
            self._mostrar_error(error)
            return
        signo = "El signo se conserva y la expansión se realiza sobre el valor absoluto.\n" if datos["decimal"] < 0 else ""
        suma = " + ".join(str(valor) for valor in datos["parciales"])
        self._poner(self.n_resultado, f"Base de origen: 2\n{signo}({datos['binario']})₂ = {datos['descomposicion']}\n= {suma} = ({datos['decimal']})₁₀\nComprobación: decimal a binario devuelve {datos['binario']}.")

    def _crear_errores(self, parent):
        marco = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True)
        punto = analizar_punto_flotante()
        bloque = (
            "REPRESENTACIÓN FLOAT\n"
            f"0.1 + 0.2 = {punto['suma']!r}; comparación con 0.3: {punto['igual_a_03']}\n"
            f"Diferencia respecto a 0.3: {punto['diferencia']:.18g}\n"
            f"Épsilon de máquina: {punto['epsilon']:.17g} — {punto['epsilon_explicacion']}\n"
            f"Overflow ilustrativo (1e308 × 1e308): {punto['overflow']}\n"
            f"Underflow ilustrativo (1e-300 × 1e-300): {punto['underflow']}\n"
            f"Pérdida de precisión (1e16 + 1 − 1e16): {punto['perdida']}\n"
            "Overflow: la magnitud supera el rango representable y aquí produce infinito. "
            "Underflow: la magnitud cae por debajo del rango y aquí se redondea a cero.\n"
            f"Por qué: {punto['razon_binaria']}\n\nTIPOS DE ERROR\n" +
            "\n".join(f"{nombre}: {descripcion}" for nombre, descripcion in resumen_tipos_error())
        )
        etiqueta(marco, bloque, tamano=13, justify="left", anchor="w").pack(fill="x", padx=12, pady=12)
        etiqueta(marco, "Error absoluto y relativo", tamano=16, negrita=True, color="texto").pack(anchor="w", padx=12, pady=(8, 0))
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(anchor="w", padx=12)
        self.e_verdadero = self._entrada(fila, "Valor verdadero", "10", 150)
        self.e_aproximado = self._entrada(fila, "Valor aproximado", "9.8", 150)
        boton_primario(fila, "Calcular errores", self.calcular_errores, width=150).pack(side="left", padx=8, pady=18)
        etiqueta(marco, "Propagación para f(x) = sin(x) + x²", tamano=16, negrita=True, color="texto").pack(anchor="w", padx=12, pady=(8, 0))
        fila2 = ctk.CTkFrame(marco, fg_color="transparent")
        fila2.pack(anchor="w", padx=12)
        self.e_x = self._entrada(fila2, "x (radianes)", "0.5", 150)
        self.e_dx = self._entrada(fila2, "Δx", "0.01", 150)
        boton_secundario(fila2, "Calcular propagación", self.calcular_propagacion, width=180).pack(side="left", padx=8, pady=18)
        self.e_resultado = self._caja_texto(marco, 8)

    def calcular_errores(self):
        """Calcula y presenta errores absoluto, relativo y porcentual."""
        try:
            datos = calcular_errores(self.e_verdadero.get(), self.e_aproximado.get())
        except ValueError as error:
            self._mostrar_error(error)
            return
        relativo = "No definido porque el valor verdadero es cero." if datos["relativo"] is None else f"{datos['relativo']:.10g}"
        porcentaje = "No definido." if datos["porcentual"] is None else f"{datos['porcentual']:.10g}%"
        self._poner(self.e_resultado, f"Error absoluto = |{datos['verdadero']} − {datos['aproximado']}| = {datos['absoluto']}\nError relativo = {relativo}\nError porcentual = {porcentaje}")

    def calcular_propagacion(self):
        """Calcula cambio real, aproximación lineal y su diferencia absoluta."""
        try:
            datos = propagar_error(self.e_x.get(), self.e_dx.get())
        except (ValueError, OverflowError) as error:
            self._mostrar_error(error)
            return
        texto = (
            f"f(x) = {datos['f_x']:.12g}\n"
            f"f(x + Δx) = {datos['f_perturbado']:.12g}\n"
            f"Cambio real Δy = f(x+Δx) − f(x) = {datos['delta_y_real']:.12g}\n"
            f"f'(x) = cos(x) + 2x = {datos['derivada']:.12g}\n"
            f"Cambio aproximado Δy ≈ f'(x)·Δx = {datos['delta_y_aproximado']:.12g}\n"
            f"Diferencia absoluta = {datos['diferencia_absoluta']:.12g}\n"
            "La derivada proporciona una linealización de primer orden; suele aproximar mejor para perturbaciones pequeñas."
        )
        self._poner(self.e_resultado, texto)

    @staticmethod
    def _formato(valor):
        return "—" if valor is None else f"{valor:.6g}"

    @staticmethod
    def _poner(caja, texto):
        reemplazar_texto(caja, texto)

    @staticmethod
    def _mostrar_error(error):
        from tkinter import messagebox
        messagebox.showerror("Revisa los datos", str(error))
