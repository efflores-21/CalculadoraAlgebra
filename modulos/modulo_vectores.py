"""Panel del Módulo 3: independencia lineal de vectores."""

from fractions import Fraction
import customtkinter as ctk

from backend.eliminacion import eliminacion_con_pasos
from backend.matriz import subindice
from modulos._comun import (
    boton_primario,
    boton_secundario,
    crear_controles,
    crear_estructura,
    entrada_numero,
    etiqueta,
    formatear_matriz,
    leer_entero,
    leer_fraccion,
    mensaje_error,
    reemplazar_texto,
    reiniciar_celdas,
    subtitulo,
)


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
            libres = k - len(pivotes)

            lineas = [
                "VEREDICTO: LOS VECTORES SON "
                + ("L.I." if independiente else "L.D."),
                f"En R^{n}: k={k}, pivotes={len(pivotes)}, variables libres={libres}.",
                "",
                "Matriz de columnas A:",
                formatear_matriz(matriz),
                "Sistema homogéneo: A*c=0.",
                "Forma reducida [R|0]:",
                formatear_matriz(reducida),
                "",
                "Pasos principales de Gauss-Jordan:",
            ]
            operaciones = pasos[1:]
            if operaciones:
                for indice, paso in enumerate(operaciones, 1):
                    lineas.append(f"  {indice}) {paso['descripcion']}")
            else:
                lineas.append("  No se requieren operaciones de fila.")
            if k > n:
                lineas.append(f"Como k={k} > n={n}, el conjunto es dependiente.")
            if independiente:
                lineas.append("A*c=0 solo tiene la solución trivial c=0.")
            else:
                lineas.append("Hay una variable libre y existe una solución no trivial.")
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
