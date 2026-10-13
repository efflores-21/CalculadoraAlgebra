"""
Textos de la opción «0. Ver Teoremas Clave del Módulo» de cada módulo.

Proyecto integrador (todas las unidades).
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

TEOREMAS = {
    "sistemas": (
        "TEOREMA DE ROUCHÉ-CAPELLI\n\n"
        "El sistema Ax=b es consistente si y solo si rango(A)=rango([A|b]).\n"
        "Si además ese rango es igual al número de incógnitas, la solución es única.\n"
        "Si el rango es menor que el número de incógnitas, hay infinitas soluciones.\n\n"
        "OPERACIONES ELEMENTALES\n"
        "Intercambiar filas, multiplicar una fila por un escalar no nulo o sumar "
        "a una fila un múltiplo de otra conserva el conjunto de soluciones.\n"
        "\nREGLA DE CRAMER\n"
        "Para Ax=b cuadrado con det(A) != 0, x_i=det(A_i(b))/det(A), donde "
        "A_i(b) reemplaza la columna i de A por b.\n"
    ),
    "vectores": (
        "TEOREMA DE INDEPENDENCIA LINEAL\n\n"
        "Los vectores v₁, …, vₖ son linealmente independientes si la única solución "
        "de c₁·v₁ + … + cₖ·vₖ = 0 es c₁ = … = cₖ = 0.\n"
        "Si el sistema homogéneo tiene una variable libre, existe una solución "
        "no trivial y los vectores son linealmente dependientes.\n\n"
        "CRITERIO DE RANGO\n"
        "Los vectores son L.I. si y solo si la matriz que los tiene como columnas "
        "tiene k pivotes. En R^n no puede haber más de n vectores L.I.; por tanto, "
        "si k>n, son L.D.\n\n"
        "PROPIEDADES\n"
        "Un conjunto que contiene al vector cero es L.D. Un subconjunto de un "
        "conjunto L.I. también es L.I. Si un conjunto es L.D., cualquier conjunto "
        "que lo contenga también es L.D.\n"
    ),
    "operaciones_vectores": (
        "OPERACIONES CON VECTORES\n\n"
        "La suma y la resta se realizan coordenada por coordenada:\n"
        "(u+v)i = ui+vi y (u-v)i = ui-vi.\n"
        "El producto por escalar también opera en cada coordenada:\n"
        "(c*u)i = c*ui.\n\n"
        "COMBINACION LINEAL\n"
        "b es combinación lineal de v₁, …, vₖ si existen escalares c₁, …, cₖ "
        "tales que c₁·v₁ + … + cₖ·vₖ = b. Esto se resuelve como V*c=b, con los "
        "vectores como columnas de V.\n"
    ),
    "matrices": (
        "PROPIEDADES BÁSICAS DE MATRICES\n\n"
        "A+B y A-B están definidas cuando A y B tienen el mismo tamaño.\n"
        "El producto AB está definido si columnas(A)=filas(B).\n"
        "Una matriz cuadrada A es invertible si existe A^-1 tal que "
        "A*A^-1=A^-1*A=I.\n"
        "La traspuesta intercambia filas por columnas: (A^T)[i,j]=A[j,i].\n"
        "Regla fila-columna: (AB)[i,j] es el producto punto de la fila i de A "
        "con la columna j de B.\n"
        "(A^T)^T=A; (A+B)^T=A^T+B^T; (rA)^T=rA^T; (AB)^T=B^T A^T.\n"
        "\nTEOREMA DE LA INVERSA (Sesión 10)\n"
        "(A^-1)^-1=A; (AB)^-1=B^-1 A^-1; "
        "(A^T)^-1=(A^-1)^T.\n"
        "\nTEOREMA DE LA MATRIZ INVERTIBLE: caracterizaciones indicadas\n"
        "c) A tiene n posiciones pivote.\n"
        "e) Las columnas de A son linealmente independientes.\n"
        "h) Las columnas de A generan R^n.\n"
        "A es invertible si y solo si det(A) != 0.\n"
        "A^-1 = (1/det(A)) · adj(A), donde adj(A) es la transpuesta de la matriz de cofactores.\n"
        "La reducción [A | I] -> [I | A^-1] calcula la inversa por Gauss-Jordan.\n"
        "\nPROPIEDADES QUE COMPRUEBA EL VERIFICADOR (opción 9)\n"
        "Transposición: (A^T)^T = A; (A+B)^T = A^T + B^T; (kA)^T = kA^T; (AB)^T = B^T A^T; "
        "A(B+C) = AB + AC; (AB)C = A(BC).\n"
        "Inversa: (A^-1)^-1 = A; (AB)^-1 = B^-1 A^-1; (A^T)^-1 = (A^-1)^T; A·A^-1 = I.\n"
        "Determinantes: det(A^T) = det(A); det(AB) = det(A)det(B); det(A^-1) = 1/det(A); "
        "det(kA) = k^n det(A).\n"
        "Operaciones de fila: una permutación cambia el signo del determinante, un reemplazo "
        "lo conserva y multiplicar una fila por k lo multiplica por k.\n"
        "Matriz triangular: su determinante es el producto de la diagonal.\n"
    ),
    "determinantes": (
        "PROPIEDADES DEL DETERMINANTE\n\n"
        "El determinante está definido para matrices cuadradas.\n"
        "Intercambiar dos filas cambia el signo del determinante.\n"
        "Sumar a una fila un múltiplo de otra no cambia el determinante.\n"
        "Multiplicar una fila por un escalar multiplica el determinante por ese escalar.\n"
        "Una matriz es singular si y solo si det(A)=0.\n"
        "En una matriz triangular, det(A) es el producto de las entradas diagonales.\n"
        "det(A^T)=det(A) y det(AB)=det(A)det(B).\n"
        "Si det(A) != 0, det(A^-1)=1/det(A).\n"
        "A^-1=(1/det(A)) adj(A), donde adj(A)=C^T y C es la matriz de cofactores.\n"
        "Regla de Cramer: para Ax=b con det(A) != 0, "
        "x_i=det(A_i(b))/det(A).\n"
    ),
    "lu": (
        "FACTORIZACIÓN LU\n\n"
        "Si A (m×n) se puede llevar a su forma escalonada U usando solo reemplazos "
        "de fila (Fi ← Fi − l·Fj), entonces A = LU, donde:\n"
        "• U (m×n) es la forma escalonada de A.\n"
        "• L (m×m) es triangular inferior con unos en la diagonal y guarda cada "
        "multiplicador l = (elemento a eliminar) / (pivote) en la posición (i, j).\n\n"
        "PERMUTACIONES\n"
        "Si un pivote es cero y hace falta intercambiar filas, A no admite A = LU; "
        "se necesita pivoteo parcial: PA = LU.\n\n"
        "SOLUCIÓN DE Ax = b (A de n×n)\n"
        "Como Ax = L(Ux) = b, se resuelve en dos etapas:\n"
        "1) Ly = b, por sustitución hacia adelante sobre [L | b].\n"
        "2) Ux = y, por sustitución hacia atrás sobre [U | y].\n"
        "Si U tiene un cero en la diagonal, A es singular y no hay solución única.\n\n"
        "VENTAJA\n"
        "La factorización se hace una sola vez y sirve para resolver Ax = b con "
        "muchos vectores b distintos.\n"
    ),
    "propiedades": (
        "LINEALIDAD DEL PRODUCTO MATRIZ-VECTOR\n\n"
        "Si A es m por n y u,v pertenecen a R^n, entonces:\n"
        "A(u+v)=Au+Av.\n\n"
        "Para todo escalar c:\n"
        "A(cu)=c(Au).\n\n"
        "Estas dos igualdades expresan que la transformación x -> A*x es lineal.\n"
        "Las dimensiones deben ser compatibles: A tiene n columnas y u,v tienen "
        "n componentes.\n"
    ),
}


def obtener_resumen(modulo):
    """Devuelve el resumen teórico asociado al módulo indicado."""
    if modulo not in TEOREMAS:
        raise ValueError("No hay un resumen de teoremas para este módulo.")
    return TEOREMAS[modulo]
