"""
CALCULADORA DE ÁLGEBRA LINEAL
Programa Principal - Resolución de Sistemas de Ecuaciones Lineales

Autor: Grupo de Programación
Asignatura: Álgebra Lineal (MTM0120)
Universidad Americana

Este programa resuelve sistemas de ecuaciones lineales Ax = b
utilizando el método de eliminación por filas (Gaussiana)
sin librerías como NumPy o SciPy.
"""

from frontend.interfaz import (
    obtener_datos_usuario, mostrar_solucion, verificar_solucion, menu_principal
)
from backend.matriz import crear_matriz_aumentada, mostrar_matriz
from backend.eliminacion import resolver_sistema
from backend.clasificador import clasificar_sistema, mostrar_clasificacion


def main():
    """
    Función principal que orquesta el flujo del programa.
    """
    print("\n" + "="*70)
    print("CALCULADORA DE SISTEMAS DE ECUACIONES LINEALES".center(70))
    print("Método: Eliminación Gaussiana".center(70))
    print("="*70)
    
    while True:
        opcion = menu_principal()
        
        if opcion == '2':
            print("\n¡Gracias por usar la calculadora! Hasta luego.")
            break
        
        # Opción 1: Resolver un nuevo sistema
        try:
            # PASO 1: Obtener datos del usuario
            m, n, coeficientes, terminos = obtener_datos_usuario()
            
            # PASO 2: Crear la matriz aumentada [A|b]
            matriz_aumentada = crear_matriz_aumentada(m, n, coeficientes, terminos)
            
            # PASO 3: Resolver el sistema usando eliminación Gaussiana
            resultado = resolver_sistema(matriz_aumentada)
            
            # PASO 4: Clasificar el sistema
            clasificacion = clasificar_sistema(
                resultado['matriz_escalonada'],
                resultado['rango']
            )
            mostrar_clasificacion(clasificacion)
            
            # PASO 5: Mostrar la solución
            if clasificacion['tipo'] != 'Inconsistente':
                mostrar_solucion(resultado, coeficientes, terminos)
            
            # PASO 6: Verificar la solución
            if clasificacion['tipo'] != 'Inconsistente':
                verificar_solucion(
                    resultado['soluciones'].copy(),
                    coeficientes,
                    terminos,
                    resultado['variables_libres']
                )
            
            # Mostrar matriz escalonada final
            print("\n" + "="*70)
            print("MATRIZ ESCALONADA FINAL")
            print("="*70)
            mostrar_matriz(resultado['matriz_escalonada'], "Matriz en forma escalonada")
            
        except Exception as e:
            print(f"\nError durante la resolución: {e}")
            print("Por favor, verifique los datos ingresados.")
        
        # Preguntar si desea continuar
        print("\n" + "="*70)
        continuar = input("¿Desea resolver otro sistema? (s/n): ").lower()
        if continuar != 's':
            print("\n¡Gracias por usar la calculadora! Hasta luego.")
            break


if __name__ == "__main__":
    main()
