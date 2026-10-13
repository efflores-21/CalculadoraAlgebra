"""Textos breves de los teoremas relacionados con cada módulo."""

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
        "La reduccion [A | I] -> [I | A^-1] calcula la inversa por Gauss-Jordan.\n"
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
        "A = LU.\n"
        "L es una matriz triangular inferior con unos en la diagonal.\n"
        "U es una matriz triangular superior.\n\n"
        "Para resolver Ax = b mediante LU:\n"
        "1) Resolver Ly = b mediante sustitución hacia adelante.\n"
        "2) Resolver Ux = y mediante sustitución hacia atrás.\n"
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
