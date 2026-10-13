"""Panel de ejercicios interactivos sobre propiedades de matrices."""

from fractions import Fraction

import customtkinter as ctk

from backend.matriz import formatear_valor
from backend.propiedades import verificar_propiedades
from backend.eliminacion import eliminacion_con_pasos
from backend.matrices import determinante_triangular, invertir_gauss_jordan
from backend.operaciones_matriciales import (
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    suma_matrices,
    transponer_matriz,
)
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


TEOREMAS_TRANSPOSICION = (
    "(Aᵀ)ᵀ = A",
    "(A + B)ᵀ = Aᵀ + Bᵀ",
    "(cA)ᵀ = cAᵀ",
    "(AB)ᵀ = BᵀAᵀ",
)

TEOREMAS_INVERSA_DETERMINANTE = (
    "(A⁻¹)⁻¹ = A",
    "(AB)⁻¹ = B⁻¹A⁻¹",
    "(Aᵀ)⁻¹ = (A⁻¹)ᵀ",
    "det(Aᵀ) = det(A)",
    "det(AB) = det(A)det(B)",
    "det(A⁻¹) = 1/det(A)",
)

TEOREMAS_PRODUCTO = (
    "Asociatividad: A(BC) = (AB)C",
    "Distributividad izquierda: A(B+C) = AB+AC",
    "Distributividad derecha: (A+B)C = AC+BC",
    "Identidad: AI = IA = A",
    "No conmutatividad: comparar AB y BA",
    "Cancelación: comprobar AB = AC con B ≠ C",
    "Producto nulo: AB = 0 no implica A = 0 o B = 0",
)


def calcular_teorema_producto(teorema, A, B=None, C=None):
    """Calcula los pasos y la conclusión de un ejercicio de producto matricial."""
    pasos = []

    def producto(nombre, izquierda, derecha):
        try:
            resultado = multiplicar_matrices(izquierda, derecha)
        except ValueError as error:
            raise ValueError(f"No se puede calcular {nombre}: {error}") from error
        pasos.append((nombre, resultado))
        return resultado

    def suma(nombre, izquierda, derecha):
        try:
            resultado = suma_matrices(izquierda, derecha)
        except ValueError as error:
            raise ValueError(f"No se puede calcular {nombre}: {error}") from error
        pasos.append((nombre, resultado))
        return resultado

    if teorema == TEOREMAS_PRODUCTO[0]:
        if B is None or C is None:
            raise ValueError("Ingrese las matrices B y C para verificar asociatividad.")
        bc = producto("BC", B, C)
        izquierda = producto("A(BC)", A, bc)
        ab = producto("AB", A, B)
        derecha = producto("(AB)C", ab, C)
        nombre_izq, nombre_der = "A(BC)", "(AB)C"
        coincide = izquierda == derecha
        conclusion = "La multiplicación es asociativa para estas matrices."
    elif teorema == TEOREMAS_PRODUCTO[1]:
        if B is None or C is None:
            raise ValueError("Ingrese las matrices B y C para verificar distributividad.")
        suma_bc = suma("B + C", B, C)
        izquierda = producto("A(B+C)", A, suma_bc)
        ab = producto("AB", A, B)
        ac = producto("AC", A, C)
        derecha = suma("AB + AC", ab, ac)
        nombre_izq, nombre_der = "A(B+C)", "AB+AC"
        coincide = izquierda == derecha
        conclusion = "Se cumple la distributividad a la izquierda." if coincide else "No coincide la igualdad."
    elif teorema == TEOREMAS_PRODUCTO[2]:
        if B is None or C is None:
            raise ValueError("Ingrese las matrices A, B y C para verificar distributividad.")
        suma_ab = suma("A + B", A, B)
        izquierda = producto("(A+B)C", suma_ab, C)
        ac = producto("AC", A, C)
        bc = producto("BC", B, C)
        derecha = suma("AC + BC", ac, bc)
        nombre_izq, nombre_der = "(A+B)C", "AC+BC"
        coincide = izquierda == derecha
        conclusion = "Se cumple la distributividad a la derecha." if coincide else "No coincide la igualdad."
    elif teorema == TEOREMAS_PRODUCTO[3]:
        filas, columnas = len(A), len(A[0])
        identidad_filas = [[Fraction(int(i == j)) for j in range(filas)] for i in range(filas)]
        identidad_columnas = [
            [Fraction(int(i == j)) for j in range(columnas)]
            for i in range(columnas)
        ]
        izquierda = producto("AI", A, identidad_columnas)
        derecha = producto("IA", identidad_filas, A)
        nombre_izq, nombre_der = "AI", "IA"
        coincide = izquierda == A and derecha == A
        pasos.append(("A", A))
        conclusion = "AI = IA = A se cumple." if coincide else "No coinciden todos los productos con A."
    elif teorema == TEOREMAS_PRODUCTO[4]:
        if B is None:
            raise ValueError("Ingrese la matriz B para comparar AB y BA.")
        if len(A) != len(A[0]) or len(B) != len(B[0]) or len(A) != len(B):
            raise ValueError(
                "Para comparar AB con BA, A y B deben ser cuadradas del mismo orden; "
                "así ambos productos tienen las mismas dimensiones."
            )
        izquierda = producto("AB", A, B)
        derecha = producto("BA", B, A)
        nombre_izq, nombre_der = "AB", "BA"
        coincide = izquierda != derecha
        conclusion = (
            "Este ejemplo muestra que AB ≠ BA."
            if coincide else "Estas matrices conmutan; cargue otro ejemplo para mostrar AB ≠ BA."
        )
    elif teorema == TEOREMAS_PRODUCTO[5]:
        if B is None or C is None:
            raise ValueError("Ingrese las matrices B y C para comprobar la cancelación.")
        izquierda = producto("AB", A, B)
        derecha = producto("AC", A, C)
        nombre_izq, nombre_der = "AB", "AC"
        b_distinta_c = B != C
        coincide = izquierda == derecha and b_distinta_c
        pasos.append(("B", B))
        pasos.append(("C", C))
        conclusion = (
            "Contraejemplo: AB = AC, pero B ≠ C; no se puede cancelar A en general."
            if coincide else
            ("AB = AC, pero B = C; cambie B o C para obtener un contraejemplo."
             if izquierda == derecha else
             "AB ≠ AC; estos datos no forman un contraejemplo de cancelación.")
        )
    elif teorema == TEOREMAS_PRODUCTO[6]:
        if B is None:
            raise ValueError("Ingrese la matriz B para comprobar el producto nulo.")
        izquierda = producto("AB", A, B)
        derecha = [
            [Fraction(0) for _ in range(len(izquierda[0]))]
            for _ in range(len(izquierda))
        ]
        a_no_nula = any(valor != 0 for fila in A for valor in fila)
        b_no_nula = any(valor != 0 for fila in B for valor in fila)
        coincide = izquierda == derecha and a_no_nula and b_no_nula
        nombre_izq, nombre_der = "AB", "0"
        pasos.extend([("A", A), ("B", B)])
        conclusion = (
            "Contraejemplo confirmado: AB = 0 aunque A ≠ 0 y B ≠ 0."
            if coincide else
            "Estos datos no muestran el contraejemplo: se requiere AB = 0 y A, B no nulas."
        )
    else:
        raise ValueError("Seleccione una propiedad del producto válida.")

    return pasos, nombre_izq, izquierda, nombre_der, derecha, coincide, conclusion


