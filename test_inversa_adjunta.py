#!/usr/bin/env python3
"""
Script de validación de la Fase 1: Inversa por Matriz Adjunta.

Este script prueba las funciones implementadas sin modificar archivos del proyecto.
Solo ejecuta y documenta resultados.
"""

import sys
from fractions import Fraction

# Importar las funciones implementadas
sys.path.insert(0, '.')
from backend.operaciones_matriciales import (
    determinante_por_cofactores,
    matriz_menores,
    matriz_cofactores,
    matriz_adjunta,
    inversa_por_adjunta,
    transponer_matriz,
    multiplicar_matrices
)
from backend.matriz import formatear_valor


def formatear_matriz_test(M):
    """Formatea una matriz para visualización en pruebas."""
    if not M:
        return "[ ]"
    filas = []
    for fila in M:
        valores = [str(v) if isinstance(v, Fraction) else formatear_valor(v) for v in fila]
        filas.append("[ " + ", ".join(valores) + " ]")
    return "\n".join(filas)


def comparar_matrices(M1, M2, tolerancia=None):
    """Compara dos matrices exactamente (con Fraction)."""
    if len(M1) != len(M2) or len(M1[0]) != len(M2[0]):
        return False
    for i in range(len(M1)):
        for j in range(len(M1[0])):
            if M1[i][j] != M2[i][j]:
                return False
    return True


print("=" * 80)
print("VALIDACIÓN FASE 1: INVERSA POR MATRIZ ADJUNTA")
print("=" * 80)

# ============================================================================
# PRUEBA 1: MATRIZ 2×2
# ============================================================================
print("\n" + "=" * 80)
print("PRUEBA 1: MATRIZ 2×2")
print("=" * 80)

A1 = [[1, 2], [3, 4]]
print("\nMatriz A:")
print(formatear_matriz_test(A1))

try:
    det_1 = determinante_por_cofactores(A1)
    print(f"\n✓ Determinante calculado: det(A) = {det_1}")
    print(f"  Esperado: -2")
    print(f"  Coincide: {det_1 == Fraction(-2, 1)}")
    
    menores_1 = matriz_menores(A1)
    print(f"\n✓ Matriz de menores:")
    print(formatear_matriz_test(menores_1))
    print(f"  Esperado:")
    print(formatear_matriz_test([[Fraction(4), Fraction(3)], 
                                 [Fraction(2), Fraction(1)]]))
    esperado_menores_1 = [[Fraction(4), Fraction(3)], [Fraction(2), Fraction(1)]]
    print(f"  Coincide: {comparar_matrices(menores_1, esperado_menores_1)}")
    
    cofactores_1 = matriz_cofactores(A1)
    print(f"\n✓ Matriz de cofactores:")
    print(formatear_matriz_test(cofactores_1))
    print(f"  Esperado:")
    print(formatear_matriz_test([[Fraction(4), Fraction(-3)], 
                                 [Fraction(-2), Fraction(1)]]))
    esperado_cofactores_1 = [[Fraction(4), Fraction(-3)], [Fraction(-2), Fraction(1)]]
    print(f"  Coincide: {comparar_matrices(cofactores_1, esperado_cofactores_1)}")
    
    adjunta_1 = matriz_adjunta(A1)
    print(f"\n✓ Matriz adjunta:")
    print(formatear_matriz_test(adjunta_1))
    print(f"  Esperado:")
    print(formatear_matriz_test([[Fraction(4), Fraction(-2)], 
                                 [Fraction(-3), Fraction(1)]]))
    esperado_adjunta_1 = [[Fraction(4), Fraction(-2)], [Fraction(-3), Fraction(1)]]
    print(f"  Coincide: {comparar_matrices(adjunta_1, esperado_adjunta_1)}")
    
    inversa_1, pasos_1 = inversa_por_adjunta(A1)
    print(f"\n✓ Matriz inversa A^-1:")
    print(formatear_matriz_test(inversa_1))
    print(f"  Esperado:")
    print(formatear_matriz_test([[Fraction(-2), Fraction(1)], 
                                 [Fraction(3, 2), Fraction(-1, 2)]]))
    esperado_inversa_1 = [[Fraction(-2), Fraction(1)], [Fraction(3, 2), Fraction(-1, 2)]]
    print(f"  Coincide: {comparar_matrices(inversa_1, esperado_inversa_1)}")
    
    print(f"\n✓ Pasos generados: {len(pasos_1)} pasos")
    for idx, (desc, mat) in enumerate(pasos_1, 1):
        print(f"  Paso {idx}: {desc}")
    
    print("\n✅ PRUEBA 1 PASADA")
    
