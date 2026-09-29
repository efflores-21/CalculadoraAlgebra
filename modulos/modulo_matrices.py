"""Ventana del módulo de operaciones con matrices."""

from fractions import Fraction
import customtkinter as ctk

from backend.matriz import _a_fraction, formatear_valor, subindice
from backend.operaciones_matriciales import (
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    resta_matrices,
    suma_matrices,
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
)


def transponer_matriz(A):
    """Intercambia filas y columnas, equivalente a definir (A^T)[i,j]=A[j,i]."""
    if not A or not A[0]:
        raise ValueError("A debe ser una matriz no vacía.")
    columnas = len(A[0])
    if any(len(fila) != columnas for fila in A):
        raise ValueError("A debe ser rectangular.")
    return [[A[i][j] for i in range(len(A))] for j in range(columnas)]


def invertir_matriz(A):
    """
    Calcula A^-1 reduciendo [A|I] a [I|A^-1] por Gauss-Jordan.

    El procedimiento algebraico usa solo operaciones elementales de fila.
    Si no se puede obtener la identidad a la izquierda, A es singular y no
    tiene inversa.
    """
    if not A or not A[0]:
        raise ValueError("A debe ser una matriz no vacía.")
    n = len(A)
    if any(len(fila) != n for fila in A):
        raise ValueError("La inversa solo está definida para matrices cuadradas.")
    aumentada = [
        [_a_fraction(valor) for valor in A[i]]
        + [Fraction(1 if i == j else 0) for j in range(n)]
        for i in range(n)
    ]
    pasos = [("Matriz aumentada inicial [A|I]", [fila[:] for fila in aumentada])]

    for columna in range(n):
        fila_pivote = columna
        while fila_pivote < n and aumentada[fila_pivote][columna] == 0:
            fila_pivote += 1
        if fila_pivote == n:
            raise ValueError("La matriz es singular; su determinante es cero y no tiene inversa.")
        if fila_pivote != columna:
            aumentada[columna], aumentada[fila_pivote] = (
                aumentada[fila_pivote], aumentada[columna]
            )
            pasos.append((
                f"Intercambiar F{columna + 1} y F{fila_pivote + 1}",
                [fila[:] for fila in aumentada],
            ))
        pivote = aumentada[columna][columna]
        aumentada[columna] = [valor / pivote for valor in aumentada[columna]]
        pasos.append((
            f"Dividir F{columna + 1} entre {formatear_valor(pivote)}",
            [fila[:] for fila in aumentada],
        ))
        for fila in range(n):
            if fila == columna:
                continue
            factor = aumentada[fila][columna]
            if factor != 0:
                aumentada[fila] = [
                    aumentada[fila][j] - factor * aumentada[columna][j]
                    for j in range(2 * n)
                ]
                pasos.append((
                    f"F{fila + 1} <- F{fila + 1} - "
                    f"({formatear_valor(factor)})F{columna + 1}",
                    [fila_actual[:] for fila_actual in aumentada],
                ))
    inversa = [fila[n:] for fila in aumentada]
    return inversa, pasos


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
                "[ A ][ B ]  MÓDULO: ÁLGEBRA DE MATRICES\n"
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
            ("A + B", "suma"), ("A − B", "resta"), ("k · A", "escalar"),
            ("A · B", "producto"), ("Aᵀ  traspuesta", "traspuesta"), ("A⁻¹  inversa", "inversa"),
        ]
        for indice, (texto, operacion) in enumerate(operaciones):
            boton_primario(
                acciones, texto, lambda op=operacion: self.calcular(op), height=38
            ).grid(
                row=indice // 3, column=indice % 3, sticky="ew",
                padx=(0 if indice % 3 == 0 else 8, 0), pady=(0, 8),
            )
        boton_secundario(acciones, "Limpiar", self.limpiar, height=36).grid(
            row=2, column=0, columnspan=3, sticky="ew"
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
            else:
                C, pasos = invertir_matriz(A)
                lineas = ["Inversa por Gauss-Jordan: transformar [A|I] en [I|A^-1]."]
                for indice, (descripcion, matriz_paso) in enumerate(pasos, 1):
                    lineas.extend([
                        f"Paso {indice}: {descripcion}",
                        formatear_matriz(matriz_paso),
                    ])
                lineas.extend(["", "A^-1 =", formatear_matriz(C)])
                texto = "\n".join(lineas)
            nombre = {
                "suma": "A + B", "resta": "A − B", "escalar": "k · A",
                "producto": "A · B", "traspuesta": "Aᵀ", "inversa": "A⁻¹",
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
