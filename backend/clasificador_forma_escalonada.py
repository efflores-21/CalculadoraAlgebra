"""Clasificación exacta de matrices en forma escalonada (REF) y reducida (RREF)."""

from fractions import Fraction

from backend.matriz import _a_fraction, formatear_valor


def clasificar_forma_escalonada(matriz):
    """Comprueba las condiciones de REF/RREF y devuelve datos para explicarlas.

    Las posiciones de ``posiciones_pivote`` y ``filas_nulas`` son 1-based,
    apropiadas para mostrarlas a una persona. ``columnas_pivote`` conserva la
    convención 0-based de ``backend.clasificador.columnas_pivote``.
    Los valores se convierten a :class:`Fraction` antes de comprobar ceros o unos.
    """
    if matriz is None or not matriz:
        raise ValueError("La matriz no puede estar vacía.")

    columnas = None
    datos = []
    for indice, fila in enumerate(matriz, 1):
        if fila is None:
            raise ValueError(f"La fila {indice} de la matriz no puede estar vacía.")
        try:
            ancho = len(fila)
        except TypeError as error:
            raise ValueError(f"La fila {indice} debe ser una secuencia de valores numéricos.") from error
        if ancho == 0:
            raise ValueError(f"La fila {indice} de la matriz no puede estar vacía.")
        if columnas is None:
            columnas = ancho
        elif ancho != columnas:
            raise ValueError("La matriz debe ser rectangular: todas las filas deben tener el mismo número de columnas.")
        datos.append([_a_fraction(valor) for valor in fila])

    filas = len(datos)
    posiciones = []
    filas_nulas = []
    for i, fila in enumerate(datos):
        columna_pivote = next((j for j, valor in enumerate(fila) if valor != 0), None)
        if columna_pivote is None:
            filas_nulas.append(i + 1)
        else:
            posiciones.append({
                "fila": i + 1,
                "columna": columna_pivote + 1,
                "valor": fila[columna_pivote],
            })

    violaciones_orden = [
        (anterior, actual)
        for anterior, actual in zip(posiciones, posiciones[1:])
        if actual["columna"] <= anterior["columna"]
    ]
    filas_nulas_antes = [
        (fila_nula, posicion["fila"])
        for fila_nula in filas_nulas
        for posicion in posiciones
        if fila_nula < posicion["fila"]
    ]
    elementos_debajo = [
        {"fila": i + 1, "columna": pivote["columna"], "valor": datos[i][pivote["columna"] - 1]}
        for pivote in posiciones
        for i in range(pivote["fila"], filas)
        if datos[i][pivote["columna"] - 1] != 0
    ]
    filas_nulas_al_final = not filas_nulas_antes
    pivotes_avanzan = not violaciones_orden
    ceros_debajo = not elementos_debajo

    pivotes_no_unitarios = [p for p in posiciones if p["valor"] != 1]
    otros_en_columna = [
        {"fila": i + 1, "columna": pivote["columna"], "valor": datos[i][pivote["columna"] - 1]}
        for pivote in posiciones
        for i in range(filas)
        if i + 1 != pivote["fila"] and datos[i][pivote["columna"] - 1] != 0
    ]

    condiciones = {
        "filas_nulas_al_final": {
            "cumple": filas_nulas_al_final,
            "explicacion": (
                "Todas las filas nulas están debajo de las filas no nulas."
                if filas_nulas_al_final else
                "Hay una fila nula antes de una fila no nula: " + ", ".join(
                    f"fila {nula} antes de fila {no_nula}" for nula, no_nula in filas_nulas_antes
                ) + "."
            ),
        },
        "pivotes_avanzan_derecha": {
            "cumple": pivotes_avanzan,
            "explicacion": (
                "El pivote de cada fila no nula está a la derecha del pivote anterior."
                if pivotes_avanzan else
                "Los pivotes no avanzan estrictamente a la derecha: " + "; ".join(
                    f"fila {actual['fila']} (columna {actual['columna']}) no queda a la derecha "
                    f"de fila {anterior['fila']} (columna {anterior['columna']})"
                    for anterior, actual in violaciones_orden
                ) + "."
            ),
        },
        "ceros_debajo_pivotes": {
            "cumple": ceros_debajo,
            "explicacion": (
                "Debajo de cada pivote hay únicamente ceros."
                if ceros_debajo else
                "Hay entradas no nulas debajo de pivotes: " + ", ".join(
                    f"({dato['fila']}, {dato['columna']}) = {formatear_valor(dato['valor'])}"
                    for dato in elementos_debajo
                ) + "."
            ),
        },
    }
    es_ref = all(condicion["cumple"] for condicion in condiciones.values())
    condiciones["cumple_ref"] = {
        "cumple": es_ref,
        "explicacion": "La matriz cumple las tres condiciones de REF." if es_ref
        else "La matriz no cumple REF porque falla al menos una de sus tres condiciones.",
    }
    condiciones["pivotes_iguales_a_uno"] = {
        "cumple": not pivotes_no_unitarios,
        "explicacion": "Todos los pivotes son 1." if not pivotes_no_unitarios else
        "Estos pivotes no son 1: " + ", ".join(
            f"({p['fila']}, {p['columna']}) = {formatear_valor(p['valor'])}"
            for p in pivotes_no_unitarios
        ) + ".",
    }
    condiciones["pivotes_unicos_en_columna"] = {
        "cumple": not otros_en_columna,
        "explicacion": "Cada pivote es el único elemento no nulo de su columna." if not otros_en_columna else
        "Hay otros elementos no nulos en columnas pivote: " + ", ".join(
            f"({dato['fila']}, {dato['columna']}) = {formatear_valor(dato['valor'])}"
            for dato in otros_en_columna
        ) + ".",
    }
    es_rref = es_ref and condiciones["pivotes_iguales_a_uno"]["cumple"] \
        and condiciones["pivotes_unicos_en_columna"]["cumple"]

    incumplimientos = [
        {"codigo": codigo, "explicacion": condicion["explicacion"]}
        for codigo, condicion in condiciones.items()
        if not condicion["cumple"]
    ]
    if not es_ref:
        conclusion = "La matriz no está en REF ni en RREF, porque toda matriz RREF debe cumplir REF."
    elif es_rref:
        conclusion = "La matriz está en REF y también en RREF: sus pivotes son 1 y únicos en sus columnas."
    else:
        conclusion = "La matriz está en REF, pero no en RREF: " + " ".join(
            condiciones[codigo]["explicacion"]
            for codigo in ("pivotes_iguales_a_uno", "pivotes_unicos_en_columna")
            if not condiciones[codigo]["cumple"]
        )

    return {
        "filas": filas,
        "columnas": columnas,
        "dimensiones": (filas, columnas),
        "numero_pivotes": len(posiciones),
        "posiciones_pivote": posiciones,
        "columnas_pivote": [pivote["columna"] - 1 for pivote in posiciones],
        "filas_nulas": filas_nulas,
        "es_ref": es_ref,
        "es_rref": es_rref,
        "condiciones": condiciones,
        "incumplimientos": incumplimientos,
        "conclusion": conclusion,
        "matriz": datos,
    }