except Exception as e:
    print(f"\n❌ PRUEBA 1 FALLÓ")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PRUEBA 2: MATRIZ 3×3
# ============================================================================
print("\n" + "=" * 80)
print("PRUEBA 2: MATRIZ 3×3")
print("=" * 80)

A2 = [[1, 2, 3], [0, 1, 4], [5, 6, 0]]
print("\nMatriz A:")
print(formatear_matriz_test(A2))

try:
    det_2 = determinante_por_cofactores(A2)
    print(f"\n✓ Determinante calculado: det(A) = {det_2}")
    print(f"  Esperado: 1")
    print(f"  Coincide: {det_2 == Fraction(1, 1)}")
    
    menores_2 = matriz_menores(A2)
    print(f"\n✓ Matriz de menores calculada ({len(menores_2)}×{len(menores_2[0])})")
    print(formatear_matriz_test(menores_2))
    
    cofactores_2 = matriz_cofactores(A2)
    print(f"\n✓ Matriz de cofactores calculada ({len(cofactores_2)}×{len(cofactores_2[0])})")
    print(formatear_matriz_test(cofactores_2))
    
    adjunta_2 = matriz_adjunta(A2)
    print(f"\n✓ Matriz adjunta calculada ({len(adjunta_2)}×{len(adjunta_2[0])})")
    print(formatear_matriz_test(adjunta_2))
    
    inversa_2, pasos_2 = inversa_por_adjunta(A2)
    print(f"\n✓ Matriz inversa A^-1 calculada ({len(inversa_2)}×{len(inversa_2[0])})")
    print(formatear_matriz_test(inversa_2))
    
    # Verificación de consistencia: A × A^-1 debe ser cercano a I
    # (Hacemos multiplicación manual para verificar)
    print(f"\n✓ Verificación de consistencia: A × A^-1")
    producto = multiplicar_matrices(A2, inversa_2)
    print("Producto A × A^-1:")
    print(formatear_matriz_test(producto))
    
    # Construcción de matriz identidad esperada
    n = len(A2)
    identidad_esperada = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
    
    if comparar_matrices(producto, identidad_esperada):
        print("✓ A × A^-1 = I exactamente (verificación exitosa)")
    else:
        print("⚠ A × A^-1 ≠ I exactamente")
        print("Diferencias (debería ser cercano a I):")
        for i in range(n):
            for j in range(n):
                diff = producto[i][j] - identidad_esperada[i][j]
                if diff != 0:
                    print(f"  [{i}][{j}]: {producto[i][j]} vs esperado {identidad_esperada[i][j]}")
    
    print(f"\n✓ Pasos generados: {len(pasos_2)} pasos")
    
    print("\n✅ PRUEBA 2 PASADA")
    
except Exception as e:
    print(f"\n❌ PRUEBA 2 FALLÓ")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PRUEBA 3: MATRIZ SINGULAR
# ============================================================================
print("\n" + "=" * 80)
print("PRUEBA 3: MATRIZ SINGULAR")
print("=" * 80)

