"""Interfaz para factorizar A=LU y resolver Ax=b."""

import customtkinter as ctk

from backend.factorizacion_lu import (
    factorizar_lu,
    factorizar_lu_pivoteo,
    resolver_sistema_lu,
)
from backend.operaciones_matriciales import multiplicar_matrices
from modulos._comun import (
    boton_primario, boton_secundario, crear_controles, crear_estructura,
    copiar_entradas_al_portapapeles, copiar_matriz_al_portapapeles,
    entrada_numero, formatear_matriz, formatear_vector, leer_entero,
    leer_fraccion, mensaje_error, pegar_matriz_en_entradas, reemplazar_texto,
    reiniciar_celdas, Selector, subtitulo,
)


class ModuloLU(ctk.CTkFrame):
    """Factoriza matrices y clasifica sistemas compatibles mediante LU."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_A = []
        self.entradas_b = []
        self.ultima_L = None
        self.ultima_U = None
        zonas = crear_estructura(
            self, on_back, numero=6, titulo="Factorización LU",
            descripcion="Factoriza A = LU o PA = LU y resuelve sistemas rectangulares.",
            logo="A = L U\nLy = b  →  Ux = y",
            pasos=[
                "Escribe las dimensiones m y n de A y pulsa «Crear tabla».",
                "Llena A y el vector b (una entrada por fila) para resolver Ax=b.",
                "Elige el método: sin pivoteo o con pivoteo parcial.",
            ], clave_teoremas="lu",
            indicacion="Se muestran intercambios, P, multiplicadores, L, U y la verificación.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido
        controles, entradas = crear_controles(
            contenido,
            [("m", "Filas m", "2", 90), ("n", "Columnas n", "2", 90)],
            self.actualizar_entradas,
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_m = entradas["m"]
        self.entry_n = entradas["n"]
        etiqueta_metodo = ctk.CTkLabel(
            contenido, text="Método de factorización", anchor="w"
        )
        etiqueta_metodo.pack(anchor="w", padx=10, pady=(12, 2))
        self.selector_pivoteo = Selector(
            contenido, ["Sin pivoteo", "Pivoteo parcial (PA = LU)"], "Sin pivoteo"
        )
        self.selector_pivoteo.pack(anchor="w", padx=10)
        subtitulo(contenido, "Matriz A y vector b").pack(
            anchor="w", padx=10, pady=(18, 6)
        )
        self.tabla = ctk.CTkFrame(contenido, fg_color="transparent")
        self.tabla.pack(anchor="w", padx=6)
        portapapeles = ctk.CTkFrame(contenido, fg_color="transparent")
        portapapeles.pack(anchor="w", padx=10, pady=(8, 0))
        for texto, callback, ancho in (
            ("Copiar A", self.copiar_A, 90), ("Pegar en A", self.pegar_A, 100),
            ("Copiar L", self.copiar_L, 90), ("Copiar U", self.copiar_U, 90),
        ):
            boton_secundario(portapapeles, texto, callback, width=ancho).pack(
                side="left", padx=(0, 5)
            )
        boton_primario(
            zonas.acciones, "Factorizar", self.calcular
        ).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(
            zonas.acciones, "Resolver Ax = b", self.resolver_sistema, width=130, height=40
        ).pack(side="left", padx=(0, 8))
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(side="left")
        self.actualizar_entradas()

    def actualizar_entradas(self):
        try:
            m = leer_entero(self.entry_m, "La cantidad de filas m")
            n = leer_entero(self.entry_n, "La cantidad de columnas n")
        except ValueError as error:
            mensaje_error(error)
            return
        for widget in self.tabla.winfo_children():
            widget.destroy()
        self.entradas_A, self.entradas_b = [], []
        self.ultima_L = None
        self.ultima_U = None
        for i in range(m):
            fila = []
            for j in range(n):
                campo = entrada_numero(self.tabla)
                campo.grid(row=i, column=j, padx=3, pady=3)
                fila.append(campo)
            self.entradas_A.append(fila)
            b = entrada_numero(self.tabla)
            b.grid(row=i, column=n, padx=(14, 3), pady=3)
            self.entradas_b.append(b)
        reemplazar_texto(self.resultado, "")

    def calcular(self, resolver=False):
        """Factoriza A; opcionalmente clasifica y resuelve Ax=b mediante LU."""
        self.ultima_L = None
        self.ultima_U = None
        try:
            A = [[leer_fraccion(c, f"La entrada ({i + 1},{j + 1}) de A")
                  for j, c in enumerate(fila)] for i, fila in enumerate(self.entradas_A)]
            pasos = []
            pivoteo_parcial = self.selector_pivoteo.get() == "Pivoteo parcial (PA = LU)"
            if resolver:
                b = [leer_fraccion(c, f"La entrada {i + 1} de b")
                     for i, c in enumerate(self.entradas_b)]
                sistema = resolver_sistema_lu(
                    A, b, registrar_paso=pasos.append,
                    pivoteo_parcial=pivoteo_parcial,
                )
                P, L, U, y = sistema["P"], sistema["L"], sistema["U"], sistema["y"]
                x = sistema["solucion_particular"]
            else:
                if pivoteo_parcial:
                    P, L, U = factorizar_lu_pivoteo(A, registrar_paso=pasos.append)
                else:
                    P = None
                    L, U = factorizar_lu(A, registrar_paso=pasos.append)
            self.ultima_L, self.ultima_U = L, U
            producto_lu = multiplicar_matrices(L, U)
            matriz_verificacion = (
                multiplicar_matrices(P, A) if P is not None else A
            )
            lineas = [
                "Factorización P·A = L·U con pivoteo parcial"
                if pivoteo_parcial else "Factorización A = L·U sin pivoteo",
                "Matriz original A:", formatear_matriz(A),
                "\nConstrucción de U y registro de multiplicadores en L:",
            ]
            if pivoteo_parcial:
                lineas.extend(["Matriz de permutación P:", formatear_matriz(P)])
            if resolver:
                lineas.append("Vector b = " + formatear_vector(b))
            for indice, paso in enumerate(pasos, 1):
                lineas.append(f"Paso {indice}: {paso['descripcion']}")
                if paso["mostrar_matrices"]:
                    lineas.extend([
                        "L =", formatear_matriz(paso["L"]),
                        "U =", formatear_matriz(paso["U"]),
                    ])
                    if "P" in paso:
                        lineas.extend(["P =", formatear_matriz(paso["P"])])
                if "vector" in paso:
                    nombre, valores = paso["vector"]
                    lineas.append(f"{nombre} parcial = {formatear_vector(valores)}")
            lineas.extend([
                "\nVerificación P·A = L·U:" if pivoteo_parcial
                else "\nVerificación LU = A:",
                "LU =", formatear_matriz(producto_lu),
                "P·A =" if pivoteo_parcial else "A =",
                formatear_matriz(matriz_verificacion),
                ("P·A = LU: " if pivoteo_parcial else "LU = A: ")
                + ("Se cumple" if producto_lu == matriz_verificacion else "No se cumple"),
            ])
            if resolver:
                lineas.extend([
                    "\nSustitución hacia adelante Ly = Pb:" if pivoteo_parcial
                    else "\nSustitución hacia adelante Ly = b:",
                    "y = " + formatear_vector(y),
                ])
                if sistema["estado"] == "incompatible":
                    lineas.extend([
                        "\nClasificación: sistema incompatible (no tiene solución).",
                        "Eliminación hacia atrás encontró una fila cero igual a un valor no nulo.",
                    ])
                else:
                    lineas.extend([
                        "\nSustitución hacia atrás Ux = y:",
                        ("x = " if sistema["estado"] == "unica" else "x₀ = ")
                        + formatear_vector(x),
                    ])
                    if sistema["estado"] == "unica":
                        lineas.append("Clasificación: solución única.")
                    else:
                        lineas.append(
                            f"Clasificación: infinitas soluciones; variables libres: "
                            + ", ".join(f"x{j + 1}" for j in sistema["columnas_libres"])
                            + "."
                        )
                        lineas.append("Familia: x = x₀ + " + " + ".join(
                            f"t{indice}·v{indice} ({formatear_vector(base)})"
                            for indice, base in enumerate(sistema["bases_nucleo"], 1)
                        ))
                        for indice, base in enumerate(sistema["bases_nucleo"], 1):
                            producto_base = [
                                sum(A[i][j] * base[j] for j in range(len(base)))
                                for i in range(len(A))
                            ]
                            lineas.append(
                                f"A v{indice} = {formatear_vector(producto_base)}; "
                                "verificación homogénea exacta: "
                                + ("se cumple." if sistema["verificaciones_bases"][indice - 1]
                                   else "no se cumple.")
                            )
                    lineas.extend([
                        "Ax₀ = " + formatear_vector(
                            [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]
                        ),
                        "b = " + formatear_vector(b),
                        "Verificación exacta Ax₀ = b: "
                        + ("se cumple." if sistema["verificacion"] else "no se cumple."),
                    ])
            elif len(A) != len(A[0]):
                lineas.append(
                    "A es rectangular: L tiene m filas y m columnas; U tiene m filas y n columnas."
                )
            reemplazar_texto(
                self.resultado,
                "\n".join(lineas) + "\n",
                ("Sistema incompatible" if sistema["estado"] == "incompatible" else
                 ("Solución única: x = " + formatear_vector(x))
                 if sistema["estado"] == "unica" else "Sistema con infinitas soluciones")
                if resolver
                else ("Factorización PA = LU completada" if pivoteo_parcial
                      else "Factorización LU completada"),
            )
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def resolver_sistema(self):
        """Clasifica y resuelve Ax=b con factorización LU."""
        self.calcular(resolver=True)

    def copiar_A(self):
        copiar_entradas_al_portapapeles(self, self.entradas_A)

    def pegar_A(self):
        pegar_matriz_en_entradas(self, self.entradas_A)

    def copiar_L(self):
        copiar_matriz_al_portapapeles(self, self.ultima_L)

    def copiar_U(self):
        copiar_matriz_al_portapapeles(self, self.ultima_U)

    def limpiar(self):
        reiniciar_celdas(self.entradas_A, self.entradas_b)
        self.ultima_L = None
        self.ultima_U = None
        reemplazar_texto(self.resultado, "")
