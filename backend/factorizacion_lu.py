"""
Factorización LU (A = LU) y solución de Ax = b por doble sustitución.

Unidad II, Álgebra de matrices [P6]. Reutiliza el producto matricial, la comprobación
de igualdad y la eliminación de Gauss-Jordan; incluye además PA = LU con pivoteo
parcial y la clasificación de sistemas rectangulares.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

from fractions import Fraction

from backend.clasificador import clasificar_sistema
from backend.eliminacion import resolver_sistema
from backend.matriz import _a_fraction, formatear_valor
from backend.operaciones_matriciales import (
    _matriz_a_fraction,
    identidad,
    multiplicar_matrices,
    multiplicar_matriz_vector,
    son_iguales,
)

MENSAJE_PERMUTACION = (
    "La matriz no admite Factorización LU sin permutación "
    "(requiere pivoteo parcial PA = LU)."
)


def factorizar_lu(A, incluir_explicaciones=False):
    """Reduce A (m×n) a su forma escalonada U solo con reemplazos de fila y guarda
    cada multiplicador en L (m×m). Devuelve (matriz_L, matriz_U, pasos)."""
    matriz_U = _matriz_a_fraction(A)
    m, n = len(matriz_U), len(matriz_U[0])
    matriz_L = identidad(m)
    pasos = []
    pasos_explicados = []
    fila_pivote = 0
    for columna in range(n):
        if fila_pivote == m:
            break
        pivote = matriz_U[fila_pivote][columna]
        if pivote == 0:
            # Con un cero en la posición pivote solo un intercambio de filas permitiría
            # seguir, y eso ya no es A = LU sino PA = LU.
            if any(matriz_U[i][columna] != 0 for i in range(fila_pivote + 1, m)):
                raise ValueError(MENSAJE_PERMUTACION)
            pasos_explicados.append({
                "objetivo": f"Buscar un pivote válido en la columna {columna + 1}.",
                "fundamento": "Si las entradas desde la fila activa hacia abajo son cero, no hay pivote en esta columna; se conserva la fila activa y se prueba la columna siguiente.",
                "procedimiento": f"Revisar U[{fila_pivote + 1}:{m},{columna + 1}]; todas las entradas candidatas son cero.",
                "resultado": "Se avanza una columna sin intercambiar filas; el siguiente pivote puede quedar fuera de la diagonal.",
                "matriz": [fila[:] for fila in matriz_U],
            })
            continue
        pasos_explicados.append({
            "objetivo": f"Seleccionar el pivote de la etapa {fila_pivote + 1} en la columna {columna + 1}.",
            "fundamento": "Sin permutar filas, el pivote es la entrada de la fila activa y la columna actual; la fila activa avanza solo después de encontrarlo.",
            "procedimiento": f"p = U[{fila_pivote + 1},{columna + 1}] = {formatear_valor(pivote)}.",
            "resultado": "Este pivote será el divisor para calcular cada multiplicador debajo de él.",
            "matriz": [fila[:] for fila in matriz_U],
        })
        for i in range(fila_pivote + 1, m):
            multiplicador_l = matriz_U[i][columna] / pivote
            if multiplicador_l == 0:
                continue
            # Se registra el multiplicador en L antes de alterar la fila en U.
            matriz_L[i][fila_pivote] = multiplicador_l
            entrada = matriz_U[i][columna]
            matriz_U[i] = [
                valor - multiplicador_l * valor_pivote
                for valor, valor_pivote in zip(matriz_U[i], matriz_U[fila_pivote])
            ]
            pasos.append((
                f"F{i + 1} ← F{i + 1} − ({formatear_valor(multiplicador_l)})·F{fila_pivote + 1}"
                f"   →   l{i + 1}{fila_pivote + 1} = {formatear_valor(multiplicador_l)}",
                [fila[:] for fila in matriz_U],
            ))
            pasos_explicados.append({
                "objetivo": f"Anular la entrada de la fila {i + 1}, columna {columna + 1} para formar U.",
                "fundamento": "Fᵢ ← Fᵢ − lᵢₖFₖ conserva la equivalencia; lᵢₖ se guarda en L para reconstruir A = LU.",
                "procedimiento": (f"lᵢₖ = {formatear_valor(entrada)} / {formatear_valor(pivote)} "
                                 f"= {formatear_valor(multiplicador_l)}; F{i + 1} ← F{i + 1} − "
                                 f"({formatear_valor(multiplicador_l)})F{fila_pivote + 1}."),
                "resultado": "La entrada bajo el pivote queda en cero y el multiplicador queda registrado en L.",
                "matriz": [fila[:] for fila in matriz_U],
            })
        fila_pivote += 1
    if incluir_explicaciones:
        return matriz_L, matriz_U, pasos, pasos_explicados
    return matriz_L, matriz_U, pasos


def resolver_por_reduccion(matriz, vector):
    """Reduce [matriz | vector] con Gauss-Jordan (sin reordenar filas).
    Devuelve (resultado de resolver_sistema, clasificación del sistema)."""
    aumentada = [fila[:] + [valor] for fila, valor in zip(matriz, vector)]
    resultado = resolver_sistema(aumentada, metodo="gauss-jordan", pivoteo_parcial=False)
    clase = clasificar_sistema(resultado["matriz_escalonada"], resultado["rango"])
    return resultado, clase


def resolver_lu(A, b):
    """Factoriza A = LU, verifica L·U == A y, si A es cuadrada, resuelve Ly = b y Ux = y.
    Devuelve un diccionario con L, U, los pasos, y, x y las comprobaciones."""
    matriz_A = _matriz_a_fraction(A)
    if b is None or len(b) != len(matriz_A):
        raise ValueError("El vector b debe tener una componente por cada fila de A.")
    vector_b = [_a_fraction(valor) for valor in b]
    matriz_L, matriz_U, pasos, pasos_explicados = factorizar_lu(matriz_A, incluir_explicaciones=True)
    producto_LU = multiplicar_matrices(matriz_L, matriz_U)
    datos = {
        "L": matriz_L, "U": matriz_U, "pasos": pasos, "pasos_explicados": pasos_explicados, "LU": producto_LU,
        "b": vector_b,
        "factorizacion_correcta": son_iguales(producto_LU, matriz_A),
        "cuadrada": len(matriz_A) == len(matriz_A[0]),
    }
    if not datos["cuadrada"]:
        return datos

    # L es triangular inferior con unos en la diagonal: Ly = b siempre tiene solución única.
    etapa_y, _ = resolver_por_reduccion(matriz_L, vector_b)
    vector_y = [etapa_y["soluciones_generales"][j][0] for j in range(len(matriz_L))]
    etapa_x, clase_x = resolver_por_reduccion(matriz_U, vector_y)
    datos.update({"etapa_y": etapa_y, "y": vector_y, "etapa_x": etapa_x, "clase_x": clase_x})
    if clase_x["tipo"] != "Consistente Determinado":
        return datos

    vector_x = [etapa_x["soluciones_generales"][j][0] for j in range(len(matriz_U))]
    producto_Ax = multiplicar_matriz_vector(matriz_A, vector_x)
    datos.update({"x": vector_x, "Ax": producto_Ax,
                  "comprobacion": son_iguales(producto_Ax, vector_b)})
    return datos

# Pivoteo parcial (PA = LU) y sistemas rectangulares: cada paso se registra con
# un callback para que la pantalla pueda mostrar la traza completa.


def _registrar_paso(callback, descripcion, L, U, mostrar_matrices=True, vector=None, P=None,
                    objetivo=None, fundamento=None, procedimiento=None, resultado=None):
    """Entrega una copia estable del estado actual a quien solicita la traza."""
    if callback is not None:
        paso = {
            "descripcion": descripcion,
            "objetivo": objetivo,
            "fundamento": fundamento,
            "procedimiento": procedimiento,
            "resultado": resultado,
            "L": [fila[:] for fila in L],
            "U": [fila[:] for fila in U],
            "mostrar_matrices": mostrar_matrices,
        }
        if vector is not None:
            paso["vector"] = (vector[0], vector[1][:])
        if P is not None:
            paso["P"] = [fila[:] for fila in P]
        callback(paso)


def _factorizar_con_traza(A, registrar_paso=None, pivoteo_parcial=False):
    """Factoriza P·A = L·U (o A = L·U sin pivoteo) registrando cada paso.
    Devuelve (P, L, U); sin pivoteo P es la identidad."""
    matriz = _matriz_a_fraction(A)
    m, n = len(matriz), len(matriz[0])
    P = [[Fraction(int(i == j)) for j in range(m)] for i in range(m)]
    L = [[Fraction(int(i == j)) for j in range(m)] for i in range(m)]
    U = [fila[:] for fila in matriz]
    _registrar_paso(
        registrar_paso, "Estado inicial: P=I, L=I y U=A.", L, U,
        P=P if pivoteo_parcial else None,
        objetivo="Inicializar las matrices para la factorización.",
        fundamento="I·A=A; P registra los intercambios y L conservará los multiplicadores de eliminación.",
        procedimiento="Asignar P=I, L=I y U=A.",
        resultado="U parte de A; todavía no se ha eliminado ninguna entrada.",
    )
    fila_pivote = 0
    for columna in range(n):
        if fila_pivote >= m:
            break
        if pivoteo_parcial:
            candidatos = [(i, U[i][columna]) for i in range(fila_pivote, m)]
            fila_elegida = max(
                range(fila_pivote, m), key=lambda i: abs(U[i][columna])
            )
            if U[fila_elegida][columna] == 0:
                _registrar_paso(
                    registrar_paso,
                    f"Columna {columna + 1} sin pivote: las entradas restantes son cero; "
                    "se continúa a la columna siguiente.",
                    L, U, P=P, mostrar_matrices=False,
                    objetivo=f"Seleccionar un pivote válido en la columna {columna + 1}.",
                    fundamento="Si todas las entradas disponibles valen cero, ningún intercambio produce un pivote no nulo.",
                    procedimiento="Comparar los valores absolutos candidatos de la columna activa.",
                    resultado="Se omite la columna; no se divide por cero.",
                )
                continue
            if fila_elegida != fila_pivote:
                pivote_anterior = U[fila_pivote][columna]
                pivote_elegido = U[fila_elegida][columna]
                U[fila_pivote], U[fila_elegida] = U[fila_elegida], U[fila_pivote]
                P[fila_pivote], P[fila_elegida] = P[fila_elegida], P[fila_pivote]
                for j in range(fila_pivote):
                    L[fila_pivote][j], L[fila_elegida][j] = (
                        L[fila_elegida][j], L[fila_pivote][j]
                    )
                _registrar_paso(
                    registrar_paso,
                    f"Intercambio parcial F{fila_pivote + 1} ↔ F{fila_elegida + 1}; "
                    "se permutan P y las columnas previas de L.",
                    L, U, P=P,
                    objetivo="Colocar en la fila activa el candidato seleccionado por pivoteo parcial.",
                    fundamento=("El pivote actual es cero y no se puede usar como divisor. Se intercambia por un candidato no nulo."
                                if pivote_anterior == 0 else
                                "El pivote actual no tiene el mayor valor absoluto disponible. El pivoteo parcial elige el de mayor magnitud para limitar el tamaño de los multiplicadores."),
                    procedimiento=("Candidatos antes del intercambio: " + ", ".join(f"U[{i + 1},{columna + 1}]={formatear_valor(v)}" for i, v in candidatos)
                                   + f"; |{formatear_valor(pivote_anterior)}| < |{formatear_valor(pivote_elegido)}|, así que se intercambian F{fila_pivote + 1} y F{fila_elegida + 1}."),
                    resultado="P y U ya contienen las filas permutadas; también se reordenaron en L los multiplicadores de columnas previas.",
                )
        elif U[fila_pivote][columna] == 0:
            if all(U[i][columna] == 0 for i in range(fila_pivote + 1, m)):
                _registrar_paso(
                    registrar_paso,
                    f"Columna {columna + 1} sin pivote: las entradas restantes son cero; "
                    "se continúa a la columna siguiente.",
                    L, U, mostrar_matrices=False,
                    objetivo=f"Buscar un pivote sin permutar filas en la columna {columna + 1}.",
                    fundamento="Si las entradas restantes son cero, la columna no permite ni requiere eliminación adicional.",
                    procedimiento="Inspeccionar las filas desde la fila activa hacia abajo.",
                    resultado="Se avanza a la columna siguiente sin mover la fila activa ni intercambiar filas.",
                )
                continue
            raise ValueError(MENSAJE_PERMUTACION)
        pivote = U[fila_pivote][columna]
        candidatos_actuales = ([(i, U[i][columna]) for i in range(fila_pivote, m)]
                               if pivoteo_parcial else [])
        _registrar_paso(
            registrar_paso,
            f"Pivote de la etapa {fila_pivote + 1}, columna {columna + 1}: "
            f"U[{fila_pivote + 1},{columna + 1}] = {formatear_valor(pivote)}.",
            L, U, mostrar_matrices=False, P=P if pivoteo_parcial else None,
            objetivo="Fijar el pivote que se usará en las eliminaciones de esta columna.",
            fundamento=("Se selecciona el mayor valor absoluto entre las filas restantes; así se evita dividir por cero y se limita la magnitud de los multiplicadores."
                        if pivoteo_parcial else
                        "Sin permutar filas, se toma la entrada de la fila activa en la columna actual; la fila avanza únicamente cuando se encuentra un pivote."),
            procedimiento=(("Candidatos actuales en U: " + ", ".join(f"U[{i + 1},{columna + 1}]={formatear_valor(v)}" for i, v in candidatos_actuales)
                            + f". Pivote: U[{fila_pivote + 1},{columna + 1}]={formatear_valor(pivote)}.")
                           if pivoteo_parcial else f"Pivote U[{fila_pivote + 1},{columna + 1}]={formatear_valor(pivote)}."),
            resultado=f"Se usará {formatear_valor(pivote)} para calcular los multiplicadores de las filas inferiores.",
        )
        for i in range(fila_pivote + 1, m):
            if U[i][columna] == 0:
                continue
            multiplicador = U[i][columna] / pivote
            L[i][fila_pivote] = multiplicador
            _registrar_paso(
                registrar_paso,
                f"Multiplicador m{i + 1},{fila_pivote + 1} = "
                f"L[{i + 1},{fila_pivote + 1}] = U[{i + 1},{columna + 1}] / "
                f"{formatear_valor(pivote)} = {formatear_valor(multiplicador)}; "
                "se registra en L.",
                L, U, P=P if pivoteo_parcial else None,
                objetivo=f"Calcular el factor para anular U[{i + 1},{columna + 1}].",
                fundamento="El cociente entrada/pivote hace que la primera componente de Fᵢ − mFₖ sea cero; ese factor se almacena en L.",
                procedimiento=(f"m = {formatear_valor(U[i][columna])} / {formatear_valor(pivote)} "
                               f"= {formatear_valor(multiplicador)}; registrar L[{i + 1},{fila_pivote + 1}]."),
                resultado=f"L[{i + 1},{fila_pivote + 1}] = {formatear_valor(multiplicador)}.",
            )
            for j in range(columna, n):
                U[i][j] -= multiplicador * U[fila_pivote][j]
            _registrar_paso(
                registrar_paso,
                f"Eliminación: F{i + 1} <- F{i + 1} - "
                f"({formatear_valor(multiplicador)})F{fila_pivote + 1}.",
                L, U, P=P if pivoteo_parcial else None,
                objetivo=f"Hacer cero U[{i + 1},{columna + 1}] sin cambiar las soluciones.",
                fundamento="Reemplazar una fila por ella menos un múltiplo de otra fila preserva el sistema equivalente.",
                procedimiento=f"F{i + 1} ← F{i + 1} − ({formatear_valor(multiplicador)})F{fila_pivote + 1}.",
                resultado="La entrada debajo del pivote se anula; L conserva el multiplicador para reconstruir la matriz original.",
            )
        _registrar_paso(
            registrar_paso,
            f"Matrices L y U al finalizar la etapa {fila_pivote + 1} "
            f"(columna pivote {columna + 1}).",
            L, U, mostrar_matrices=False, P=P if pivoteo_parcial else None,
            objetivo=f"Cerrar la eliminación de la columna {columna + 1}.",
            fundamento="Al terminar esta columna, sus entradas debajo del pivote deben ser cero; las etapas posteriores no alteran las columnas ya eliminadas.",
            procedimiento=f"Conservar los valores actuales de L y U después de procesar el pivote de la columna {columna + 1}.",
            resultado=f"L y U muestran la factorización parcial tras la etapa {fila_pivote + 1}.",
        )
        fila_pivote += 1
    return P, L, U


def factorizar_lu_pivoteo(A, registrar_paso=None):
    """Factoriza P·A = L·U con pivoteo parcial; devuelve (P, L, U)."""
    return _factorizar_con_traza(A, registrar_paso, pivoteo_parcial=True)


def resolver_sistema_lu(A, b, registrar_paso=None, pivoteo_parcial=False):
    """Resuelve y clasifica Ax = b (A de m×n) mediante PA = LU o A = LU.
    Devuelve P, L, U, y, el estado (única, infinitas o incompatible) y la solución general."""
    matriz = _matriz_a_fraction(A)
    m, n = len(matriz), len(matriz[0])
    if b is None:
        raise ValueError("El vector b no puede estar vacío.")
    vector_original = [_a_fraction(valor) for valor in b]
    if len(vector_original) != m:
        raise ValueError("El vector b debe tener una entrada por fila de A.")

    P, L, U = _factorizar_con_traza(
        matriz, registrar_paso=registrar_paso, pivoteo_parcial=pivoteo_parcial
    )
    vector_permutado = vector_original[:]
    if pivoteo_parcial:
        vector_permutado = [
            sum(P[i][j] * vector_original[j] for j in range(m)) for i in range(m)
        ]
        _registrar_paso(
            registrar_paso, "Permutar el vector: Pb.", L, U,
            mostrar_matrices=False, vector=("Pb", vector_permutado), P=P,
            objetivo="Aplicar al término independiente el mismo orden de filas que a A.",
            fundamento="De PA=LU y Ax=b se obtiene PAx=Pb; por eso la sustitución usa Pb.",
            procedimiento="Multiplicar P por b con la permutación de filas registrada.",
            resultado="Pb es el lado derecho de Ly=Pb.",
        )

    y = [Fraction(0) for _ in range(m)]
    for i in range(m):
        suma = sum(L[i][j] * y[j] for j in range(i))
        y[i] = vector_permutado[i] - suma
        termino = f"(Pb)_{i + 1}" if pivoteo_parcial else f"b_{i + 1}"
        _registrar_paso(
            registrar_paso,
            f"y_{i + 1} = {termino} - ({formatear_valor(suma)}) "
            f"= {formatear_valor(y[i])} (diagonal de L igual a 1).",
            L, U, mostrar_matrices=False, vector=("y", y), P=P if pivoteo_parcial else None,
            objetivo=f"Calcular y_{i + 1} en la sustitución progresiva Ly=Pb.",
            fundamento="L es triangular inferior con diagonal unitaria, así que la incógnita actual queda aislada usando solo componentes anteriores.",
            procedimiento=f"y_{i + 1} = {termino} − {formatear_valor(suma)} = {formatear_valor(y[i])}.",
            resultado=f"La componente y_{i + 1} ya queda disponible para las filas siguientes.",
        )

    pivotes = []
    filas_pivote = []
    for i, fila in enumerate(U):
        columna = next((j for j, valor in enumerate(fila) if valor != 0), None)
        if columna is not None:
            pivotes.append(columna)
            filas_pivote.append(i)
    filas_cero_inconsistentes = [
        i for i, fila in enumerate(U)
        if all(valor == 0 for valor in fila) and y[i] != 0
    ]
    if filas_cero_inconsistentes:
        for i in filas_cero_inconsistentes:
            _registrar_paso(
                registrar_paso,
                f"Incompatibilidad: fila {i + 1} de U es cero, pero y_{i + 1} "
                f"= {formatear_valor(y[i])} ≠ 0; no existe solución.",
                L, U, mostrar_matrices=False, vector=("y", y), P=P if pivoteo_parcial else None,
                objetivo="Determinar si el sistema triangular es compatible.",
                fundamento="Una fila nula de U representa 0 en el lado izquierdo; su término independiente también debe ser cero.",
                procedimiento=f"En la fila {i + 1}, U es nula y y_{i + 1}={formatear_valor(y[i])}≠0.",
                resultado="La ecuación exigiría 0={formatear_valor(y[i])}; el sistema es incompatible.",
            )
        return {
            "P": P, "L": L, "U": U, "y": y, "estado": "incompatible",
            "rango": len(pivotes), "columnas_pivote": pivotes,
            "columnas_libres": [j for j in range(n) if j not in pivotes],
            "solucion_particular": None, "bases_nucleo": [],
            "verificacion": None,
        }

    columnas_libres = [j for j in range(n) if j not in pivotes]

    def sustituir(valores_libres, nombre, vector_rhs=None):
        vector_rhs = y if vector_rhs is None else vector_rhs
        solucion = [Fraction(0) for _ in range(n)]
        for columna, valor in valores_libres.items():
            solucion[columna] = valor
        for fila_indice, columna_pivote in reversed(list(zip(filas_pivote, pivotes))):
            suma = sum(
                U[fila_indice][j] * solucion[j]
                for j in range(columna_pivote + 1, n)
            )
            solucion[columna_pivote] = (
                vector_rhs[fila_indice] - suma
            ) / U[fila_indice][columna_pivote]
            _registrar_paso(
                registrar_paso,
                f"Despeje en fila {fila_indice + 1}: x_{columna_pivote + 1} = "
                f"({formatear_valor(vector_rhs[fila_indice])} - {formatear_valor(suma)}) / "
                f"{formatear_valor(U[fila_indice][columna_pivote])} "
                f"= {formatear_valor(solucion[columna_pivote])}.",
                L, U, mostrar_matrices=False, vector=(nombre, solucion), P=P if pivoteo_parcial else None,
                objetivo=f"Despejar x_{columna_pivote + 1} en sustitución regresiva.",
                fundamento="U es triangular superior; se recorren las filas desde abajo y se usan las variables ya despejadas.",
                procedimiento=f"x_{columna_pivote + 1} = ({formatear_valor(vector_rhs[fila_indice])} − {formatear_valor(suma)}) / {formatear_valor(U[fila_indice][columna_pivote])} = {formatear_valor(solucion[columna_pivote])}.",
                resultado=f"Se obtiene x_{columna_pivote + 1} = {formatear_valor(solucion[columna_pivote])}.",
            )
        return solucion

    particular = sustituir({}, "x₀")
    bases = []
    for indice, columna_libre in enumerate(columnas_libres, 1):
        bases.append(sustituir(
            {columna_libre: Fraction(1)}, f"v{indice}", [Fraction(0) for _ in range(m)]
        ))
    estado = "unica" if not columnas_libres else "infinitas"
    producto = [
        sum(matriz[i][j] * particular[j] for j in range(n)) for i in range(m)
    ]
    verificacion = producto == vector_original
    verificaciones_bases = [
        all(
            sum(matriz[i][j] * base[j] for j in range(n)) == 0
            for i in range(m)
        )
        for base in bases
    ]
    _registrar_paso(
        registrar_paso,
        "Verificación exacta Ax=b: " + ("se cumple." if verificacion else "no se cumple."),
        L, U, mostrar_matrices=False, vector=("Ax", producto), P=P if pivoteo_parcial else None,
        objetivo="Comprobar que la solución particular satisface el sistema original.",
        fundamento="Una solución de Ax=b debe reproducir b al multiplicar x por la matriz original A.",
        procedimiento=("Calcular Ax=(" + ", ".join(formatear_valor(v) for v in producto)
                       + ") y comparar con b=(" + ", ".join(formatear_valor(v) for v in vector_original) + ")."),
        resultado=("Ax=b; la solución satisface el sistema." if verificacion
                   else "Ax≠b; la solución no satisface el sistema."),
    )
    return {
        "P": P, "L": L, "U": U, "y": y, "estado": estado,
        "rango": len(pivotes), "columnas_pivote": pivotes,
        "columnas_libres": columnas_libres,
        "solucion_particular": particular, "bases_nucleo": bases,
        "verificacion": verificacion,
        "verificaciones_bases": verificaciones_bases,
    }
