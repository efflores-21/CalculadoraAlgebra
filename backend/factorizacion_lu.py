"""Factorizacion LU y solucion de sistemas con aritmetica racional exacta."""

from fractions import Fraction

from backend.matriz import _a_fraction
from backend.operaciones_matriciales import _matriz_a_fraction


def factorizar_lu(A):
    """Factoriza A=L*U sin pivoteo y devuelve (L, U), con diagonal de L unitaria."""
    matriz = _matriz_a_fraction(A)
    n = len(matriz)
    if len(matriz[0]) != n:
        raise ValueError("La factorizacion LU requiere una matriz cuadrada.")
    L = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    U = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for k in range(n):
        for j in range(k, n):
            U[k][j] = matriz[k][j] - sum(L[k][s] * U[s][j] for s in range(k))
        if U[k][k] == 0:
            raise ValueError(
                "La matriz requiere pivoteo para factorizarse como A=LU en este orden."
            )
        for i in range(k + 1, n):
            L[i][k] = (matriz[i][k] - sum(L[i][s] * U[s][k] for s in range(k))) / U[k][k]
    return L, U


def resolver_lu(A, b):
    """Resuelve Ax=b mediante Ly=b (adelante) y Ux=y (atras)."""
    L, U = factorizar_lu(A)
    if b is None:
        raise ValueError("El vector b no puede estar vacío.")
    vector = list(b)
    n = len(L)
    if len(vector) != n:
        raise ValueError("El vector b debe tener una entrada por fila de A.")
    vector = [_a_fraction(v) for v in vector]
    y = [Fraction(0) for _ in range(n)]
    for i in range(n):
        y[i] = (vector[i] - sum(L[i][j] * y[j] for j in range(i))) / L[i][i]
    x = [Fraction(0) for _ in range(n)]
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - sum(U[i][j] * x[j] for j in range(i + 1, n))) / U[i][i]
    return L, U, y, x
