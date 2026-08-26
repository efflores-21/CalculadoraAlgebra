"""
Módulo de clasificación de sistemas lineales
Clasifica el sistema según el tipo de solución que presenta
"""

from backend.matriz import es_cero


def clasificar_sistema(matriz_escalonada, rango):
    """
    Clasifica el sistema como:
    - Consistente Determinado: una solución única
    - Consistente Indeterminado: infinitas soluciones
    - Inconsistente: sin solución
    
    Args:
        matriz_escalonada: matriz en forma escalonada
        rango: rango de la matriz de coeficientes
    
    Returns:
        dict con:
            - 'tipo': tipo de sistema
            - 'descripcion': descripción detallada
    """
    m = len(matriz_escalonada)  # número de filas
    n = len(matriz_escalonada[0]) - 1  # número de variables
    
    # Verificar si existe una fila inconsistente: [0 0 ... 0 | k] con k ≠ 0
    for fila in range(rango, m):
        # Verificar si la fila tiene todos ceros en la parte de coeficientes
        todos_ceros = all(es_cero(matriz_escalonada[fila][j]) for j in range(n))
        
        # Si tiene todos ceros pero término independiente ≠ 0, es inconsistente
        if todos_ceros and not es_cero(matriz_escalonada[fila][n]):
            return {
                'tipo': 'Inconsistente',
                'descripcion': 'El sistema NO tiene solución (inconsistente).',
                'variables_libres': 0,
                'fila_inconsistente': fila
            }
    
    # Calcular número de variables libres
    numero_variables_libres = n - rango
    
    if numero_variables_libres == 0:
        return {
            'tipo': 'Consistente Determinado',
            'descripcion': 'El sistema tiene SOLUCIÓN ÚNICA.',
            'variables_libres': 0
        }
    else:
        return {
            'tipo': 'Consistente Indeterminado',
            'descripcion': f'El sistema tiene INFINITAS SOLUCIONES con {numero_variables_libres} variable(s) libre(s).',
            'variables_libres': numero_variables_libres
        }


def mostrar_clasificacion(clasificacion):
    """
    Muestra la clasificación del sistema de manera clara.
    
    Args:
        clasificacion: diccionario con la clasificación
    """
    print("\n" + "="*70)
    print("CLASIFICACIÓN DEL SISTEMA")
    print("="*70)
    print(f"Tipo: {clasificacion['tipo']}")
    print(f"Descripción: {clasificacion['descripcion']}")
    if clasificacion.get('variables_libres', 0) > 0:
        print(f"Número de variables libres: {clasificacion['variables_libres']}")
    print("="*70)
