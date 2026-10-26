"""
Pantalla del módulo de independencia lineal (L.I. / L.D.).

Unidad I, Vectores e independencia lineal [P4].
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

from fractions import Fraction
import customtkinter as ctk

from backend.eliminacion import eliminacion_con_pasos, solucion_general
from backend.matriz import formatear_valor, subindice
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


def _texto_pasos_independencia(pasos, cantidad_variables):
    """Presenta cada operación registrada de Gauss-Jordan y sus estados."""
    if not pasos:
        return []
    anterior = pasos[0]["matriz"]
    lineas = ["Estado inicial de [A|0]:", formatear_matriz(anterior)]
    for indice, paso in enumerate(pasos[1:], 1):
        estado = paso["matriz"]
        descripcion = paso["descripcion"]
        lineas.extend([f"Paso {indice}: {descripcion}", "Antes:", formatear_matriz(anterior)])
        if descripcion.startswith("Intercambio F"):
            filas = descripcion.removeprefix("Intercambio F").split(" ↔ F")
            lineas.append(
                f"Se intercambian las filas completas de [A|0] para colocar un pivote no nulo "
                f"(F{filas[0]} ↔ F{filas[1]}). La operación es reversible y conserva las soluciones."
            )
        elif descripcion.startswith("Normalizar F"):
            fila = int(descripcion.split("F", 1)[1].split()[0]) - 1
            columna = next(j for j in range(cantidad_variables) if anterior[fila][j] != 0)
            pivote = anterior[fila][columna]
            calculos = "; ".join(
                f"{formatear_valor(anterior[fila][j])}/{formatear_valor(pivote)}="
                f"{formatear_valor(estado[fila][j])}"
                for j in range(len(estado[fila]))
            )
            lineas.extend([
                f"Pivote a{fila + 1},{columna + 1} = {formatear_valor(pivote)}. "
                "Se divide toda la fila por este valor no nulo para convertirlo en 1; "
                "las soluciones no cambian.",
                "Cálculo de la fila completa: " + calculos + ".",
            ])
        elif " ← " in descripcion:
            izquierda, operacion = descripcion.split(" ← ")
            fila_objetivo = int(izquierda[1:]) - 1
            fila_pivote = int(operacion.split("·F")[1]) - 1
            columna = next(j for j in range(cantidad_variables) if anterior[fila_pivote][j] != 0)
            pivote = anterior[fila_pivote][columna]
            factor = anterior[fila_objetivo][columna] / pivote
            calculos = "; ".join(
                f"{formatear_valor(anterior[fila_objetivo][j])} - "
                f"({formatear_valor(factor)})({formatear_valor(anterior[fila_pivote][j])})="
                f"{formatear_valor(estado[fila_objetivo][j])}"
                for j in range(len(estado[fila_objetivo]))
            )
            lineas.extend([
                f"Pivote a{fila_pivote + 1},{columna + 1} = {formatear_valor(pivote)}; "
                f"se elimina la entrada de F{fila_objetivo + 1}.",
                "Restar un múltiplo de una fila a otra es reversible y conserva el sistema homogéneo.",
                "Cálculo de la fila completa: " + calculos + ".",
            ])
        lineas.extend(["Después:", formatear_matriz(estado)])
        anterior = estado
    return lineas


def _solucion_no_trivial(datos, cantidad_vectores):
    """Elige una solución del homogéneo fijando una variable libre en 1."""
    libres = datos["variables_libres"]
    if not libres:
        return [Fraction(0) for _ in range(cantidad_vectores)]
    parametros = {columna: Fraction(0) for columna in libres}
    parametros[libres[0]] = Fraction(1)
    coeficientes = []
    for columna in range(cantidad_vectores):
        constante, terminos = datos["soluciones_generales"][columna]
        valor = constante + sum(
            (coeficiente * parametros.get(libre, Fraction(0))
             for libre, coeficiente in terminos.items()),
            Fraction(0),
        )
        coeficientes.append(valor)
    return coeficientes


def _texto_relacion_dependencia(vectores, coeficientes):
    """Muestra una relación no trivial y comprueba cada componente de su suma."""
    lineas = ["Una solución no trivial de A·c=0 produce esta relación:"]
    lineas.append(
        " + ".join(
            f"({formatear_valor(c)})·v{subindice(i + 1)}"
            for i, c in enumerate(coeficientes) if c != 0
        ) + " = 0"
    )
    escalados = []
    for i, (coeficiente, vector) in enumerate(zip(coeficientes, vectores), 1):
        escalado = [coeficiente * componente for componente in vector]
        escalados.append(escalado)
        lineas.append(
            f"({formatear_valor(coeficiente)})·v{subindice(i)} = "
            + formatear_vector(escalado)
        )
    suma = [
        sum((vector[i] for vector in escalados), Fraction(0))
        for i in range(len(vectores[0]))
    ]
    lineas.extend(
        f"Componente {i + 1}: "
        + " + ".join(formatear_valor(vector[i]) for vector in escalados)
        + f" = {formatear_valor(suma[i])}."
        for i in range(len(suma))
    )
    coincide_con_cero = all(componente == 0 for componente in suma)
    lineas.append(
        f"La suma es {formatear_vector(suma)}; "
        + ("coincide con el vector cero, por eso los vectores son dependientes."
           if coincide_con_cero else
           "no coincide con el vector cero; revisa la relación antes de concluir dependencia.")
    )
    return lineas


class ModuloVectores(ctk.CTkFrame):
    """Panel para estudiar independencia lineal sin abrir otra ventana."""

    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.entradas_vectores = []
        self._construir_interfaz()
        self.actualizar_entradas()

    def _construir_interfaz(self):
        """Construye la interfaz del módulo y su flujo de entrada y resultado."""
        zonas = crear_estructura(
            self,
            self.on_back,
            numero=3,
            titulo="Independencia lineal",
            descripcion="Decide si un conjunto de vectores es L.I. o L.D.",
            logo=(
                "  v1  v2  vk   MÓDULO: VECTORES E INDEPENDENCIA LINEAL\n"
                "  |   |   |    Combinaciones Lineales, L.I. y L.D.\n"
                "  [ A ] c = 0  Ax = 0"
            ),
            pasos=[
                "Escribe cuántos vectores tienes y cuántos componentes tiene "
                "cada uno, y pulsa «Crear tabla».",
                "Cada columna es un vector: escribe sus componentes de arriba "
                "hacia abajo.",
                "Pulsa «Analizar» para saber si son independientes (L.I.) "
                "o dependientes (L.D.).",
            ],
            clave_teoremas="vectores",
            indicacion="Aquí verás el veredicto L.I. o L.D., la matriz reducida, "
                       "los pivotes y las variables libres.",
        )
        self.resultado = zonas.resultado
        contenido = zonas.contenido

        controles, entradas = crear_controles(
            contenido,
            [("k", "Cantidad de vectores", "2", 130), ("n", "Componentes", "2", 100)],
            self.actualizar_entradas,
        )
        controles.pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_k, self.entry_n = entradas["k"], entradas["n"]

        subtitulo(contenido, "Tus vectores").pack(anchor="w", padx=10, pady=(20, 6))
        self.marco_entradas = ctk.CTkFrame(contenido, fg_color="transparent")
        self.marco_entradas.pack(anchor="w", padx=6)

        boton_primario(zonas.acciones, "Analizar", self.analizar).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        boton_secundario(zonas.acciones, "Limpiar", self.limpiar, width=100, height=40).pack(
            side="left"
        )

    def actualizar_entradas(self):
        """Lee k y n y construye campos para k vectores con n componentes."""
        try:
            k = leer_entero(self.entry_k, "La cantidad k")
            n = leer_entero(self.entry_n, "La dimensión n")
        except ValueError as error:
            mensaje_error(error)
            return

        for widget in self.marco_entradas.winfo_children():
            widget.destroy()
        self.entradas_vectores = [[] for _ in range(k)]
        for j in range(k):
            etiqueta(self.marco_entradas, f"v{subindice(j + 1)}", color="texto", negrita=True).grid(
                row=0, column=j, pady=(0, 2)
            )
        for i in range(n):
            for j in range(k):
                entry = entrada_numero(self.marco_entradas)
                entry.grid(row=i + 1, column=j, padx=3, pady=3)
                self.entradas_vectores[j].append(entry)
        reemplazar_texto(self.resultado, "")

    def leer_datos(self):
        """Lee los vectores de la tabla, equivalente a definir elementos de R^n."""
        if not self.entradas_vectores:
            raise ValueError("Primero aplica dimensiones válidas.")
        vectores = []
        for j, entradas in enumerate(self.entradas_vectores):
            vectores.append([
                leer_fraccion(entry, f"El componente {i + 1} del vector v{subindice(j + 1)}")
                for i, entry in enumerate(entradas)
            ])
        return vectores

    def construir_matriz_columnas(self, vectores):
        """Forma A con los vectores como columnas: A[i,j] es componente i de vj."""
        dimension = len(vectores[0])
        return [
            [vectores[j][i] for j in range(len(vectores))]
            for i in range(dimension)
        ]

    def construir_sistema_homogeneo(self, matriz_columnas):
        """Construye [A|0], equivalente a resolver A*c=0 para independencia."""
        return [fila[:] + [Fraction(0, 1)] for fila in matriz_columnas]

    def eliminar_gauss_jordan(self, matriz_aumentada):
        """Reduce [A|0] con operaciones elementales, equivalente a resolver el homogéneo."""
        matriz_reducida, rango, pasos = eliminacion_con_pasos(
            matriz_aumentada, metodo="gauss-jordan", verbose=False
        )
        return matriz_reducida, rango, pasos

    def contar_pivotes(self, matriz_reducida, cantidad_vectores):
        """Cuenta columnas pivote, equivalente al rango de la matriz de columnas."""
        pivotes = []
        for fila in matriz_reducida:
            for columna in range(cantidad_vectores):
                if fila[columna] != 0:
                    pivotes.append(columna)
                    break
        return pivotes

    def determinar_veredicto(self, n, k, pivotes):
        """Decide L.I. si cada vector aporta pivote; en otro caso, decide L.D."""
        if k > n:
            return False
        return len(pivotes) == k

    def analizar(self):
        """Construye y resuelve A*c=0, mostrando reducción, rango y veredicto."""
        try:
            # Se usa el tamaño de la tabla visible, aunque los campos cambien.
            vectores = self.leer_datos()
            k = len(vectores)
            n = len(vectores[0])
            matriz = self.construir_matriz_columnas(vectores)
            aumentada = self.construir_sistema_homogeneo(matriz)
            reducida, rango, pasos = self.eliminar_gauss_jordan(aumentada)
            pivotes = self.contar_pivotes(reducida, k)
            independiente = self.determinar_veredicto(n, k, pivotes)
            soluciones_generales, variables_libres, _ = solucion_general(reducida, rango)
            libres = len(variables_libres)

            lineas = [
                "VEREDICTO: LOS VECTORES SON "
                + ("L.I." if independiente else "L.D."),
                f"En R^{n}: k={k}, pivotes={len(pivotes)}, variables libres={libres}.",
                "",
                "Vectores analizados:",
                *[
                    f"v{subindice(j + 1)} = {formatear_vector(vector)} (dimensión {n})."
                    for j, vector in enumerate(vectores)
                ],
                "",
                "Matriz de columnas A:",
                formatear_matriz(matriz),
                "Para probar independencia se plantea c₁·v₁ + … + cₖ·vₖ = 0, "
                "equivalentemente el sistema homogéneo A·c=0. Las columnas de A son los vectores y la última "
                "columna de [A|0] contiene el término homogéneo cero.",
                "",
                "Reducción de [A|0] por Gauss-Jordan:",
            ]
            lineas.extend(_texto_pasos_independencia(pasos, k))
            lineas.extend([
                "Forma reducida final [R|0]:",
                formatear_matriz(reducida),
                f"Rango(A) = {rango}; hay {libres} variable(s) libre(s) entre los coeficientes.",
            ])
            if k > n:
                lineas.append(
                    f"Como hay k={k} vectores en R^{n} y k>n, el conjunto necesariamente es dependiente."
                )
            if independiente:
                lineas.append(
                    "La reducción muestra pivote en cada columna de coeficientes: "
                    "A·c=0 solo admite c₁=…=cₖ=0. Por definición, son linealmente independientes."
                )
            else:
                coeficientes_no_triviales = _solucion_no_trivial({
                    "variables_libres": variables_libres,
                    "soluciones_generales": soluciones_generales,
                }, k)
                lineas.extend([
                    "Al menos una columna de coeficientes no tiene pivote y queda libre; "
                    "asignarle un valor no nulo produce una solución no trivial.",
                    "Coeficientes elegidos: " + ", ".join(
                        f"c{subindice(j + 1)}={formatear_valor(valor)}"
                        for j, valor in enumerate(coeficientes_no_triviales)
                    ) + ".",
                    *_texto_relacion_dependencia(vectores, coeficientes_no_triviales),
                ])
            resumen = (
                "Linealmente independientes (L.I.)" if independiente
                else "Linealmente dependientes (L.D.)"
            ) + f"   ·   {len(pivotes)} pivote(s) de {k} vector(es)"
            reemplazar_texto(self.resultado, "\n".join(lineas) + "\n", resumen)
        except (ValueError, ZeroDivisionError) as error:
            mensaje_error(error)

    def limpiar(self):
        """Reinicia todas las componentes ingresadas a cero y limpia el resultado."""
        reiniciar_celdas(self.entradas_vectores)
        reemplazar_texto(self.resultado, "")