def analizar_criterios_invertibilidad(A):
    """Evalúa determinante, pivotes y dependencia usando eliminación exacta."""
    if not A or any(len(fila) != len(A) for fila in A):
        raise ValueError("Los criterios de invertibilidad requieren una matriz cuadrada no vacía.")
    determinante, pasos_determinante = determinante_triangular(A)
    n = len(A)
    aumentada = [list(fila) + [Fraction(0)] for fila in A]
    escalonada, rango, pasos_eliminacion = eliminacion_con_pasos(
        aumentada, metodo="gauss"
    )
    columnas_pivote = [
        next(columna + 1 for columna in range(n) if fila[columna] != 0)
        for fila in escalonada
        if any(fila[columna] != 0 for columna in range(n))
    ]
    determinante_no_nulo = determinante != 0
    pivote_en_cada_columna = rango == n
    columnas_independientes = pivote_en_cada_columna
    inversa = None
    pasos_inversa = []
    producto_a_inversa = None
    producto_inversa_a = None
    if determinante_no_nulo:
        inversa, pasos_inversa = invertir_gauss_jordan(A)
        identidad = [
            [Fraction(int(i == j)) for j in range(n)] for i in range(n)
        ]
        producto_a_inversa = multiplicar_matrices(A, inversa)
        producto_inversa_a = multiplicar_matrices(inversa, A)
        inversa_derecha = producto_a_inversa == identidad
        inversa_izquierda = producto_inversa_a == identidad
    else:
        inversa_izquierda = inversa_derecha = False
    solucion_unica_para_todo_b = pivote_en_cada_columna
    transformacion_inyectiva = columnas_independientes
    transformacion_sobreyectiva = rango == n
    return {
        "determinante": determinante,
        "pasos_determinante": pasos_determinante,
        "pasos_eliminacion": pasos_eliminacion,
        "matriz_escalonada": escalonada,
        "rango": rango,
        "columnas_pivote": columnas_pivote,
        "determinante_no_nulo": determinante_no_nulo,
        "pivote_en_cada_columna": pivote_en_cada_columna,
        "columnas_independientes": columnas_independientes,
        "solucion_unica_para_todo_b": solucion_unica_para_todo_b,
        "transformacion_inyectiva": transformacion_inyectiva,
        "transformacion_sobreyectiva": transformacion_sobreyectiva,
        "inversa_izquierda": inversa_izquierda,
        "inversa_derecha": inversa_derecha,
        "inversa": inversa,
        "pasos_inversa": pasos_inversa,
        "producto_a_inversa": producto_a_inversa,
        "producto_inversa_a": producto_inversa_a,
        "invertible": (
            determinante_no_nulo
            and pivote_en_cada_columna
            and solucion_unica_para_todo_b
            and transformacion_inyectiva
            and transformacion_sobreyectiva
            and inversa_izquierda
            and inversa_derecha
        ),
    }


