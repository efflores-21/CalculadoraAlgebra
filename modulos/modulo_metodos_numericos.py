"""Pantalla integrada de bisección, gráficas, notación posicional y errores numéricos."""

import math
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
from backend.newton_raphson import resolver_newton_raphson
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
    if not re.fullmatch(r"[+-]?[0-9]+", texto):
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


MAX_FILAS_TABLA = 50


def _filas_a_mostrar(tabla, maximo=MAX_FILAS_TABLA):
    """Primeras y últimas iteraciones, con None donde se omiten las del medio."""
    # Cada celda es un widget: con ~1000 iteraciones (tolerancia 1e-300) dibujarlas
    # todas congelaba la app varios minutos.
    if len(tabla) <= maximo:
        return list(tabla)
    mitad = maximo // 2
    return tabla[:mitad] + [None] + tabla[-mitad:]


def _formatear_numero(valor):
    """Formatea números para la GUI sin perder valores pequeños ni precisión interna."""
    if valor is None:
        return "—"
    if not math.isfinite(valor):
        return "No finito"
    if valor == 0:
        return "0"
    magnitud = abs(valor)
    if 1e-4 <= magnitud < 1e7:
        return f"{valor:.8g}"
    return f"{valor:.6e}"


class ModuloMetodosNumericos(ctk.CTkFrame):
    """Agrupa las actividades de métodos numéricos en pestañas de una misma pantalla."""

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
        etiqueta(self, "Bisección · Graficador · Notación posicional · Errores numéricos · Newton-Raphson", tamano=14).pack(
            anchor="w", padx=34, pady=(0, 8))
        self.pestanas = ctk.CTkTabview(self, fg_color=COLOR["tarjeta"])
        self.pestanas.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        for nombre in ("Bisección", "Graficador", "Notación posicional", "Errores numéricos", "Newton-Raphson"):
            self.pestanas.add(nombre)
        self._crear_biseccion(self.pestanas.tab("Bisección"))
        self._crear_graficador(self.pestanas.tab("Graficador"))
        self._crear_notacion(self.pestanas.tab("Notación posicional"))
        self._crear_errores(self.pestanas.tab("Errores numéricos"))
        self._crear_newton_raphson(self.pestanas.tab("Newton-Raphson"))

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
        self.b_resultado = ctk.CTkFrame(marco, fg_color="transparent")
        self.b_resultado.pack(fill="x", expand=True, padx=6, pady=(8, 12))

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
        for widget in self.b_resultado.winfo_children():
            widget.destroy()

        def numero(valor):
            return "—" if valor is None else f"{valor:.8g}"

        resumen = ctk.CTkFrame(self.b_resultado, fg_color="transparent")
        resumen.pack(fill="x", padx=6, pady=(0, 8))
        valores = (
            ("Raíz aproximada", numero(datos["raiz"])),
            ("Iteraciones realizadas", str(datos["iteraciones"])),
            ("Iteraciones teóricas", str(datos["iteraciones_teoricas"])),
            ("Intervalo final", f"[{numero(datos['intervalo_final'][0])}, {numero(datos['intervalo_final'][1])}]"),
            ("Cota de error final", numero(datos["cota_error"])),
            ("Tolerancia solicitada", numero(float(self.b_tol.get()))),
        )
        for columna in range(3):
            resumen.grid_columnconfigure(columna, weight=1, uniform="resumen_biseccion")
        for indice, (titulo, valor) in enumerate(valores):
            tarjeta = ctk.CTkFrame(resumen, fg_color=COLOR["tarjeta"], corner_radius=10,
                                   border_width=1, border_color=COLOR["borde"])
            tarjeta.grid(row=indice // 3, column=indice % 3, sticky="ew", padx=4, pady=4)
            etiqueta(tarjeta, titulo, tamano=11, color="gris").pack(anchor="w", padx=12, pady=(8, 1))
            etiqueta(tarjeta, valor, tamano=14, negrita=True, color="texto").pack(anchor="w", padx=12, pady=(0, 8))

        if datos["aviso_discontinuidad"]:
            estado = "Sin raíz confiable: posible asíntota"
        elif datos["alcanzada_tolerancia"]:
            estado = "Tolerancia alcanzada"
        elif "precisión" in datos["motivo"]:
            estado = "Límite de precisión de la computadora"
        else:
            estado = "Máximo de iteraciones alcanzado"
        if datos["aviso_discontinuidad"]:
            color_estado = COLOR["mal"]
        else:
            color_estado = "#66C2A5" if datos["alcanzada_tolerancia"] else "#F4A261"
        tarjeta_estado = ctk.CTkFrame(resumen, fg_color=COLOR["tarjeta"], corner_radius=10,
                                      border_width=1, border_color=COLOR["borde"])
        tarjeta_estado.grid(row=2, column=0, columnspan=3, sticky="ew", padx=4, pady=4)
        etiqueta(tarjeta_estado, "Estado de terminación", tamano=11, color="gris").pack(
            anchor="w", padx=12, pady=(8, 1)
        )
        ctk.CTkLabel(tarjeta_estado, text=estado, text_color=color_estado,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(0, 8))
        explicacion = (
            "Se alcanzó la tolerancia solicitada porque la cota del semiancho del intervalo final "
            "es menor o igual que la tolerancia establecida."
            if datos["alcanzada_tolerancia"] else
            datos["motivo"] if "precisión" in datos["motivo"] else
            "Se llegó al máximo de iteraciones antes de cumplir la tolerancia; la aproximación mostrada "
            "no garantiza que el error sea menor o igual que el valor solicitado."
        )
        if datos["aviso_discontinuidad"]:
            ctk.CTkLabel(self.b_resultado, text="⚠  " + datos["aviso_discontinuidad"], text_color=COLOR["mal"],
                         font=ctk.CTkFont(size=13, weight="bold"), anchor="w", justify="left",
                         wraplength=900).pack(anchor="w", padx=10, pady=(6, 2))
        etiqueta(self.b_resultado, datos["advertencia"], tamano=11, color="gris").pack(
            anchor="w", padx=10, pady=(4, 6)
        )

        contenedor = ctk.CTkFrame(self.b_resultado, fg_color=COLOR["tarjeta"], corner_radius=10)
        contenedor.pack(fill="x", expand=True, padx=6, pady=(0, 6))
        canvas = tk.Canvas(contenedor, height=330, background=COLOR["tarjeta"],
                           highlightthickness=0, borderwidth=0)
        barra_y = ctk.CTkScrollbar(contenedor, orientation="vertical", command=canvas.yview)
        barra_x = ctk.CTkScrollbar(contenedor, orientation="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)
        tabla = ctk.CTkFrame(canvas, fg_color=COLOR["tarjeta"], width=1390)
        canvas.create_window((0, 0), window=tabla, anchor="nw")
        tabla.bind("<Configure>", lambda _evento: canvas.configure(scrollregion=canvas.bbox("all")))

        titulos = ("Iteración", "a", "b", "Punto medio (xr)", "f(xr)", "Cota de error",
                   "Error aproximado", "Intervalo conservado")
        anchos = (76, 145, 145, 165, 145, 145, 165, 260)
        for columna, (titulo, ancho) in enumerate(zip(titulos, anchos)):
            ctk.CTkLabel(tabla, text=titulo, width=ancho, height=42, anchor="center",
                         fg_color=COLOR["acento"], text_color=COLOR["texto"],
                         font=ctk.CTkFont(size=12, weight="bold")).grid(
                             row=0, column=columna, sticky="nsew", padx=1, pady=1)
        if not datos["tabla"]:
            etiqueta(tabla, "La raíz exacta está en un extremo; no se requieren iteraciones.",
                     tamano=12, color="gris").grid(row=1, column=0, columnspan=8, sticky="w", padx=12, pady=12)
        fuente_celda = ctk.CTkFont(size=12)
        for fila, paso in enumerate(_filas_a_mostrar(datos["tabla"]), 1):
            if paso is None:
                omitidas = len(datos["tabla"]) - MAX_FILAS_TABLA
                etiqueta(tabla, f"…  {omitidas} iteraciones intermedias no se muestran "
                                f"(hay {len(datos['tabla'])} en total; el resumen de arriba usa todas)  …",
                         tamano=12, color="gris").grid(row=fila, column=0, columnspan=8, pady=8)
                continue
            intervalo = paso["intervalo_siguiente"]
            if paso["fr"] == 0:
                conservado = f"Raíz exacta: xr = {numero(paso['xr'])}"
            elif intervalo[1] == paso["xr"]:
                conservado = f"[a, xr] = [{numero(intervalo[0])}, {numero(intervalo[1])}]"
            else:
                conservado = f"[xr, b] = [{numero(intervalo[0])}, {numero(intervalo[1])}]"
            celdas = (str(paso["k"]), numero(paso["a"]), numero(paso["b"]), numero(paso["xr"]),
                      numero(paso["fr"]), numero(paso["cota_error"]),
                      numero(paso["error_absoluto_aprox"]), conservado)
            fondo = COLOR["suave"] if fila % 2 == 0 else COLOR["tarjeta"]
            for columna, (valor, ancho) in enumerate(zip(celdas, anchos)):
                ctk.CTkLabel(tabla, text=valor, width=ancho, height=34, anchor="center",
                             fg_color=fondo, text_color=COLOR["texto"],
                             font=fuente_celda).grid(
                                 row=fila, column=columna, sticky="nsew", padx=1, pady=1)
        cabecera = ctk.CTkFrame(self.b_resultado, fg_color=COLOR["suave"], corner_radius=8)
        cabecera.pack(fill="x", padx=6, pady=(4, 0))
        ctk.CTkLabel(cabecera, text=estado, text_color=color_estado,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(9, 2))
        etiqueta(cabecera, explicacion, tamano=12, color="texto").pack(anchor="w", padx=12, pady=(0, 9))

    def _crear_newton_raphson(self, parent):
        """Construye el formulario, el resumen numérico y la tabla de Newton-Raphson."""
        marco = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        marco.pack(fill="both", expand=True)
        etiqueta(
            marco,
            "Usa la misma sintaxis segura que las otras herramientas: ** para potencias y funciones como sin(x), cos(x), exp(x). "
            "La tolerancia se introduce en porcentaje.",
            tamano=13,
        ).pack(anchor="w", padx=12, pady=(10, 5))

        fila_funcion = ctk.CTkFrame(marco, fg_color="transparent")
        fila_funcion.pack(anchor="w", padx=12)
        self.nr_expr = self._entrada(fila_funcion, "Función f(x)", "x**3 - 2*x - 5", 360)
        self.nr_x0 = self._entrada(fila_funcion, "Valor inicial x₀", "2", 130)

        fila_parametros = ctk.CTkFrame(marco, fg_color="transparent")
        fila_parametros.pack(anchor="w", padx=12)
        self.nr_tol = self._entrada(fila_parametros, "Tolerancia (%)", "0.0001", 150)
        self.nr_max = self._entrada(fila_parametros, "Máximo de iteraciones", "100", 180)

        acciones = ctk.CTkFrame(marco, fg_color="transparent")
        acciones.pack(anchor="w", padx=12, pady=5)
        boton_primario(acciones, "Calcular", self.calcular_newton_raphson, width=130).pack(side="left", padx=(0, 8))
        boton_secundario(acciones, "Ejemplo", self.ejemplo_newton_raphson, width=110).pack(side="left", padx=(0, 8))
        boton_secundario(acciones, "Limpiar", self.limpiar_newton_raphson, width=110).pack(side="left")

        self.nr_estado = ctk.CTkLabel(
            marco, text="Ingresa una función y sus parámetros para comenzar.",
            text_color=COLOR["gris"], anchor="w", justify="left",
            font=ctk.CTkFont(size=13),
        )
        self.nr_estado.pack(fill="x", padx=16, pady=(4, 6))
        self.nr_resultado = ctk.CTkFrame(marco, fg_color="transparent")
        self.nr_resultado.pack(fill="both", expand=True, padx=6, pady=(4, 12))
        self.nr_grafica = None
        self.nr_datos = None
        self.nr_paso_seleccionado = 0

    def _vaciar_resultado_newton(self):
        """Elimina el resumen y las filas anteriores antes de una nueva ejecución."""
        for widget in self.nr_resultado.winfo_children():
            widget.destroy()

    def ejemplo_newton_raphson(self):
        """Carga un ejemplo didáctico válido para el evaluador actual."""
        for campo, valor in (
            (self.nr_expr, "x**3 - 2*x - 5"),
            (self.nr_x0, "2"),
            (self.nr_tol, "0.0001"),
            (self.nr_max, "100"),
        ):
            campo.delete(0, "end")
            campo.insert(0, valor)
        self._vaciar_resultado_newton()
        self.nr_estado.configure(text="Ejemplo cargado. Pulsa Calcular para ver las iteraciones.",
                                 text_color=COLOR["gris"])

    def limpiar_newton_raphson(self):
        """Restablece campos, estado, resumen y tabla de iteraciones."""
        self.nr_expr.delete(0, "end")
        for campo, valor in ((self.nr_x0, "1"), (self.nr_tol, "0.0001"), (self.nr_max, "100")):
            campo.delete(0, "end")
            campo.insert(0, valor)
        self._vaciar_resultado_newton()
        self.nr_estado.configure(text="Formulario limpiado. Escribe una función para comenzar.",
                                 text_color=COLOR["gris"])

    def calcular_newton_raphson(self):
        """Valida las entradas, invoca el backend y presenta su resultado sin recalcularlo."""
        self._vaciar_resultado_newton()
        try:
            expresion = self.nr_expr.get().strip()
            if not expresion:
                raise ValueError("Escribe una función matemática en f(x).")
            x0 = _leer_real(self.nr_x0.get(), "El valor inicial x₀")
            tolerancia = _leer_real(self.nr_tol.get(), "La tolerancia")
            maximo = _leer_entero(self.nr_max.get(), "El máximo de iteraciones")
            datos = resolver_newton_raphson(expresion, x0, tolerancia, maximo)
        except (ValueError, OverflowError) as error:
            self.nr_estado.configure(text="No se pudo calcular. Revisa los datos ingresados.",
                                     text_color=COLOR["mal"])
            self._mostrar_error(error)
            return
        except Exception:
            self.nr_estado.configure(text="Ocurrió un error inesperado durante el cálculo.",
                                     text_color=COLOR["mal"])
            self._mostrar_error(ValueError(
                "No se pudo completar el cálculo. Revisa la función y vuelve a intentarlo."
            ))
            return

        self._mostrar_resultado_newton(datos)

    def _mostrar_resultado_newton(self, datos):
        """Muestra las métricas devueltas por el backend y la traza de iteraciones."""
        if datos["convergio"]:
            estado = "Convergió"
            color_estado = COLOR["ok"]
            self.nr_estado.configure(text="Newton-Raphson convergió con los criterios solicitados.",
                                     text_color=color_estado)
        elif datos["estado"] == "maximo":
            estado = "No convergió dentro del máximo de iteraciones"
            color_estado = "#F4A261"
            self.nr_estado.configure(text=estado + ". La última aproximación no se confirma como raíz.",
                                     text_color=color_estado)
        else:
            estado = "Detenido por una condición matemática o numérica"
            color_estado = COLOR["mal"]
            self.nr_estado.configure(text=estado + ". Revisa el motivo indicado en los resultados.",
                                     text_color=color_estado)

        if datos["error_final"] is not None:
            error_final = _formatear_numero(datos["error_final"]) + "%"
        elif datos["iteraciones"] and datos["tabla"][-1].get("xi_siguiente") == 0:
            error_final = "No definido (xₙ₊₁ = 0)"
        elif datos["iteraciones"] == 0 and datos["convergio"]:
            error_final = "No aplica (raíz inicial exacta)"
        else:
            error_final = "No disponible"

        etiqueta_aproximacion = (
            "Aproximación de la raíz" if datos["convergio"]
            else "Última aproximación (no confirmada como raíz)"
        )
        valores = (
            ("Función original", datos["expresion"]),
            ("Derivada simbólica", datos["derivada"]),
            (etiqueta_aproximacion, _formatear_numero(datos["aproximacion"])),
            ("Estado", estado),
            ("Iteraciones realizadas", str(datos["iteraciones"])),
            ("Error aproximado final", error_final),
            ("Residuo final |f(x)|", _formatear_numero(datos["residuo_final"])),
            ("Residuo relativo al inicial", (
                "—" if datos.get("residuo_relativo_porcentual_final") is None else
                _formatear_numero(datos["residuo_relativo_porcentual_final"]) + "%"
            )),
            ("Motivo de finalización", datos["motivo"]),
        )
        resumen = ctk.CTkFrame(self.nr_resultado, fg_color="transparent")
        resumen.pack(fill="x", padx=6, pady=(0, 8))
        for columna in range(3):
            resumen.grid_columnconfigure(columna, weight=1, uniform="resumen_newton")
        for indice, (titulo, valor) in enumerate(valores):
            tarjeta = ctk.CTkFrame(resumen, fg_color=COLOR["tarjeta"], corner_radius=10,
                                   border_width=1, border_color=COLOR["borde"])
            tarjeta.grid(row=indice // 3, column=indice % 3, sticky="nsew", padx=4, pady=4)
            etiqueta(tarjeta, titulo, tamano=11, color="gris").pack(anchor="w", padx=12, pady=(8, 1))
            ctk.CTkLabel(
                tarjeta, text=valor, text_color=color_estado if titulo == "Estado" else COLOR["texto"],
                font=ctk.CTkFont(size=13, weight="bold"), anchor="w", justify="left",
                wraplength=340,
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 8))

        self.nr_datos = datos
        self.nr_paso_seleccionado = max(0, len(datos["tabla"]) - 1)
        self._crear_grafica_newton()

        etiqueta(self.nr_resultado, "Tabla de iteraciones", tamano=15, negrita=True, color="texto").pack(
            anchor="w", padx=10, pady=(6, 4)
        )
        contenedor = ctk.CTkFrame(self.nr_resultado, fg_color=COLOR["tarjeta"], corner_radius=10)
        contenedor.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        canvas = tk.Canvas(contenedor, height=290, background=COLOR["tarjeta"],
                           highlightthickness=0, borderwidth=0)
        barra_y = ctk.CTkScrollbar(contenedor, orientation="vertical", command=canvas.yview)
        barra_x = ctk.CTkScrollbar(contenedor, orientation="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        titulos = ("Iteración", "Xi", "f(Xi)", "f′(Xi)", "Xi+1", "Error aprox. (%)",
                   "Residuo |f(Xi+1)|", "Residuo relativo (%)")
        anchos = (76, 130, 145, 145, 130, 150, 165, 170)
        tabla = ctk.CTkFrame(canvas, fg_color=COLOR["tarjeta"], width=sum(anchos))
        canvas.create_window((0, 0), window=tabla, anchor="nw")
        tabla.bind("<Configure>", lambda _evento: canvas.configure(scrollregion=canvas.bbox("all")))
        for columna, (titulo, ancho) in enumerate(zip(titulos, anchos)):
            ctk.CTkLabel(tabla, text=titulo, width=ancho, height=42, anchor="center",
                         fg_color=COLOR["acento"], text_color=COLOR["texto"],
                         font=ctk.CTkFont(size=11, weight="bold")).grid(
                             row=0, column=columna, sticky="nsew", padx=1, pady=1)

        if not datos["tabla"]:
            mensaje = ("El valor inicial ya era una raíz; no se requirieron iteraciones."
                       if datos["convergio"] else "No se completó ninguna iteración.")
            etiqueta(tabla, mensaje, tamano=12, color="gris").grid(
                row=1, column=0, columnspan=len(titulos), sticky="w", padx=12, pady=12
            )
        fuente_celda = ctk.CTkFont(size=11)
        for fila, paso in enumerate(_filas_a_mostrar(datos["tabla"]), 1):
            if paso is None:
                omitidas = len(datos["tabla"]) - MAX_FILAS_TABLA
                etiqueta(tabla, f"…  {omitidas} iteraciones intermedias omitidas; se registraron {len(datos['tabla'])} en total  …",
                         tamano=12, color="gris").grid(
                             row=fila, column=0, columnspan=len(titulos), pady=8
                         )
                continue
            error = paso.get("error_aproximado_porcentual")
            if error is None and paso.get("xi_siguiente") == 0:
                error_texto = "No definido"
            else:
                error_texto = "—" if error is None else _formatear_numero(error) + "%"
            celdas = (
                str(paso["k"]), _formatear_numero(paso["xi"]), _formatear_numero(paso["fxi"]),
                _formatear_numero(paso.get("derivada")), _formatear_numero(paso.get("xi_siguiente")),
                error_texto, _formatear_numero(paso.get("residuo")),
                ("—" if paso.get("residuo_relativo_porcentual") is None else
                 _formatear_numero(paso["residuo_relativo_porcentual"]) + "%"),
            )
            fondo = COLOR["suave"] if fila % 2 == 0 else COLOR["tarjeta"]
            for columna, (valor, ancho) in enumerate(zip(celdas, anchos)):
                celda = ctk.CTkLabel(tabla, text=valor, width=ancho, height=34, anchor="center",
                                     fg_color=fondo, text_color=COLOR["texto"], font=fuente_celda)
                celda.grid(
                                 row=fila, column=columna, sticky="nsew", padx=1, pady=1)
                celda.bind("<Button-1>", lambda _evento, indice=len([p for p in datos["tabla"][:paso["k"]]
                                                                      if p is not None]) - 1:
                           self._seleccionar_paso_newton(indice))

    def _crear_grafica_newton(self):
        """Crea la gráfica y controles; navegar reutiliza la traza ya calculada."""
        marco = ctk.CTkFrame(self.nr_resultado, fg_color=COLOR["tarjeta"], corner_radius=10)
        marco.pack(fill="x", padx=6, pady=(4, 10))
        etiqueta(marco, "Gráfica interactiva de Newton-Raphson", tamano=15,
                 negrita=True, color="texto").pack(anchor="w", padx=12, pady=(9, 2))
        self.nr_info_paso = ctk.CTkLabel(marco, text="", anchor="w", justify="left",
                                          text_color=COLOR["texto"])
        self.nr_info_paso.pack(fill="x", padx=12, pady=(0, 5))
        controles = ctk.CTkFrame(marco, fg_color="transparent")
        controles.pack(fill="x", padx=10, pady=(0, 5))
        self.nr_boton_anterior = boton_secundario(
            controles, "◀ Anterior", lambda: self._navegar_paso_newton(-1), width=115)
        self.nr_boton_anterior.pack(side="left", padx=(0, 8))
        filas = self.nr_datos["tabla"]
        self.nr_slider = ctk.CTkSlider(
            controles, from_=0, to=max(1, len(filas) - 1), number_of_steps=max(1, len(filas) - 1),
            command=self._cambiar_paso_newton)
        self.nr_slider.set(self.nr_paso_seleccionado)
        self.nr_slider.pack(side="left", fill="x", expand=True, padx=6)
        self.nr_boton_siguiente = boton_secundario(
            controles, "Siguiente ▶", lambda: self._navegar_paso_newton(1), width=115)
        self.nr_boton_siguiente.pack(side="left", padx=(8, 0))
        self.nr_canvas = tk.Canvas(marco, height=350, background=COLOR["tarjeta"],
                                   highlightthickness=0, borderwidth=0)
        self.nr_canvas.pack(fill="x", expand=True, padx=6, pady=(0, 8))
        self.nr_canvas.bind("<Configure>", lambda _evento: self._dibujar_grafica_newton())
        self._dibujar_grafica_newton()

    def _navegar_paso_newton(self, desplazamiento):
        if not self.nr_datos or not self.nr_datos["tabla"]:
            return
        self._seleccionar_paso_newton(self.nr_paso_seleccionado + desplazamiento)

    def _cambiar_paso_newton(self, valor):
        self._seleccionar_paso_newton(round(float(valor)), desde_slider=True)

    def _seleccionar_paso_newton(self, indice, desde_slider=False):
        if not self.nr_datos or not self.nr_datos["tabla"]:
            return
        indice = max(0, min(len(self.nr_datos["tabla"]) - 1, int(indice)))
        self.nr_paso_seleccionado = indice
        if not desde_slider:
            self.nr_slider.set(indice)
        self._dibujar_grafica_newton()

    @staticmethod
    def _rango_robusto(valores, incluir_cero=False):
        """Calcula límites centrados que reducen el efecto de iteraciones extremas."""
        finitos = sorted(v for v in valores if math.isfinite(v))
        if not finitos:
            return (-1.0, 1.0)
        mediana = finitos[len(finitos) // 2]
        desviaciones = sorted(abs(v - mediana) for v in finitos)
        mad = desviaciones[len(desviaciones) // 2]
        escala = max(4 * mad, abs(mediana) * 0.05, 0.1)
        minimo, maximo = mediana - escala, mediana + escala
        if incluir_cero:
            minimo, maximo = min(minimo, 0.0), max(maximo, 0.0)
        return minimo, maximo

    def _dibujar_grafica_newton(self):
        """Traza f(x), el recorrido y solo la tangente del paso seleccionado."""
        datos = self.nr_datos
        canvas = getattr(self, "nr_canvas", None)
        if not datos or canvas is None or not canvas.winfo_exists():
            return
        ancho, alto = max(280, canvas.winfo_width()), max(220, canvas.winfo_height())
        margen = 55
        filas = datos["tabla"]
        indice = min(self.nr_paso_seleccionado, len(filas) - 1) if filas else -1
        x0 = datos["valor_inicial"]
        xs = [x0]
        for paso in filas:
            xs.append(paso["xi"])
            if paso.get("xi_siguiente") is not None:
                xs.append(paso["xi_siguiente"])
        if datos["convergio"]:
            xs.append(datos["aproximacion"])
        xmin, xmax = self._rango_robusto(xs)
        if xmin == xmax:
            xmin, xmax = xmin - 1, xmax + 1
        muestra = muestrear_funcion(datos["expresion"], xmin, xmax, cantidad=1200)
        ys = [y for segmento in muestra["segmentos"] for _, y in segmento]
        if not ys:
            canvas.delete("all")
            canvas.create_text(ancho / 2, alto / 2, text="No hay valores reales finitos para graficar.",
                               fill=COLOR["texto"])
            return
        ymin, ymax = self._rango_robusto(ys, incluir_cero=True)
        for paso in filas:
            if ymin <= paso["fxi"] <= ymax:
                ys.append(paso["fxi"])
        ymin, ymax = self._rango_robusto(ys, incluir_cero=True)
        if ymin == ymax:
            ymin, ymax = ymin - 1, ymax + 1
        # Recorta valores atípicos al muestrear y vuelve a usar los segmentos seguros.
        muestra = muestrear_funcion(datos["expresion"], xmin, xmax, cantidad=1200,
                                   limites_y=(ymin, ymax))
        px = lambda x: margen + (x - xmin) * (ancho - 2 * margen) / (xmax - xmin)
        py = lambda y: alto - margen - (y - ymin) * (alto - 2 * margen) / (ymax - ymin)
        canvas.delete("all")
        for marca in range(6):
            gx = margen + marca * (ancho - 2 * margen) / 5
            gy = margen + marca * (alto - 2 * margen) / 5
            canvas.create_line(gx, margen, gx, alto - margen, fill="#303036")
            canvas.create_line(margen, gy, ancho - margen, gy, fill="#303036")
            canvas.create_text(gx, alto - margen + 16,
                               text=f"{xmin + marca * (xmax - xmin) / 5:.3g}", fill="#B8B8C0")
            canvas.create_text(margen - 27, gy,
                               text=f"{ymax - marca * (ymax - ymin) / 5:.3g}", fill="#B8B8C0")
        if xmin <= 0 <= xmax:
            canvas.create_line(px(0), margen, px(0), alto - margen, fill="#85858D", width=2)
        if ymin <= 0 <= ymax:
            canvas.create_line(margen, py(0), ancho - margen, py(0), fill="#85858D", width=2)
        for segmento in muestra["segmentos"]:
            coords = [c for x, y in segmento for c in (px(x), py(y))]
            if len(coords) >= 4:
                canvas.create_line(*coords, fill="#66C2A5", width=2)

        # La trayectoria usa únicamente los valores xi y xi+1 devueltos por el backend.
        for paso_indice, paso in enumerate(filas[:indice + 1]):
            xi, fxi = paso["xi"], paso["fxi"]
            if xmin <= xi <= xmax and ymin <= fxi <= ymax:
                color = "#F4A261" if paso_indice == indice else "#8AB4F8"
                canvas.create_line(px(xi), py(0), px(xi), py(fxi), fill=color, dash=(3, 3))
                canvas.create_oval(px(xi)-4, py(fxi)-4, px(xi)+4, py(fxi)+4,
                                   fill=color, outline="white")
            siguiente = paso.get("xi_siguiente")
            derivada = paso.get("derivada")
            if siguiente is not None and derivada not in (None, 0) and xmin <= siguiente <= xmax:
                tangencia_en_x = min(xmax, max(xmin, siguiente))
                y_intermedio = fxi + derivada * (tangencia_en_x - xi)
                if math.isfinite(y_intermedio) and ymin <= y_intermedio <= ymax:
                    canvas.create_line(px(tangencia_en_x), py(0), px(tangencia_en_x),
                                       py(y_intermedio), fill="#B39DDB", dash=(2, 3))
                canvas.create_oval(px(siguiente)-4, py(0)-4, px(siguiente)+4, py(0)+4,
                                   fill="#B39DDB", outline="white")
            if paso_indice == indice and derivada is not None:
                if derivada == 0:
                    if ymin <= fxi <= ymax:
                        canvas.create_line(margen, py(fxi), ancho - margen, py(fxi),
                                           fill="#F4A261", width=2, dash=(6, 3))
                    canvas.create_text(ancho / 2, alto - 27,
                                       text="Derivada cero: no existe intercepto de Newton para este paso.",
                                       fill="#F4A261")
                else:
                    # La recta se recorta al área visible y nunca evalúa valores no finitos.
                    cortes = (xi + (ymin - fxi) / derivada, xi + (ymax - fxi) / derivada)
                    if all(math.isfinite(corte) for corte in cortes):
                        xa, xb = max(xmin, min(cortes)), min(xmax, max(cortes))
                    else:
                        xa, xb = xmin, xmax
                    if xa <= xb and math.isfinite(fxi):
                        ya, yb = fxi + derivada * (xa - xi), fxi + derivada * (xb - xi)
                        if math.isfinite(ya) and math.isfinite(yb) and ymin <= ya <= ymax and ymin <= yb <= ymax:
                            canvas.create_line(px(xa), py(ya), px(xb), py(yb),
                                               fill="#F4A261", width=2, dash=(6, 3))

        if datos["convergio"] and xmin <= datos["aproximacion"] <= xmax:
            canvas.create_oval(px(datos["aproximacion"])-6, py(0)-6,
                               px(datos["aproximacion"])+6, py(0)+6,
                               fill="#66D19E", outline="white", width=2)
            canvas.create_text(px(datos["aproximacion"])+8, py(0)-14,
                               text="raíz confirmada", fill="#66D19E", anchor="w")
        canvas.create_text(ancho / 2, 15, text=f"Newton-Raphson · f(x) = {datos['expresion']}",
                           fill=COLOR["texto"], font=("Segoe UI", 12, "bold"))
        canvas.create_text(ancho - 110, 32, text="━ f(x)   ┄ tangente   ● aproximación",
                           fill=COLOR["texto"])
        if indice >= 0:
            paso = filas[indice]
            detalle = (f"Iteración {paso['k']} / {len(filas)}   ·   xi = {_formatear_numero(paso['xi'])}"
                       f"   ·   f(xi) = {_formatear_numero(paso['fxi'])}"
                       f"   ·   xi+1 = {_formatear_numero(paso.get('xi_siguiente'))}")
            if paso.get("motivo"):
                detalle += "   ·   " + paso["motivo"]
        else:
            detalle = ("Raíz inicial exacta; no se generaron tangentes." if datos["convergio"]
                       else "No se generaron iteraciones.")
        self.nr_info_paso.configure(text=detalle)
        if hasattr(self, "nr_slider"):
            self.nr_slider.configure(state="normal" if filas else "disabled")
            self.nr_boton_anterior.configure(state="normal" if indice > 0 else "disabled")
            self.nr_boton_siguiente.configure(state="normal" if indice < len(filas) - 1 else "disabled")

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
            a0, b0 = resultado["a"], resultado["b"]
            if xmin <= a0 <= xmax and xmin <= b0 <= xmax and ymin <= 0 <= ymax:
                # La guía pide identificar qué intervalo se dibuja: es el inicial [a, b].
                canvas.create_line(px(a0), py(0), px(b0), py(0), fill="#F4A261", width=4)
                canvas.create_text((px(a0) + px(b0)) / 2, py(0) + 16, fill="#F4A261",
                                   text=f"intervalo inicial de bisección [{a0:g}, {b0:g}]")
            if xmin <= xr <= xmax and ymin <= fr <= ymax:
                canvas.create_oval(px(xr)-5, py(fr)-5, px(xr)+5, py(fr)+5, fill="#F4A261", outline="white")
                canvas.create_text(px(xr)+9, py(fr)-10, text=f"raíz ≈ {xr:.6g}", fill="#F4A261", anchor="w")

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
        if datos["decimal"] < 0:
            suma = f"-({suma})"
        # Sin ceros a la izquierda: es lo que devuelve de verdad la conversión inversa.
        inverso = ("-" if datos["decimal"] < 0 else "") + format(abs(datos["decimal"]), "b")
        self._poner(self.n_resultado, f"Base de origen: 2\n{signo}({datos['binario']})₂ = {datos['descomposicion']}\n= {suma} = ({datos['decimal']})₁₀\nComprobación: decimal a binario devuelve {inverso}.")

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
    def _poner(caja, texto):
        reemplazar_texto(caja, texto)

    @staticmethod
    def _mostrar_error(error):
        from tkinter import messagebox
        messagebox.showerror("Revisa los datos", str(error))
