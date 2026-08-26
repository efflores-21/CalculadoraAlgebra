"""
Módulo de interfaz de usuario
Interacción con el usuario para entrada/salida de datos
"""

from backend.matriz import crear_matriz_aumentada, mostrar_matriz, es_cero


def obtener_datos_usuario():
    """
    Solicita al usuario el tamaño del sistema y los coeficientes.
    
    Returns:
        tuple: (m, n, coeficientes, terminos)
            - m: número de ecuaciones
            - n: número de variables
            - coeficientes: lista de listas con los coeficientes
            - terminos: lista con los términos independientes
    """
    print("\n" + "="*70)
    print("CALCULADORA DE SISTEMAS DE ECUACIONES LINEALES")
    print("Método: Eliminación por Filas (Gauss)")
    print("="*70)
    
    # Solicitar dimensiones
    while True:
        try:
            m = int(input("\nIngrese el número de ecuaciones (m): "))
            n = int(input("Ingrese el número de variables (n): "))
            if m <= 0 or n <= 0:
                print("Error: Los valores deben ser positivos.")
                continue
            break
        except ValueError:
            print("Error: Ingrese números enteros válidos.")
    
    print(f"\nIngresará los coeficientes de una matriz de {m}×{n} y el vector b")
    
    coeficientes = []
    terminos = []
    
    # Solicitar coeficientes
    for i in range(m):
        print(f"\nEcuación {i + 1}:")
        fila = []
        
        for j in range(n):
            while True:
                try:
                    coef = float(input(f"  Coeficiente x{j + 1}: "))
                    fila.append(coef)
                    break
                except ValueError:
                    print("  Error: Ingrese un número válido.")
        
        coeficientes.append(fila)
        
        # Solicitar término independiente
        while True:
            try:
                termino = float(input(f"  Término independiente (b): "))
                terminos.append(termino)
                break
            except ValueError:
                print("  Error: Ingrese un número válido.")
    
    return m, n, coeficientes, terminos


def mostrar_solucion(resultado, coeficientes_originales, terminos_originales):
    """
    Muestra la solución del sistema de manera clara.
    
    Args:
        resultado: diccionario con los resultados de resolver_sistema()
        coeficientes_originales: matriz A original
        terminos_originales: vector b original
    """
    soluciones = resultado['soluciones']
    variables_libres = resultado['variables_libres']
    n = len(coeficientes_originales[0])
    
    print("\n" + "="*70)
    print("SOLUCIÓN DEL SISTEMA")
    print("="*70)
    
    if not variables_libres:
        # Solución única
        print("\nValores de las variables:")
        for var in range(n):
            valor = soluciones.get(var, 0)
            print(f"  x{var + 1} = {valor:.6f}")
    else:
        # Infinitas soluciones
        print("\nVariables con valor definido:")
        for var in range(n):
            if var not in variables_libres:
                valor = soluciones.get(var, 0)
                print(f"  x{var + 1} = {valor:.6f}")
        
        print("\nVariables libres:")
        for var_libre in variables_libres:
            print(f"  x{var_libre + 1} = t_{var_libre + 1} (parámetro libre)")


def verificar_solucion(soluciones, coeficientes_originales, terminos_originales, variables_libres):
    """
    Verifica la solución sustituyendo en el sistema original.
    
    Args:
        soluciones: diccionario con variable -> valor
        coeficientes_originales: matriz A original
        terminos_originales: vector b original
        variables_libres: lista de variables libres
    
    Returns:
        bool: True si la solución es válida (para el caso determinado)
    """
    print("\n" + "="*70)
    print("VERIFICACIÓN DE LA SOLUCIÓN")
    print("="*70)
    
    if variables_libres:
        print("\nNota: Sistema con infinitas soluciones.")
        print("La verificación usa valores específicos para las variables libres.")
        print("Asignando valores de prueba: t_i = 0 para cada variable libre.\n")
        
        # Asignar 0 a las variables libres para la verificación
        for var_libre in variables_libres:
            soluciones[var_libre] = 0
    
    m = len(coeficientes_originales)
    
    print("Sustituyendo en el sistema original:\n")
    
    todas_correctas = True
    
    for i in range(m):
        # Calcular suma de productos
        suma = 0
        ecuacion_str = ""
        
        for j in range(len(coeficientes_originales[i])):
            coef = coeficientes_originales[i][j]
            valor = soluciones.get(j, 0)
            suma += coef * valor
            
            if j == 0:
                ecuacion_str += f"{coef:.2f}·x{j+1}"
            else:
                ecuacion_str += f" + {coef:.2f}·x{j+1}" if coef >= 0 else f" - {abs(coef):.2f}·x{j+1}"
        
        termino = terminos_originales[i]
        diferencia = abs(suma - termino)
        es_correcta = es_cero(diferencia)
        
        if not es_correcta:
            todas_correctas = False
        
        estado = "[OK]" if es_correcta else "[ERROR]"
        print(f"Ecuación {i+1}: {ecuacion_str} = {suma:.6f}")
        print(f"            Término independiente esperado: {termino:.6f} {estado}\n")
    
    return todas_correctas


def menu_principal():
    """
    Muestra el menú principal y solicita la opción del usuario.
    
    Returns:
        str: opción seleccionada
    """
    print("\n" + "="*70)
    print("MENÚ PRINCIPAL")
    print("="*70)
    print("1. Resolver un nuevo sistema")
    print("2. Salir")
    print("="*70)
    
    while True:
        opcion = input("Seleccione una opción (1-2): ")
        if opcion in ['1', '2']:
            return opcion
        print("Error: Seleccione una opción válida.")