def calcular_teorema_transposicion(teorema, A, B=None, c=None):
    """Calcula ambos lados de una identidad de transposición y sus pasos."""
    pasos = []
    if teorema == TEOREMAS_TRANSPOSICION[0]:
        transpuesta = transponer_matriz(A)
        izquierda = transponer_matriz(transpuesta)
        derecha = A
        pasos.extend([("Aᵀ", transpuesta), ("(Aᵀ)ᵀ", izquierda)])
        lado_izquierdo, lado_derecho = "(Aᵀ)ᵀ", "A"
    elif teorema == TEOREMAS_TRANSPOSICION[1]:
        suma = suma_matrices(A, B)
        izquierda = transponer_matriz(suma)
        transpuesta_a = transponer_matriz(A)
        transpuesta_b = transponer_matriz(B)
        derecha = suma_matrices(transpuesta_a, transpuesta_b)
        pasos.extend([("A + B", suma), ("(A + B)ᵀ", izquierda),
                      ("Aᵀ", transpuesta_a), ("Bᵀ", transpuesta_b),
                      ("Aᵀ + Bᵀ", derecha)])
        lado_izquierdo, lado_derecho = "(A + B)ᵀ", "Aᵀ + Bᵀ"
    elif teorema == TEOREMAS_TRANSPOSICION[2]:
        escalada = multiplicar_escalar_matriz(c, A)
        izquierda = transponer_matriz(escalada)
        transpuesta = transponer_matriz(A)
        derecha = multiplicar_escalar_matriz(c, transpuesta)
        pasos.extend([("cA", escalada), ("(cA)ᵀ", izquierda),
                      ("Aᵀ", transpuesta), ("cAᵀ", derecha)])
        lado_izquierdo, lado_derecho = "(cA)ᵀ", "cAᵀ"
    elif teorema == TEOREMAS_TRANSPOSICION[3]:
        producto = multiplicar_matrices(A, B)
        izquierda = transponer_matriz(producto)
        transpuesta_b = transponer_matriz(B)
        transpuesta_a = transponer_matriz(A)
        derecha = multiplicar_matrices(transpuesta_b, transpuesta_a)
        pasos.extend([("AB", producto), ("(AB)ᵀ", izquierda),
                      ("Bᵀ", transpuesta_b), ("Aᵀ", transpuesta_a),
                      ("BᵀAᵀ", derecha)])
        lado_izquierdo, lado_derecho = "(AB)ᵀ", "BᵀAᵀ"
    else:
        raise ValueError("Seleccione un teorema de transposición válido.")
    return pasos, lado_izquierdo, izquierda, lado_derecho, derecha, izquierda == derecha


def calcular_teorema_inversa_determinante(teorema, A, B=None):
    """Evalúa una identidad de inversas o determinantes y devuelve su traza."""
    pasos = []

    def determinante(nombre, matriz):
        valor, traza = determinante_triangular(matriz)
        pasos.extend((f"{nombre}: {descripcion}", estado) for descripcion, estado in traza)
        return valor

    def exigir_invertible(nombre, matriz):
        valor = determinante(nombre, matriz)
        if valor == 0:
            raise ValueError(f"{nombre} es singular (det={formatear_valor(valor)}); no tiene inversa.")
        return valor

    def inversa(nombre, matriz):
        resultado, traza = invertir_gauss_jordan(matriz)
        pasos.extend((f"{nombre}: {descripcion}", estado) for descripcion, estado in traza)
        return resultado

    if teorema == TEOREMAS_INVERSA_DETERMINANTE[0]:
        exigir_invertible("A", A)
        inversa_a = inversa("A⁻¹", A)
        izquierda = inversa("(A⁻¹)⁻¹", inversa_a)
        derecha = A
        nombre_izq, nombre_der = "(A⁻¹)⁻¹", "A"
    elif teorema == TEOREMAS_INVERSA_DETERMINANTE[1]:
        if not B:
            raise ValueError("Ingrese la matriz B.")
        if len(A) != len(B):
            raise ValueError(
                "Para (AB)⁻¹, A y B deben ser cuadradas del mismo orden."
            )
        exigir_invertible("A", A)
        exigir_invertible("B", B)
        producto = multiplicar_matrices(A, B)
        izquierda = inversa("(AB)⁻¹", producto)
        inversa_b = inversa("B⁻¹", B)
        inversa_a = inversa("A⁻¹", A)
        derecha = multiplicar_matrices(inversa_b, inversa_a)
        pasos.append(("B⁻¹A⁻¹", derecha))
        nombre_izq, nombre_der = "(AB)⁻¹", "B⁻¹A⁻¹"
    elif teorema == TEOREMAS_INVERSA_DETERMINANTE[2]:
        exigir_invertible("A", A)
        transpuesta = transponer_matriz(A)
        izquierda = inversa("(Aᵀ)⁻¹", transpuesta)
        inversa_a = inversa("A⁻¹", A)
        derecha = transponer_matriz(inversa_a)
        pasos.append(("(A⁻¹)ᵀ", derecha))
        nombre_izq, nombre_der = "(Aᵀ)⁻¹", "(A⁻¹)ᵀ"
    elif teorema == TEOREMAS_INVERSA_DETERMINANTE[3]:
        determinante_a = determinante("A", A)
        transpuesta = transponer_matriz(A)
        determinante_at = determinante("Aᵀ", transpuesta)
        izquierda, derecha = determinante_at, determinante_a
        pasos.append(("Comparación det(Aᵀ) = det(A)", None))
        nombre_izq, nombre_der = "det(Aᵀ)", "det(A)"
    elif teorema == TEOREMAS_INVERSA_DETERMINANTE[4]:
        if not B:
            raise ValueError("Ingrese la matriz B.")
        determinante_a = determinante("A", A)
        determinante_b = determinante("B", B)
        producto = multiplicar_matrices(A, B)
        determinante_ab = determinante("AB", producto)
        izquierda = determinante_ab
        derecha = determinante_a * determinante_b
        pasos.append((
            f"det(A)det(B) = {formatear_valor(determinante_a)} × "
            f"{formatear_valor(determinante_b)} = {formatear_valor(derecha)}",
            None,
        ))
        nombre_izq, nombre_der = "det(AB)", "det(A)det(B)"
    elif teorema == TEOREMAS_INVERSA_DETERMINANTE[5]:
        determinante_a = exigir_invertible("A", A)
        inversa_a = inversa("A⁻¹", A)
        izquierda = determinante("A⁻¹", inversa_a)
        derecha = Fraction(1, 1) / determinante_a
        pasos.append((
            f"1/det(A) = 1/{formatear_valor(determinante_a)} = "
            f"{formatear_valor(derecha)}",
            None,
        ))
        nombre_izq, nombre_der = "det(A⁻¹)", "1/det(A)"
    else:
        raise ValueError("Seleccione un teorema de inversas o determinantes válido.")

    return pasos, nombre_izq, izquierda, nombre_der, derecha, izquierda == derecha


