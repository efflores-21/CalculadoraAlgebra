"""
Módulo de operaciones con matrices
Funciones para manipular, mostrar y operar con matrices
sin usar librerías como NumPy
"""

def crear_matriz_aumentada(m, n, coeficientes, terminos):
    """
    Crea la matriz aumentada [A|b] a partir de los coeficientes y términos independientes.
    
    Args:
        m: número de ecuaciones (filas)
        n: número de variables (columnas)
        coeficientes: lista de listas con los coeficientes de A
        terminos: lista con los términos independientes b
    
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
    Imprime la matriz en formato visual.
    
    Args:
        matriz: lista de listas representando la matriz
        mensaje: mensaje descriptivo a mostrar
    """
    print(f"\n{mensaje}:")
    print("-" * (15 * (len(matriz[0]) if matriz else 0) + 10))
    for fila in matriz:
        fila_formateada = "| "
        for elemento in fila:
            # Mostrar números con 2 decimales
            fila_formateada += f"{elemento:8.2f} "
        fila_formateada += "|"
        print(fila_formateada)
    print("-" * (15 * (len(matriz[0]) if matriz else 0) + 10))


def intercambiar_filas(matriz, i, j):
    """
    Intercambia dos filas de la matriz.
    Operación elemental: Fila_i ↔ Fila_j
    
    Args:
        matriz: lista de listas (matriz aumentada)
        i: índice de la primera fila
        j: índice de la segunda fila
    """
    matriz[i], matriz[j] = matriz[j], matriz[i]


def multiplicar_fila(matriz, i, escalar):
    """
    Multiplica una fila por un escalar no nulo.
    Operación elemental: Fila_i → escalar * Fila_i
    
    Args:
        matriz: lista de listas (matriz aumentada)
        i: índice de la fila
        escalar: número a multiplicar (debe ser != 0)
    """
    if escalar != 0:
        for j in range(len(matriz[i])):
            matriz[i][j] *= escalar


def sumar_filas(matriz, i, j, multiplicador):
    """
    Suma a una fila, otra fila multiplicada por un escalar.
    Operación elemental: Fila_i → Fila_i + multiplicador * Fila_j
    
    Args:
        matriz: lista de listas (matriz aumentada)
        i: índice de la fila a modificar
        j: índice de la fila a sumar
        multiplicador: escalar multiplicador
    """
    for k in range(len(matriz[i])):
        matriz[i][k] += multiplicador * matriz[j][k]


def es_cero(valor, tolerancia=1e-10):
    """
    Verifica si un valor es prácticamente cero (manejo de errores de redondeo).
    
    Args:
        valor: número a verificar
        tolerancia: umbral de tolerancia
    
    Returns:
        True si |valor| < tolerancia, False en caso contrario
    """
    return abs(valor) < tolerancia


def obtener_numero_variables_libres(matriz, rango):
    """
    Calcula el número de variables libres en un sistema.
    variables_libres = número_de_variables - rango
    
    Args:
        matriz: matriz aumentada
        rango: rango de la matriz
    
    Returns:
        número de variables libres
    """
    n = len(matriz[0]) - 1  # número de columnas menos la columna aumentada
    return n - rango
