"""
Módulo de operaciones con matrices
Funciones para manipular, mostrar y operar con matrices
sin usar librerías como NumPy.
Ahora utiliza Fraction para exactitud.
"""

from fractions import Fraction


def crear_matriz_aumentada(m, n, coeficientes, terminos):
    """
    Crea la matriz aumentada [A|b] a partir de los coeficientes y términos independientes.
    Args:
        m: número de ecuaciones (filas)
        n: número de variables (columnas)
        coeficientes: lista de listas con los coeficientes de A (Fraction)
        terminos: lista con los términos independientes b (Fraction)
    Returns:
        matriz_aumentada: lista de listas representando [A|b]
    """
    matriz_aumentada = []
    for i in range(m):
        fila = coeficientes[i][:] + [terminos[i]]
        matriz_aumentada.append(fila)
    return matriz_aumentada


def mostrar_matriz(matriz, mensaje="Matriz"):
    """
    Imprime la matriz en formato visual (para consola, pero se puede reutilizar en GUI).
    """
    print(f"\n{mensaje}:")
    for fila in matriz:
        print("  ".join(f"{str(elem):>10}" for elem in fila))


def intercambiar_filas(matriz, i, j):
    """
    Intercambia dos filas de la matriz.
    Operación elemental: Fila_i ↔ Fila_j
    """
    matriz[i], matriz[j] = matriz[j], matriz[i]


def multiplicar_fila(matriz, i, escalar):
    """
    Multiplica una fila por un escalar no nulo.
    Operación elemental: Fila_i → escalar * Fila_i
    """
    if escalar != 0:
        for j in range(len(matriz[i])):
            matriz[i][j] *= escalar


def sumar_filas(matriz, i, j, multiplicador):
    """
    Suma a una fila, otra fila multiplicada por un escalar.
    Operación elemental: Fila_i → Fila_i + multiplicador * Fila_j
    """
    for k in range(len(matriz[i])):
        matriz[i][k] += multiplicador * matriz[j][k]


def es_cero(valor):
    """
    Verifica si un valor es exactamente cero (usando Fraction).
    """
    return valor == Fraction(0, 1)