class ModuloPropiedades(ctk.CTkFrame):
    """Presenta propiedades de producto, transposición, inversas y determinantes."""

    def __init__(self, master, on_back):
        """Inicializa el panel con una matriz 2x2 y vectores de dimensión 2."""
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A = []
        self.entradas_u = []
        self.entradas_v = []
        self.entradas_A_transposicion = []
        self.entradas_B_transposicion = []
        self.entradas_producto = {"A": [], "B": [], "C": []}
        self.entradas_invertibilidad = []
        self._construir_interfaz()
        self.actualizar_entradas()
        self._actualizar_matrices_transposicion()
        self._actualizar_matrices_producto()
        self._actualizar_matriz_invertibilidad()

    def _construir_interfaz(self):
        """Construye los controles para A,u,v,c y el área de pasos."""
        zonas = crear_estructura(
            self,
            self.on_back,
            numero=7,
            titulo="Propiedades de matrices",
            descripcion="Comprueba linealidad, transposición, inversas y determinantes.",
            logo=(
                " A · B   MÓDULO: PROPIEDADES DE MATRICES\n"
                "         A(u + v) = Au + Av\n"
                "         (AB)ᵀ = BᵀAᵀ\n"
                "         det(AB) = det(A)det(B)"
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

        subtitulo(contenido, "Teoremas de transposición").pack(
            anchor="w", padx=10, pady=(24, 6)
        )
        self.teorema_transposicion_var = ctk.StringVar(value=TEOREMAS_TRANSPOSICION[0])
        ctk.CTkOptionMenu(
            contenido,
            variable=self.teorema_transposicion_var,
            values=list(TEOREMAS_TRANSPOSICION),
            width=260,
        ).pack(anchor="w", padx=10, pady=(0, 8))
        controles_transposicion, entradas_transposicion = crear_controles(
            contenido,
            [("at_m", "Filas A", "2", 76), ("at_n", "Columnas A", "2", 90),
             ("bt_m", "Filas B", "2", 76), ("bt_n", "Columnas B", "2", 90),
             ("at_c", "Escalar c", "2", 76, False)],
            self._actualizar_matrices_transposicion,
            texto_boton="Crear matrices",
        )
        controles_transposicion.pack(anchor="w", padx=10, pady=(0, 8))
        self.entries_dim_transposicion = entradas_transposicion
        self.panel_matrices_transposicion = ctk.CTkFrame(
            contenido, fg_color="transparent"
        )
        self.panel_matrices_transposicion.pack(anchor="w", fill="x")
        boton_primario(
            contenido, "Verificar transposición", self.verificar_transposicion, width=250
        ).pack(anchor="w", padx=10, pady=(8, 0))

        subtitulo(contenido, "Teoremas de inversas y determinantes").pack(
            anchor="w", padx=10, pady=(24, 6)
        )
        self.teorema_inversa_determinante_var = ctk.StringVar(
            value=TEOREMAS_INVERSA_DETERMINANTE[0]
        )
        ctk.CTkOptionMenu(
            contenido,
            variable=self.teorema_inversa_determinante_var,
            values=list(TEOREMAS_INVERSA_DETERMINANTE),
            width=300,
        ).pack(anchor="w", padx=10, pady=(0, 8))
        etiqueta(
            contenido,
            "Usa las matrices A y B ingresadas arriba; A y B deben ser cuadradas "
            "cuando la igualdad lo requiera.",
            tamano=12,
        ).pack(anchor="w", padx=10, pady=(0, 8))
        boton_primario(
            contenido,
            "Verificar inversa/determinante",
            self.verificar_inversa_determinante,
            width=270,
        ).pack(anchor="w", padx=10, pady=(0, 8))

        subtitulo(contenido, "Propiedades del producto de matrices").pack(
            anchor="w", padx=10, pady=(24, 6)
        )
        self.teorema_producto_var = ctk.StringVar(value=TEOREMAS_PRODUCTO[0])
        ctk.CTkOptionMenu(
            contenido,
            variable=self.teorema_producto_var,
            values=list(TEOREMAS_PRODUCTO),
            width=370,
        ).pack(anchor="w", padx=10, pady=(0, 8))
        etiqueta(
            contenido,
            "Define las dimensiones de A, B y C; las compatibilidades se validan al calcular.",
            tamano=12,
        ).pack(anchor="w", padx=10, pady=(0, 6))
        controles_producto, entradas_producto = crear_controles(
            contenido,
            [("pa_m", "A filas", "2", 68), ("pa_n", "A cols", "2", 68),
             ("pb_m", "B filas", "2", 68), ("pb_n", "B cols", "2", 68),
             ("pc_m", "C filas", "2", 68), ("pc_n", "C cols", "2", 68)],
            self._actualizar_matrices_producto,
            texto_boton="Crear matrices",
        )
        controles_producto.pack(anchor="w", padx=10, pady=(0, 8))
        self.entries_dim_producto = entradas_producto
        self.panel_matrices_producto = ctk.CTkFrame(
            contenido, fg_color="transparent"
        )
        self.panel_matrices_producto.pack(anchor="w", fill="x")
        acciones_producto = ctk.CTkFrame(contenido, fg_color="transparent")
        acciones_producto.pack(anchor="w", padx=10, pady=(8, 0))
        boton_secundario(
            acciones_producto, "Ejemplo AB ≠ BA", self.cargar_ejemplo_no_conmutativo,
            width=150,
        ).pack(side="left", padx=(0, 6))
        boton_secundario(
            acciones_producto, "Ejemplo de cancelación", self.cargar_ejemplo_cancelacion,
            width=180,
        ).pack(side="left", padx=(0, 6))
        boton_secundario(
            acciones_producto, "Ejemplo AB = 0", self.cargar_ejemplo_producto_nulo,
            width=130,
        ).pack(side="left", padx=(0, 6))
        boton_primario(
            acciones_producto, "Verificar producto", self.verificar_producto, width=175
        ).pack(side="left")

        subtitulo(contenido, "Criterios de invertibilidad").pack(
            anchor="w", padx=10, pady=(24, 6)
        )
        etiqueta(
            contenido,
            "Para una matriz cuadrada: det(A) ≠ 0, pivote en cada columna y columnas independientes.",
            tamano=12,
        ).pack(anchor="w", padx=10, pady=(0, 6))
        controles_invertibilidad, entradas_invertibilidad = crear_controles(
            contenido,
            [("inv_n", "Orden n", "2", 80)],
            self._actualizar_matriz_invertibilidad,
            texto_boton="Crear matriz",
        )
        controles_invertibilidad.pack(anchor="w", padx=10, pady=(0, 8))
        self.entry_orden_invertibilidad = entradas_invertibilidad["inv_n"]
        self.panel_invertibilidad = ctk.CTkFrame(
            contenido, fg_color="transparent"
        )
        self.panel_invertibilidad.pack(anchor="w", fill="x")
        boton_primario(
            contenido, "Analizar criterios", self.verificar_invertibilidad, width=220
        ).pack(anchor="w", padx=10, pady=(8, 0))

        boton_primario(zonas.acciones, "Verificar propiedades", self.verificar).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(
            side="left"
        )

    def _actualizar_matrices_transposicion(self):
        """Construye A y B con las dimensiones seleccionadas para el teorema."""
        try:
            dimensiones = {
                clave: leer_entero(entrada, etiqueta_dim)
                for clave, entrada, etiqueta_dim in (
                    ("at_m", self.entries_dim_transposicion["at_m"], "Las filas de A"),
                    ("at_n", self.entries_dim_transposicion["at_n"], "Las columnas de A"),
                    ("bt_m", self.entries_dim_transposicion["bt_m"], "Las filas de B"),
                    ("bt_n", self.entries_dim_transposicion["bt_n"], "Las columnas de B"),
                )
            }
        except (ValueError, AttributeError, KeyError) as error:
            if isinstance(error, ValueError):
                mensaje_error(error)
            return
        for widget in self.panel_matrices_transposicion.winfo_children():
            widget.destroy()
        panel_a = ctk.CTkFrame(self.panel_matrices_transposicion, fg_color="transparent")
        panel_b = ctk.CTkFrame(self.panel_matrices_transposicion, fg_color="transparent")
        panel_a.pack(side="left", anchor="nw", padx=4)
        panel_b.pack(side="left", anchor="nw", padx=12)
        subtitulo(panel_a, f"Matriz A ({dimensiones['at_m']} × {dimensiones['at_n']})").pack(
            anchor="w", padx=4, pady=(8, 4)
        )
        subtitulo(panel_b, f"Matriz B ({dimensiones['bt_m']} × {dimensiones['bt_n']})").pack(
            anchor="w", padx=4, pady=(8, 4)
        )
        self.entradas_A_transposicion = self._crear_matriz(
            panel_a, dimensiones["at_m"], dimensiones["at_n"]
        )
        self.entradas_B_transposicion = self._crear_matriz(
            panel_b, dimensiones["bt_m"], dimensiones["bt_n"]
        )

    def _actualizar_matrices_producto(self):
        """Construye las matrices A, B y C con sus dimensiones independientes."""
        try:
            dimensiones = {
                clave: leer_entero(entrada, nombre)
                for clave, entrada, nombre in (
                    ("pa_m", self.entries_dim_producto["pa_m"], "Filas de A"),
                    ("pa_n", self.entries_dim_producto["pa_n"], "Columnas de A"),
                    ("pb_m", self.entries_dim_producto["pb_m"], "Filas de B"),
                    ("pb_n", self.entries_dim_producto["pb_n"], "Columnas de B"),
                    ("pc_m", self.entries_dim_producto["pc_m"], "Filas de C"),
                    ("pc_n", self.entries_dim_producto["pc_n"], "Columnas de C"),
                )
            }
        except (ValueError, AttributeError, KeyError) as error:
            if isinstance(error, ValueError):
                mensaje_error(error)
            return
        for widget in self.panel_matrices_producto.winfo_children():
            widget.destroy()
        for nombre, fila_clave, columna_clave in (
            ("A", "pa_m", "pa_n"), ("B", "pb_m", "pb_n"),
            ("C", "pc_m", "pc_n"),
        ):
            panel = ctk.CTkFrame(self.panel_matrices_producto, fg_color="transparent")
            panel.pack(anchor="w", padx=8, pady=(3, 5))
            filas, columnas = dimensiones[fila_clave], dimensiones[columna_clave]
            subtitulo(panel, f"Matriz {nombre} ({filas} × {columnas})").pack(
                anchor="w", padx=4, pady=(4, 2)
            )
            self.entradas_producto[nombre] = self._crear_matriz(
                panel, filas, columnas
            )

    def _cargar_matrices_ejemplo(self, teorema, matrices):
        """Ajusta las dimensiones a 2×2 y carga un ejemplo editable."""
        self.teorema_producto_var.set(teorema)
        for entrada in self.entries_dim_producto.values():
            entrada.delete(0, "end")
            entrada.insert(0, "2")
        self._actualizar_matrices_producto()
        for nombre, valores in matrices.items():
            for fila_entradas, fila_valores in zip(
                self.entradas_producto[nombre], valores
            ):
                for celda, valor in zip(fila_entradas, fila_valores):
                    celda.delete(0, "end")
                    celda.insert(0, str(valor))

    def cargar_ejemplo_no_conmutativo(self):
        """Carga matrices 2×2 con AB distinto de BA."""
        self._cargar_matrices_ejemplo(
            TEOREMAS_PRODUCTO[4],
            {"A": [[1, 1], [0, 1]], "B": [[1, 0], [1, 1]]},
        )

    def cargar_ejemplo_cancelacion(self):
        """Carga AB=AC con B distinto de C para mostrar el fallo de cancelación."""
        self._cargar_matrices_ejemplo(
            TEOREMAS_PRODUCTO[5],
            {
                "A": [[1, 0], [0, 0]],
                "B": [[1, 0], [0, 1]],
                "C": [[1, 0], [2, 0]],
            },
        )

    def cargar_ejemplo_producto_nulo(self):
        """Carga A y B no nulas cuyo producto es la matriz cero."""
        self._cargar_matrices_ejemplo(
            TEOREMAS_PRODUCTO[6],
            {
                "A": [[1, 0], [0, 0]],
                "B": [[0, 0], [1, 0]],
            },
        )

    def verificar_producto(self):
        """Muestra pasos, ambos lados y conclusión para la propiedad elegida."""
        try:
            teorema = self.teorema_producto_var.get()
            if teorema == TEOREMAS_PRODUCTO[3]:
                necesarios = ("A",)
            elif teorema in (TEOREMAS_PRODUCTO[4], TEOREMAS_PRODUCTO[6]):
                necesarios = ("A", "B")
            else:
                necesarios = ("A", "B", "C")
            matrices = {
                nombre: self._leer_matriz_transposicion(
                    self.entradas_producto[nombre], nombre
                )
                for nombre in necesarios
            }
            pasos, nombre_izq, izquierda, nombre_der, derecha, coincide, conclusion = (
                calcular_teorema_producto(
                    teorema, matrices["A"], matrices.get("B"), matrices.get("C")
                )
            )
            lineas = [f"Verificación: {teorema}", "Matrices de entrada:"]
            for nombre in necesarios:
                lineas.extend([f"{nombre} =", formatear_matriz(matrices[nombre])])
            lineas.append("Operaciones intermedias:")
            for descripcion, resultado in pasos:
                lineas.extend([f"{descripcion} =", formatear_matriz(resultado), ""])
            lineas.extend([
                f"Lado izquierdo: {nombre_izq} =", formatear_matriz(izquierda),
                f"Lado derecho: {nombre_der} =", formatear_matriz(derecha),
                "Criterio del ejercicio: " + ("confirmado" if coincide else "no confirmado"),
                "Conclusión: " + conclusion,
            ])
            reemplazar_texto(self.resultado, "\n".join(lineas))
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def _actualizar_matriz_invertibilidad(self):
        """Crea una cuadrícula cuadrada para el análisis de invertibilidad."""
        try:
            orden = leer_entero(self.entry_orden_invertibilidad, "El orden de A")
        except (ValueError, AttributeError) as error:
            if isinstance(error, ValueError):
                mensaje_error(error)
            return
        for widget in self.panel_invertibilidad.winfo_children():
            widget.destroy()
        subtitulo(self.panel_invertibilidad, f"Matriz A ({orden} × {orden})").pack(
            anchor="w", padx=8, pady=(4, 3)
        )
        self.entradas_invertibilidad = self._crear_matriz(
            self.panel_invertibilidad, orden, orden
        )

    def verificar_invertibilidad(self):
        """Muestra los pasos y la conclusión de los tres criterios equivalentes."""
        try:
            A = self._leer_matriz_transposicion(
                self.entradas_invertibilidad, "A"
            )
            datos = analizar_criterios_invertibilidad(A)
            n = len(A)
            pivotes = set(datos["columnas_pivote"])
            sin_pivote = [columna for columna in range(1, n + 1) if columna not in pivotes]
            lineas = [
                "Criterios de invertibilidad para A:",
                formatear_matriz(A),
                "\nCálculo del determinante por triangularización:",
            ]
            for indice, (descripcion, estado) in enumerate(
                datos["pasos_determinante"], 1
            ):
                lineas.extend([f"Paso {indice}: {descripcion}", formatear_matriz(estado)])
            lineas.append(
                "\nLocalización de pivotes mediante reducción de [A|0] "
                "(la última columna es cero):"
            )
            for indice, paso in enumerate(datos["pasos_eliminacion"], 1):
                lineas.extend([
                    f"Paso {indice}: {paso['descripcion']}",
                    formatear_matriz(paso["matriz"]),
                ])
            columnas_texto = ", ".join(map(str, datos["columnas_pivote"])) or "ninguna"
            lineas.extend([
                "\nResultados de los criterios:",
                f"det(A) = {formatear_valor(datos['determinante'])}; "
                + ("det(A) ≠ 0" if datos["determinante_no_nulo"] else "det(A) = 0"),
                f"Columnas pivote: {columnas_texto} "
                f"({datos['rango']} de {n}).",
                "Hay pivote en cada columna: "
                + ("Sí" if datos["pivote_en_cada_columna"] else "No"),
                "Columnas linealmente independientes: "
                + ("Sí, porque hay un pivote en cada columna."
                   if datos["columnas_independientes"]
                   else "No, porque falta un pivote y las columnas son dependientes."),
            ])
            if sin_pivote:
                lineas.append(
                    "Columnas sin pivote: " + ", ".join(map(str, sin_pivote)) + "."
                )
            estado_si_no = lambda condicion: "Sí" if condicion else "No"
            lineas.extend([
                "Solución única de Ax=b para todo b: "
                + estado_si_no(datos["solucion_unica_para_todo_b"])
                + ("; cada columna tiene pivote, así Ax=b tiene solución única para todo b."
                   if datos["solucion_unica_para_todo_b"]
                   else "; falta un pivote, por lo que no se cumple para todo b."),
                "Transformación x ↦ Ax inyectiva: "
                + estado_si_no(datos["transformacion_inyectiva"])
                + ("; el núcleo contiene solo al vector cero."
                   if datos["transformacion_inyectiva"]
                   else "; existe una variable libre en Ax=0."),
                "Transformación x ↦ Ax sobreyectiva en Rⁿ: "
                + estado_si_no(datos["transformacion_sobreyectiva"])
                + ("; las columnas de A generan Rⁿ."
                   if datos["transformacion_sobreyectiva"]
                   else "; las columnas de A no generan todo Rⁿ."),
                "Existe inversa izquierda C con CA=I: "
                + estado_si_no(datos["inversa_izquierda"]),
                "Existe inversa derecha D con AD=I: "
                + estado_si_no(datos["inversa_derecha"]),
            ])
            if datos["inversa"] is not None:
                lineas.append("\nCálculo de A⁻¹ por Gauss-Jordan:")
                for indice, (descripcion, estado) in enumerate(datos["pasos_inversa"], 1):
                    lineas.extend([
                        f"Paso {indice}: {descripcion}", formatear_matriz(estado)
                    ])
                lineas.extend([
                    "A⁻¹ =", formatear_matriz(datos["inversa"]),
                    "A·A⁻¹ =", formatear_matriz(datos["producto_a_inversa"]),
                    "A⁻¹·A =", formatear_matriz(datos["producto_inversa_a"]),
                    "Ambas verificaciones dan I: "
                    + ("Sí" if datos["inversa_izquierda"] and datos["inversa_derecha"] else "No"),
                ])
            lineas.extend([
                "\nConclusión: A "
                + ("es invertible; los criterios equivalentes se cumplen."
                   if datos["invertible"]
                   else "es singular; falla al menos uno de los criterios de invertibilidad."),
            ])
            reemplazar_texto(
                self.resultado,
                "\n".join(lineas),
                "A es invertible" if datos["invertible"] else "A es singular",
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    @staticmethod
    def _crear_matriz(parent, filas, columnas):
        """Crea una cuadrícula de entradas para una matriz."""
        tabla = ctk.CTkFrame(parent, fg_color="transparent")
        tabla.pack(anchor="w")
        entradas = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                celda = entrada_numero(tabla)
                celda.grid(row=i, column=j, padx=3, pady=3)
                fila.append(celda)
            entradas.append(fila)
        return entradas

    @staticmethod
    def _leer_matriz_transposicion(entradas, nombre):
        return [
            [leer_fraccion(celda, f"Una entrada de {nombre}") for celda in fila]
            for fila in entradas
        ]

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
                """Escribe como (a, b, …) el vector guardado con esa clave."""
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

    def verificar_transposicion(self):
        """Calcula y compara los dos lados del teorema seleccionado."""
        try:
            teorema = self.teorema_transposicion_var.get()
            A = self._leer_matriz_transposicion(self.entradas_A_transposicion, "A")
            B = None
            if teorema in (TEOREMAS_TRANSPOSICION[1], TEOREMAS_TRANSPOSICION[3]):
                B = self._leer_matriz_transposicion(self.entradas_B_transposicion, "B")
            c = None
            if teorema == TEOREMAS_TRANSPOSICION[2]:
                c = leer_fraccion(self.entries_dim_transposicion["at_c"], "El escalar c")
            pasos, nombre_izq, lado_izq, nombre_der, lado_der, coincide = (
                calcular_teorema_transposicion(teorema, A, B, c)
            )
            lineas = [f"Verificación: {teorema}", "Matriz A:", formatear_matriz(A)]
            if B is not None:
                lineas.extend(["Matriz B:", formatear_matriz(B)])
            if c is not None:
                lineas.append(f"Escalar c = {formatear_valor(c)}")
            lineas.append("Operaciones intermedias:")
            for descripcion, matriz in pasos:
                lineas.extend([f"{descripcion} =", formatear_matriz(matriz), ""])
            lineas.extend([
                f"Lado izquierdo: {nombre_izq} =", formatear_matriz(lado_izq),
                f"Lado derecho: {nombre_der} =", formatear_matriz(lado_der),
                "Coinciden: " + ("SÍ" if coincide else "NO"),
            ])
            reemplazar_texto(
                self.resultado,
                "\n".join(lineas),
                f"{nombre_izq} = {nombre_der}: {'se cumple' if coincide else 'no se cumple'}",
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def verificar_inversa_determinante(self):
        """Calcula los dos lados y presenta las trazas del teorema elegido."""
        try:
            teorema = self.teorema_inversa_determinante_var.get()
            A = self._leer_matriz_transposicion(self.entradas_A_transposicion, "A")
            B = None
            if teorema in (
                TEOREMAS_INVERSA_DETERMINANTE[1],
                TEOREMAS_INVERSA_DETERMINANTE[4],
            ):
                B = self._leer_matriz_transposicion(self.entradas_B_transposicion, "B")
            pasos, nombre_izq, lado_izq, nombre_der, lado_der, coincide = (
                calcular_teorema_inversa_determinante(teorema, A, B)
            )
            lineas = [f"Verificación: {teorema}", "Matriz A:", formatear_matriz(A)]
            if B is not None:
                lineas.extend(["Matriz B:", formatear_matriz(B)])
            lineas.append("Operaciones intermedias:")
            for descripcion, estado in pasos:
                lineas.append(descripcion)
                if estado is not None:
                    lineas.append(formatear_matriz(estado))
                lineas.append("")
            formato_lado = lambda valor: (
                formatear_matriz(valor) if isinstance(valor, list)
                else formatear_valor(valor)
            )
            lineas.extend([
                f"Lado izquierdo: {nombre_izq} =", formato_lado(lado_izq),
                f"Lado derecho: {nombre_der} =", formato_lado(lado_der),
                "Coinciden: " + ("SÍ" if coincide else "NO"),
            ])
            reemplazar_texto(
                self.resultado,
                "\n".join(lineas),
                f"{nombre_izq} = {nombre_der}: {'se cumple' if coincide else 'no se cumple'}",
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        """Reinicia a cero la matriz, los vectores, el escalar y el resultado."""
        reiniciar_celdas(self.entradas_A, self.entradas_u, self.entradas_v, [self.entry_c])
        reiniciar_celdas(
            self.entradas_A_transposicion,
            self.entradas_B_transposicion,
            [self.entries_dim_transposicion["at_c"]],
        )
        reemplazar_texto(self.resultado, "")
