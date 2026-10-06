"""Ventana del módulo de operaciones con matrices."""

from fractions import Fraction
import customtkinter as ctk

from backend.matriz import formatear_valor, subindice
from backend.operaciones_matriciales import (
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    resta_matrices,
    suma_matrices,
)
from backend.matrices import (
    determinante_cofactores,
    determinante_triangular,
    invertir_adjunta,
    invertir_gauss_jordan,
    sarrus_3x3,
    transponer_matriz as transponer_matriz_backend,
    verificar_inversa,
    verificar_seis_propiedades,
)
from modulos._comun import (
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    entrada_numero,
    formatear_matriz,
    leer_entero,
    leer_fraccion,
    matriz_en_linea,
    mensaje_error,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
    mostrar_teoremas,
)


def transponer_matriz(A):
    """Conserva el nombre de interfaz y delega la transposición al backend."""
    return transponer_matriz_backend(A)


def invertir_matriz(A):
    """Conserva el nombre previo y delega el cálculo exacto al backend."""
    return invertir_gauss_jordan(A)


class ModuloMatrices(ctk.CTkFrame):
    """Proporciona un panel propio para operaciones matriciales."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A = []
        self.entradas_B = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Construye los controles, tablas y área de resultados del módulo."""
        zonas = crear_estructura(
            self,
            self.on_back,
            numero=4,
            titulo="Operaciones con matrices",
            descripcion="Suma, resta, producto, traspuesta e inversa de matrices.",
            logo=(
                "[ A ][ B ]  MÓDULO III: ÁLGEBRA DE MATRICES\n"
                "[ C ][ D ]  Operaciones, Traspuesta y Matriz Inversa"
            ),
            pasos=[
                "Escribe el tamaño de A y de B (filas × columnas) y pulsa "
                "«Crear tablas».",
                "Llena las matrices. kA, Aᵀ y A⁻¹ solo usan A.",
                "Pulsa la operación. A + B y A − B piden el mismo tamaño; A · B "
                "pide que las columnas de A sean iguales a las filas de B.",
            ],
            clave_teoremas="matrices",
            indicacion="Aquí verás la operación entrada por entrada y la matriz "
                       "resultante. La inversa muestra cada paso de Gauss-Jordan.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido

        controles, self.entries_dim = crear_controles(
            contenido,
            [
                ("am", "Filas de A", "2", 80), ("an", "Columnas de A", "2", 100),
                ("bm", "Filas de B", "2", 80), ("bn", "Columnas de B", "2", 100),
            ],
            self.actualizar_entradas,
            texto_boton=None,
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        extra, entradas = crear_controles(
            contenido,
            [("k", "Escalar k (para kA)", "2", 130, False)],
            self.actualizar_entradas,
            texto_boton="Crear tablas",
        )
        extra.pack(anchor="w", padx=10, pady=(12, 0))
        self.entry_escalar = entradas["k"]

        controles_fila, entradas_fila = crear_controles(
            contenido,
            [("fi", "Fila i (1-based)", "1", 95), ("fj", "Fila j", "2", 80)],
            self.actualizar_entradas,
            texto_boton=None,
        )
        controles_fila.pack(anchor="w", padx=10, pady=(6, 0))
        self.entry_fila_i = entradas_fila["fi"]
        self.entry_fila_j = entradas_fila["fj"]
        self.tipo_fila_var = ctk.StringVar(value="Intercambiar filas")
        ctk.CTkOptionMenu(
            controles_fila,
            variable=self.tipo_fila_var,
            values=["Intercambiar filas", "Sumar múltiplo de fila", "Multiplicar fila por escalar"],
            width=250,
        ).pack(side="left", padx=(8, 0))

        self.tablas = ctk.CTkFrame(contenido, fg_color="transparent")
        self.tablas.pack(anchor="w", fill="x", pady=(8, 0))
        subtitulo(self.tablas, "Matriz A").grid(row=0, column=0, sticky="w", padx=10, pady=(12, 6))
        subtitulo(self.tablas, "Matriz B").grid(row=0, column=1, sticky="w", padx=(28, 10), pady=(12, 6))
        self.scroll_A = ctk.CTkFrame(self.tablas, fg_color="transparent")
        self.scroll_A.grid(row=1, column=0, sticky="nw", padx=6)
        self.scroll_B = ctk.CTkFrame(self.tablas, fg_color="transparent")
        self.scroll_B.grid(row=1, column=1, sticky="nw", padx=(24, 6))

        acciones = zonas.acciones
        acciones.grid_columnconfigure((0, 1, 2), weight=1, uniform="ops")
        operaciones = [
            ("1. Suma", "suma"), ("2. Resta", "resta"), ("3. Escalar", "escalar"),
            ("4. Producto", "producto"), ("5. Transposición", "traspuesta"),
            ("6. Determinante", "determinante"), ("7. Inversa Gauss-Jordan", "inversa"),
            ("8. Inversa adjunta", "adjunta"), ("9. Verificador", "propiedades"),
            ("0. Teoremas clave", "teoremas"),
        ]
        for indice, (texto, operacion) in enumerate(operaciones):
            boton_primario(
                acciones, texto, lambda op=operacion: self.calcular(op), height=38
            ).grid(
                row=indice // 2, column=indice % 2, sticky="ew",
                padx=(0 if indice % 2 == 0 else 8, 0), pady=(0, 8),
            )
        boton_secundario(acciones, "Limpiar", self.limpiar, height=36).grid(
            row=(len(operaciones) + 1) // 2, column=0, columnspan=2, sticky="ew"
        )

    def actualizar_entradas(self):
        """Valida las dimensiones e inicializa las celdas de A y B."""
        try:
            nombres = {
                "am": "Las filas de A", "an": "Las columnas de A",
                "bm": "Las filas de B", "bn": "Las columnas de B",
            }
            dimensiones = {
                clave: leer_entero(entry, nombres[clave])
                for clave, entry in self.entries_dim.items()
            }
        except ValueError as error:
            mensaje_error(error)
            return
        self.entradas_A = self._construir_tabla(
            self.scroll_A, dimensiones["am"], dimensiones["an"]
        )
        self.entradas_B = self._construir_tabla(
            self.scroll_B, dimensiones["bm"], dimensiones["bn"]
        )
        reemplazar_texto(self.resultado, "")

    def _construir_tabla(self, parent, filas, columnas):
        """Crea las entradas de una matriz, equivalente a preparar M_mxn."""
        for widget in parent.winfo_children():
            widget.destroy()
        entradas = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                celda = entrada_numero(parent)
                celda.grid(row=i, column=j, padx=3, pady=3)
                fila.append(celda)
            entradas.append(fila)
        return entradas

    def _leer_matriz(self, entradas, nombre):
        """Lee y convierte las celdas de una matriz a números racionales exactos."""
        return [
            [
                leer_fraccion(celda, f"La entrada ({i + 1},{j + 1}) de {nombre}")
                for j, celda in enumerate(fila)
            ]
            for i, fila in enumerate(entradas)
        ]

    def calcular(self, operacion):
        """Ejecuta la operación seleccionada, equivalente a aplicar su definición matricial."""
        try:
            if operacion == "teoremas":
                mostrar_teoremas(self, "matrices", "Álgebra de Matrices")
                return
            A = self._leer_matriz(self.entradas_A, "A")
            if operacion == "suma":
                B = self._leer_matriz(self.entradas_B, "B")
                C = suma_matrices(A, B)
                texto = "A+B, entrada a entrada:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += (
                            f"c{subindice(i + 1)},{subindice(j + 1)} = {formatear_valor(A[i][j])} + "
                            f"{formatear_valor(B[i][j])} = {formatear_valor(C[i][j])}\n"
                        )
                texto += "\nResultado A+B:\n" + formatear_matriz(C)
            elif operacion == "resta":
                B = self._leer_matriz(self.entradas_B, "B")
                C = resta_matrices(A, B)
                texto = "A-B, entrada a entrada:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += (
                            f"c{subindice(i + 1)},{subindice(j + 1)} = {formatear_valor(A[i][j])} - "
                            f"{formatear_valor(B[i][j])} = {formatear_valor(C[i][j])}\n"
                        )
                texto += "\nResultado A-B:\n" + formatear_matriz(C)
            elif operacion == "escalar":
                k = leer_fraccion(self.entry_escalar, "El escalar k")
                C = multiplicar_escalar_matriz(k, A)
                texto = f"k={formatear_valor(k)}; cada entrada de A se multiplica por k:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += (
                            f"c{subindice(i + 1)},{subindice(j + 1)}: {formatear_valor(k)}*"
                            f"{formatear_valor(A[i][j])}={formatear_valor(C[i][j])}\n"
                        )
                texto += "\nResultado kA:\n" + formatear_matriz(C)
            elif operacion == "producto":
                B = self._leer_matriz(self.entradas_B, "B")
                C = multiplicar_matrices(A, B)
                lineas = ["A·B: cada entrada es el producto punto de fila por columna."]
                for i in range(len(A)):
                    for j in range(len(B[0])):
                        productos = [
                            f"({formatear_valor(A[i][k])}*{formatear_valor(B[k][j])})"
                            for k in range(len(A[0]))
                        ]
                        lineas.append(
                            f"c{subindice(i + 1)},{subindice(j + 1)} = " + " + ".join(productos)
                            + f" = {formatear_valor(C[i][j])}"
                        )
                lineas.extend(["", "Resultado A·B:", formatear_matriz(C)])
                texto = "\n".join(lineas)
            elif operacion == "traspuesta":
                C = transponer_matriz(A)
                texto = (
                    "Traspuesta: las filas de A pasan a ser columnas.\n"
                    "A =\n" + formatear_matriz(A)
                    + "\n\nA^T =\n" + formatear_matriz(C)
                )
            elif operacion in ("inversa", "adjunta"):
                if operacion == "adjunta":
                    C, pasos = invertir_adjunta(A)
                    titulo = "Inversa por matriz adjunta"
                else:
                    C, pasos = invertir_matriz(A)
                    titulo = "Inversa por Gauss-Jordan: transformar [A|I] en [I|A^-1]."
                verificacion, identidad, cumple = verificar_inversa(A, C, multiplicar_matrices)
                if operacion == "adjunta":
                    otra_inversa, _ = invertir_matriz(A)
                else:
                    otra_inversa, _ = invertir_adjunta(A)
                lineas = [titulo]
                for indice, (descripcion, matriz_paso) in enumerate(pasos, 1):
                    lineas.extend([
                        f"Paso {indice}: {descripcion}",
                        formatear_matriz(matriz_paso),
                    ])
                lineas.extend([
                    "", "A^-1 =", formatear_matriz(C),
                    "", "A·A^-1:", formatear_matriz(verificacion),
                    "Matriz identidad esperada:", formatear_matriz(identidad),
                    "A·A^-1 = I: " + ("Se cumple" if cumple else "No se cumple"),
                    "Comparación de métodos: " + ("las inversas coinciden" if C == otra_inversa
                                                   else "las inversas NO coinciden"),
                ])
                texto = "\n".join(lineas)
            elif operacion == "determinante":
                det_cofactores = determinante_cofactores(A)
                det_triangular, pasos = determinante_triangular(A)
                lineas = ["Determinante por expansión de cofactores: " + formatear_valor(det_cofactores)]
                if len(A) == 3:
                    det_sarrus = sarrus_3x3(A)
                    positivos = [A[0][0] * A[1][1] * A[2][2],
                                 A[0][1] * A[1][2] * A[2][0],
                                 A[0][2] * A[1][0] * A[2][1]]
                    negativos = [A[0][2] * A[1][1] * A[2][0],
                                 A[0][1] * A[1][0] * A[2][2],
                                 A[0][0] * A[1][2] * A[2][1]]
                    lineas.extend([
                        "Sarrus: suma de diagonales descendentes = " +
                        formatear_valor(sum(positivos, Fraction(0))),
                        "Sarrus: suma de diagonales ascendentes = " +
                        formatear_valor(sum(negativos, Fraction(0))),
                        "Determinante por Sarrus: " + formatear_valor(det_sarrus),
                        "Sarrus coincide con cofactores: " +
                        ("Se cumple" if det_sarrus == det_cofactores else "No se cumple"),
                    ])
                lineas.append("Reducción a forma triangular:")
                for indice, (descripcion, estado) in enumerate(pasos, 1):
                    lineas.extend([f"Paso {indice}: {descripcion}", formatear_matriz(estado)])
                lineas.extend([
                    "Determinante por triangularización: " + formatear_valor(det_triangular),
                    "Comparación de métodos: " + ("coinciden" if det_cofactores == det_triangular
                                                   else "NO coinciden"),
                ])
                C = [[det_cofactores]]
                texto = "\n".join(lineas)
            elif operacion == "propiedades":
                B = self._leer_matriz(self.entradas_B, "B")
                n = len(A)
                fila_i = leer_entero(self.entry_fila_i, "La fila i", 1, n) - 1
                fila_j = leer_entero(self.entry_fila_j, "La fila j", 1, n) - 1
                datos = verificar_seis_propiedades(
                    A, B, self.tipo_fila_var.get(), fila_i, fila_j,
                    leer_fraccion(self.entry_escalar, "El escalar k"), multiplicar_matrices,
                )
                lineas = []
                for titulo, lado_izquierdo, lado_derecho in datos:
                    if lado_derecho is None:
                        lineas.extend([titulo, ""])
                        for descripcion, estado in lado_izquierdo:
                            lineas.extend([descripcion, formatear_matriz(estado)])
                        continue
                    formato = lambda valor: formatear_matriz(valor) if isinstance(valor, list) else formatear_valor(valor)
                    lineas.extend([
                        titulo, "Lado izquierdo: " + formato(lado_izquierdo),
                        "Lado derecho: " + formato(lado_derecho),
                        "Se cumple" if lado_izquierdo == lado_derecho else "No se cumple", "",
                    ])
                C = A
                texto = "\n".join(lineas)
            nombre = {
                "suma": "A + B", "resta": "A − B", "escalar": "k · A",
                "producto": "A · B", "traspuesta": "Aᵀ", "inversa": "A⁻¹",
                "adjunta": "A⁻¹ por adjunta", "determinante": "det(A)",
                "propiedades": "Verificador de propiedades",
            }[operacion]
            reemplazar_texto(
                self.resultado, texto + "\n", f"{nombre} = {matriz_en_linea(C)}"
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        """Restaura a cero todas las entradas de las matrices y el escalar."""
        reiniciar_celdas(self.entradas_A, self.entradas_B, [self.entry_escalar])
        reemplazar_texto(self.resultado, "")
