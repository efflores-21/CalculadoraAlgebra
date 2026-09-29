"""Panel que verifica la linealidad del producto matriz-vector."""

import customtkinter as ctk

from backend.matriz import formatear_valor
from backend.propiedades import verificar_propiedades
from modulos._comun import (
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    entrada_numero,
    etiqueta,
    formatear_matriz,
    formatear_vector,
    leer_entero,
    leer_fraccion,
    mensaje_error,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
)


class ModuloPropiedades(ctk.CTkFrame):
    """Presenta A(u+v)=Au+Av y A(cu)=c(Au) en una pantalla separada."""

    def __init__(self, master, on_back):
        """Inicializa el panel con una matriz 2x2 y vectores de dimensión 2."""
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A = []
        self.entradas_u = []
        self.entradas_v = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Construye los controles para A,u,v,c y el área de pasos."""
        zonas = crear_estructura(
            self,
            self.on_back,
            numero=6,
            titulo="Producto matriz-vector",
            descripcion="Comprueba A(u + v) = Au + Av  y  A(cu) = c(Au).",
            logo=(
                " A · x   MÓDULO: PROPIEDADES DEL PRODUCTO MATRIZ-VECTOR\n"
                "         A(u + v) = Au + Av\n"
                "         A(cu) = c(Au)"
            ),
            pasos=[
                "Escribe el tamaño de A (filas × columnas) y pulsa «Crear tablas». "
                "u y v tendrán tantos componentes como columnas tenga A.",
                "Llena la matriz A, los vectores u y v, y el escalar c.",
                "Pulsa «Verificar propiedades».",
            ],
            clave_teoremas="propiedades",
            indicacion="Aquí verás cada lado de las dos igualdades calculado paso "
                       "a paso y si se cumplen.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido

        controles, entradas = crear_controles(
            contenido,
            [("m", "Filas de A", "2", 80), ("n", "Columnas de A", "2", 100),
             ("c", "Escalar c", "2", 80, False)],
            self.actualizar_entradas,
            texto_boton="Crear tablas",
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_m, self.entry_n, self.entry_c = entradas["m"], entradas["n"], entradas["c"]

        self.panel_entradas = ctk.CTkFrame(contenido, fg_color="transparent")
        self.panel_entradas.pack(anchor="w", fill="x")

        boton_primario(zonas.acciones, "Verificar propiedades", self.verificar).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(
            side="left"
        )

    def _crear_vector(self, parent, fila, nombre, columnas):
        """Crea una fila con el nombre y n entradas: un vector de R^n."""
        etiqueta(parent, nombre, tamano=14, color="texto", negrita=True).grid(
            row=fila, column=0, sticky="w", padx=(10, 12), pady=3
        )
        entradas = []
        for j in range(columnas):
            celda = entrada_numero(parent)
            celda.grid(row=fila, column=j + 1, padx=3, pady=3)
            entradas.append(celda)
        return entradas

    def actualizar_entradas(self):
        """Reconstruye la matriz A y los vectores con las dimensiones indicadas."""
        try:
            m = leer_entero(self.entry_m, "Las filas de A")
            n = leer_entero(self.entry_n, "Las columnas de A")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.panel_entradas.winfo_children():
            widget.destroy()

        subtitulo(self.panel_entradas, f"Matriz A  ({m} × {n})").pack(
            anchor="w", padx=10, pady=(20, 6)
        )
        marco_matriz = ctk.CTkFrame(self.panel_entradas, fg_color="transparent")
        marco_matriz.pack(anchor="w", padx=6)
        self.entradas_A = []
        for i in range(m):
            fila = []
            for j in range(n):
                celda = entrada_numero(marco_matriz)
                celda.grid(row=i, column=j, padx=3, pady=3)
                fila.append(celda)
            self.entradas_A.append(fila)

        subtitulo(self.panel_entradas, "Vectores u y v").pack(
            anchor="w", padx=10, pady=(20, 6)
        )
        marco_vectores = ctk.CTkFrame(self.panel_entradas, fg_color="transparent")
        marco_vectores.pack(anchor="w")
        self.entradas_u = self._crear_vector(marco_vectores, 0, "u", n)
        self.entradas_v = self._crear_vector(marco_vectores, 1, "v", n)
        reemplazar_texto(self.resultado, "")

    def _leer_vector(self, entradas, nombre):
        """Convierte un conjunto de celdas a un vector de Fraction."""
        return [leer_fraccion(celda, nombre) for celda in entradas]

    def verificar(self):
        """Calcula y presenta las dos igualdades mediante pasos agrupados."""
        try:
            A = [
                [leer_fraccion(celda, "Una entrada de A") for celda in fila]
                for fila in self.entradas_A
            ]
            u = self._leer_vector(self.entradas_u, "u")
            v = self._leer_vector(self.entradas_v, "v")
            c = leer_fraccion(self.entry_c, "El escalar c")
            datos = verificar_propiedades(A, u, v, c)

            def vector(clave):
                return formatear_vector(datos[clave])

            estado_a = "SE CUMPLE" if datos["a_se_cumple"] else "NO SE CUMPLE"
            estado_b = "SE CUMPLE" if datos["b_se_cumple"] else "NO SE CUMPLE"
            texto = (
                "MÓDULO 6: PROPIEDADES DEL PRODUCTO MATRIZ-VECTOR\n"
                f"A =\n{formatear_matriz(A)}\n"
                f"u = {formatear_vector(u)};  v = {formatear_vector(v)};  "
                f"c = {formatear_valor(c)}\n\n"
                "A) A(u+v) = Au+Av\n"
                f"  1. u+v = {vector('a_u_mas_v')}\n"
                f"  2. A(u+v) = {vector('a_A_por_u_mas_v')}\n"
                f"  3. Au = {vector('a_Au')}; Av = {vector('a_Av')}\n"
                f"  4. Au+Av = {vector('a_Au_mas_Av')}\n"
                f"  Comparación: {vector('a_A_por_u_mas_v')} = "
                f"{vector('a_Au_mas_Av')} -> {estado_a}\n\n"
                "B) A(cu) = c(Au)\n"
                f"  1. cu = {vector('b_c_por_u')}\n"
                f"  2. A(cu) = {vector('b_A_por_cu')}\n"
                f"  3. Au = {vector('b_Au')}\n"
                f"  4. c(Au) = {vector('b_c_por_Au')}\n"
                f"  Comparación: {vector('b_A_por_cu')} = "
                f"{vector('b_c_por_Au')} -> {estado_b}\n"
            )
            resumen = (
                f"A(u + v) = Au + Av:  {estado_a.lower()}    ·    "
                f"A(cu) = c(Au):  {estado_b.lower()}"
            )
            reemplazar_texto(self.resultado, texto, resumen)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        """Reinicia a cero la matriz, los vectores, el escalar y el resultado."""
        reiniciar_celdas(self.entradas_A, self.entradas_u, self.entradas_v, [self.entry_c])
        reemplazar_texto(self.resultado, "")