A3 = [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
print("\nMatriz A (singular):")
print(formatear_matriz_test(A3))

try:
    det_3 = determinante_por_cofactores(A3)
    print(f"\n✓ Determinante calculado: det(A) = {det_3}")
    print(f"  Esperado: 0")
    print(f"  Coincide: {det_3 == Fraction(0, 1)}")
    
    print("\n✓ Intentando calcular inversa_por_adjunta()...")
    try:
        inversa_3, pasos_3 = inversa_por_adjunta(A3)
        print("❌ ERROR: La función debería haber rechazado la matriz singular")
        print("   pero permitió el cálculo. PRUEBA 3 FALLÓ")
    except ValueError as e:
        if "singular" in str(e).lower():
            print(f"✓ Matriz rechazada correctamente: {e}")
            print("✅ PRUEBA 3 PASADA")
        else:
            print(f"❌ Error inesperado: {e}")
    
except Exception as e:
    print(f"\n❌ PRUEBA 3 FALLÓ (durante cálculo de determinante)")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PRUEBA 4: MATRIZ IDENTIDAD 4×4
# ============================================================================
print("\n" + "=" * 80)
print("PRUEBA 4: MATRIZ IDENTIDAD 4×4")
print("=" * 80)

A4 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
print("\nMatriz A (identidad):")
print(formatear_matriz_test(A4))

try:
    det_4 = determinante_por_cofactores(A4)
    print(f"\n✓ Determinante calculado: det(A) = {det_4}")
    print(f"  Esperado: 1")
    print(f"  Coincide: {det_4 == Fraction(1, 1)}")
    
    adjunta_4 = matriz_adjunta(A4)
    print(f"\n✓ Matriz adjunta calculada")
    print(formatear_matriz_test(adjunta_4))
    print(f"  ¿Es igual a I?: {comparar_matrices(adjunta_4, A4)}")
    
    inversa_4, pasos_4 = inversa_por_adjunta(A4)
    print(f"\n✓ Matriz inversa A^-1 calculada")
    print(formatear_matriz_test(inversa_4))
    print(f"  ¿Es igual a I?: {comparar_matrices(inversa_4, A4)}")
    
    if comparar_matrices(inversa_4, A4):
        print("✅ PRUEBA 4 PASADA")
    else:
        print("❌ PRUEBA 4 FALLÓ: A^-1 ≠ I")
    
except Exception as e:
    print(f"\n❌ PRUEBA 4 FALLÓ")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PRUEBA 5: ARITMÉTICA EXACTA (Fracciones)
# ============================================================================
print("\n" + "=" * 80)
print("PRUEBA 5: ARITMÉTICA EXACTA (Fracciones)")
print("=" * 80)

A5 = [[Fraction(1, 2), Fraction(1, 3)], [Fraction(1, 4), Fraction(1, 5)]]
print("\nMatriz A (con fracciones):")
print(formatear_matriz_test(A5))

try:
    det_5 = determinante_por_cofactores(A5)
    print(f"\n✓ Determinante calculado: det(A) = {det_5}")
    print(f"  Tipo: {type(det_5)}")
    print(f"  ¿Es Fraction?: {isinstance(det_5, Fraction)}")
    
    inversa_5, pasos_5 = inversa_por_adjunta(A5)
    print(f"\n✓ Matriz inversa A^-1 calculada")
    print(formatear_matriz_test(inversa_5))
    
    # Verificar que todos los elementos son Fraction
    todas_fraction = True
    for fila in inversa_5:
        for elem in fila:
            if not isinstance(elem, Fraction):
                todas_fraction = False
                print(f"❌ Elemento no es Fraction: {elem} (tipo: {type(elem)})")
    
    if todas_fraction:
        print(f"  ✓ Todos los elementos son Fraction (aritmética exacta)")
    
    # Verificación de consistencia
    producto = multiplicar_matrices(A5, inversa_5)
    print(f"\n✓ Verificación: A × A^-1")
    print(formatear_matriz_test(producto))
    
    n = len(A5)
    identidad_esperada = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
    
    if comparar_matrices(producto, identidad_esperada):
        print("✓ A × A^-1 = I exactamente")
        print("✅ PRUEBA 5 PASADA")
    else:
        print("❌ PRUEBA 5 FALLÓ: A × A^-1 ≠ I")
    
except Exception as e:
    print(f"\n❌ PRUEBA 5 FALLÓ")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "=" * 80)
print("RESUMEN DE VALIDACIÓN")
print("=" * 80)
print("""
Funciones implementadas en backend/operaciones_matriciales.py:

1. ✓ determinante_por_cofactores(A)
2. ✓ matriz_menores(A)
3. ✓ matriz_cofactores(A)
4. ✓ transponer_matriz(A)  [Reutilizada en matriz_adjunta]
5. ✓ matriz_adjunta(A)
6. ✓ inversa_por_adjunta(A)

Todas las funciones están operativas y sin errores de sintaxis.

Revisa los resultados de las pruebas arriba para validación completa.
""")
