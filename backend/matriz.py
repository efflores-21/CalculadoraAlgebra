"""
Módulo de operaciones con matrices.
Contiene la representación de una matriz aumentada y funciones auxiliares.
"""

from fractions import Fraction


def _a_fraction(valor):
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, int):
        return Fraction(valor, 1)
    if isinstance(valor, float):
        return Fraction(str(valor))
    if isinstance(valor, str):
        valor = valor.strip()
        if valor == "":
            return Fraction(0, 1)
        return Fraction(valor)
    return Fraction(valor)


class MatrizAumentada:
    """Representa una matriz aumentada [A | b]."""

    def __init__(self, filas):
        self.datos = [[_a_fraction(valor) for valor in fila] for fila in filas]
        self.filas = len(self.datos)
        self.n_variables = len(self.datos[0]) - 1 if self.datos else 0

    def copiar(self):
        return MatrizAumentada([fila[:] for fila in self.datos])

    def intercambiar_filas(self, i, j):
        self.datos[i], self.datos[j] = self.datos[j], self.datos[i]

    def escalar_fila(self, i, escalar):
        escalar = _a_fraction(escalar)
        if escalar == 0:
            return
        self.datos[i] = [valor * escalar for valor in self.datos[i]]

    def sumar_multiplo_fila(self, i, j, multiplicador):
        multiplicador = _a_fraction(multiplicador)
        fila_i = self.datos[i]
        fila_j = self.datos[j]
        for k in range(len(fila_i)):
            fila_i[k] += multiplicador * fila_j[k]

    def mostrar(self, mensaje="Matriz"):
        print(f"\n{mensaje}:")
        for fila in self.datos:
            print("  ".join(formatear_valor(v) for v in fila))

    def __len__(self):
        return len(self.datos)

    def __getitem__(self, index):
        return self.datos[index]

    def __iter__(self):
        return iter(self.datos)


def crear_matriz_aumentada(m, n, coeficientes, terminos):
    """Crea la matriz aumentada [A | b] desde coeficientes y términos independientes."""
    matriz = []
    for i in range(m):
        fila = [_a_fraction(valor) for valor in coeficientes[i]] + [_a_fraction(terminos[i])]
        matriz.append(fila)
    return matriz


def mostrar_matriz(matriz, mensaje="Matriz"):
    print(f"\n{mensaje}:")
    for fila in matriz:
        print("  ".join(formatear_valor(valor) for valor in fila))


def intercambiar_filas(matriz, i, j):
    if i == j:
        return
    matriz[i], matriz[j] = matriz[j], matriz[i]


def multiplicar_fila(matriz, i, escalar):
    escalar = _a_fraction(escalar)
    if escalar == 0:
        return
    for j in range(len(matriz[i])):
        matriz[i][j] = _a_fraction(matriz[i][j]) * escalar


def sumar_filas(matriz, i, j, multiplicador):
    multiplicador = _a_fraction(multiplicador)
    for k in range(len(matriz[i])):
        matriz[i][k] = _a_fraction(matriz[i][k]) + multiplicador * _a_fraction(matriz[j][k])


def es_cero(valor):
    return _a_fraction(valor) == Fraction(0, 1)


def formatear_valor(valor):
    valor = _a_fraction(valor)
    if valor.denominator == 1:
        return str(valor.numerator)
    return f"{valor.numerator}/{valor.denominator}"


def formatear_fila(fila):
    return "[" + " ".join(formatear_valor(v) for v in fila) + "]"
