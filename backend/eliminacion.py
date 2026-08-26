"""
Módulo de eliminación por filas (Gauss)
Implementa el algoritmo de eliminación Gaussiana para resolver sistemas lineales
"""

from backend.matriz import (
    intercambiar_filas, multiplicar_fila, sumar_filas, es_cero, mostrar_matriz
)


def eliminacion_gaussiana(matriz, verbose=True):
    """
    Realiza el proceso de eliminación Gaussiana con pivoteo parcial.
    Transforma la matriz a forma escalonada.
    
    Args:
        matriz: matriz aumentada [A|b]
        verbose: si True, muestra la matriz en cada paso importante
    
    Returns:
        matriz: matriz en forma escalonada
        rango: rango de la matriz de coeficientes
    """
    m = len(matriz)  # número de filas (ecuaciones)
    n = len(matriz[0]) - 1  # número de columnas de coeficientes (variables)
    
    if verbose:
        mostrar_matriz(matriz, "Matriz aumentada inicial")
    
    rango = 0  # contador del rango
    
    # Recorrer cada columna
    for col in range(n):
        # Encontrar el pivote (elemento no nulo con mayor valor absoluto en la columna)
        fila_pivote = -1
        valor_maximo = 0
        
        for fila in range(rango, m):
            if abs(matriz[fila][col]) > valor_maximo:
                valor_maximo = abs(matriz[fila][col])
                fila_pivote = fila
        
        # Si no hay pivote en esta columna, pasar a la siguiente
        if es_cero(valor_maximo):
            continue
        
        # Intercambiar la fila del pivote con la fila actual (si es necesario)
        if fila_pivote != rango:
            intercambiar_filas(matriz, rango, fila_pivote)
            if verbose:
                print(f"  Intercambio: Fila {rango} <--> Fila {fila_pivote}")
        
        # Dividir la fila del pivote por el pivote para obtener 1 en la posición del pivote
        pivote = matriz[rango][col]
        if not es_cero(pivote):
            multiplicar_fila(matriz, rango, 1 / pivote)
            if verbose:
                print(f"  Fila {rango} -> (1/{pivote:.4f}) * Fila {rango}")
        
        # Hacer ceros debajo del pivote
        for fila in range(rango + 1, m):
            factor = matriz[fila][col]
            if not es_cero(factor):
                sumar_filas(matriz, fila, rango, -factor)
                if verbose:
                    print(f"  Fila {fila} -> Fila {fila} + ({-factor:.4f}) * Fila {rango}")
        
        rango += 1
        
        if verbose:
            mostrar_matriz(matriz, f"Paso {col + 1} - Eliminación en columna {col}")
    
    return matriz, rango


def sustitucion_hacia_atras(matriz, rango):
    """
    Realiza la sustitución hacia atrás para obtener la solución.
    Se ejecuta después de la eliminación Gaussiana.
    
    Args:
        matriz: matriz en forma escalonada
        rango: rango de la matriz
    
    Returns:
        tuple: (soluciones, variables_libres)
            - soluciones: diccionario con variable -> valor (None si es libre)
            - variables_libres: lista de índices de variables libres
    """
    m = len(matriz)
    n = len(matriz[0]) - 1
    
    soluciones = {}
    variables_libres = []
    
    # Identificar variables libres (columnas sin pivote)
    for col in range(n):
        es_pivote = False
        for fila in range(rango):
            if not es_cero(matriz[fila][col]) and all(es_cero(matriz[fila][j]) for j in range(col)):
                es_pivote = True
                break
        if not es_pivote:
            variables_libres.append(col)
    
    # Sustituir hacia atrás desde la última fila con pivote
    for fila in range(rango - 1, -1, -1):
        # Encontrar la columna del pivote para esta fila
        col_pivote = -1
        for col in range(n):
            if not es_cero(matriz[fila][col]):
                col_pivote = col
                break
        
        if col_pivote == -1:
            continue
        
        # Calcular el valor de la variable correspondiente
        valor = matriz[fila][n]  # término independiente
        
        for col in range(col_pivote + 1, n):
            if col not in variables_libres:
                valor -= matriz[fila][col] * soluciones.get(col, 0)
        
        soluciones[col_pivote] = valor
    
    # Asignar None a las variables libres
    for var_libre in variables_libres:
        soluciones[var_libre] = None
    
    return soluciones, variables_libres


def resolver_sistema(matriz_aumentada):
    """
    Resuelve un sistema de ecuaciones lineales usando eliminación Gaussiana.
    
    Args:
        matriz_aumentada: la matriz [A|b]
    
    Returns:
        dict con:
            - 'matriz_escalonada': matriz en forma escalonada
            - 'rango': rango de la matriz
            - 'soluciones': diccionario con variables y sus valores
            - 'variables_libres': lista de variables libres (si las hay)
    """
    # Crear una copia para no modificar la original
    matriz_copia = [fila[:] for fila in matriz_aumentada]
    
    # Realizar eliminación Gaussiana
    matriz_escalonada, rango = eliminacion_gaussiana(matriz_copia, verbose=True)
    
    # Realizar sustitución hacia atrás
    soluciones, variables_libres = sustitucion_hacia_atras(matriz_escalonada, rango)
    
    return {
        'matriz_escalonada': matriz_escalonada,
        'rango': rango,
        'soluciones': soluciones,
        'variables_libres': variables_libres
    }
