"""Método de bisección con traza de iteraciones y criterios de parada explícitos."""

import math

from backend.funciones import compilar_funcion


def _finito(valor, nombre):
    try:
        convertido = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número real finito.") from error
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    return convertido


def iteraciones_teoricas(a, b, tolerancia):
    """Calcula ceil(log2((b-a)/E)), con cero iteraciones si la cota inicial basta."""
    ancho = b - a
    if not math.isfinite(ancho):
        raise ValueError("El ancho del intervalo debe ser finito.")
    exponente = math.log2(ancho) - math.log2(tolerancia)
    return max(0, math.ceil(exponente))


def resolver_biseccion(expresion, a, b, tolerancia, max_iteraciones):
    """Resuelve una raíz mediante bisección y devuelve resumen y tabla de pasos."""
    a, b = _finito(a, "El extremo a"), _finito(b, "El extremo b")
    tolerancia = _finito(tolerancia, "La tolerancia")
    if a >= b:
        raise ValueError("El extremo inferior a debe ser menor que b.")
    if not math.isfinite(b - a):
        raise ValueError("La distancia entre los extremos excede el rango numérico finito.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia absoluta debe ser positiva.")
    if isinstance(max_iteraciones, bool) or not isinstance(max_iteraciones, int) or not 1 <= max_iteraciones <= 10000:
        raise ValueError("El máximo de iteraciones debe ser un entero entre 1 y 10000.")

    funcion = compilar_funcion(expresion)
    fa, fb = funcion(a), funcion(b)
    teoricas = iteraciones_teoricas(a, b, tolerancia)
    advertencia = (
        "El cambio de signo no demuestra continuidad. Verifique que la función sea continua "
        "en todo el intervalo para aplicar el teorema de Bolzano."
    )
    if fa == 0 or fb == 0:
        raiz = a if fa == 0 else b
        return {
            "raiz": raiz, "f_raiz": 0.0, "iteraciones": 0,
            "intervalo_final": (raiz, raiz), "cota_error": 0.0,
            "error_absoluto_aprox": None, "error_relativo": None,
            "iteraciones_teoricas": teoricas, "motivo": "Raíz exacta en un extremo.",
            "alcanzada_tolerancia": True, "tabla": [], "advertencia": advertencia,
        }
    if (fa < 0) == (fb < 0):
        raise ValueError(
            "El intervalo no presenta cambio de signo: f(a) y f(b) tienen el mismo signo. "
            "Esto no permite concluir que no haya raíces en otros intervalos."
        )

    tabla, anterior = [], None
    for k in range(1, max_iteraciones + 1):
        a_usado, b_usado, fa_usado, fb_usado = a, b, fa, fb
        xr = a_usado / 2.0 + b_usado / 2.0
        cota = (b_usado - a_usado) / 2.0
        try:
            fr = funcion(xr)
        except ValueError as error:
            raise ValueError(
                f"No se pudo evaluar f(x) dentro del intervalo en x={xr:g}. "
                "El cambio de signo puede deberse a una discontinuidad o a una restricción de dominio. "
                "Verifique la continuidad antes de aplicar bisección."
            ) from error
        error_aprox = None if anterior is None else abs(xr - anterior)
        error_relativo_aprox = (
            None if anterior is None or xr == 0 else abs((xr - anterior) / xr)
        )
        if fr == 0:
            siguiente = (a_usado, b_usado)
            motivo = "Raíz exacta en aritmética de punto flotante."
            alcanzada = True
        elif cota <= tolerancia:
            siguiente = (a_usado, b_usado)
            motivo = "Se alcanzó la tolerancia mediante la cota del semiancho."
            alcanzada = True
        elif (fa_usado < 0) != (fr < 0):
            siguiente = (a_usado, xr)
            motivo = "Se conserva [a, xr] porque sus extremos tienen signos opuestos."
            alcanzada = False
        else:
            siguiente = (xr, b_usado)
            motivo = "Se conserva [xr, b] porque sus extremos tienen signos opuestos."
            alcanzada = False
        tabla.append({
            "k": k, "a": a_usado, "b": b_usado, "fa": fa_usado, "fb": fb_usado,
            "xr": xr, "fr": fr, "cota_error": cota,
            "error_absoluto_aprox": error_aprox,
            "error_relativo_aprox": error_relativo_aprox,
            "intervalo_siguiente": siguiente,
            "decision": motivo,
        })
        if fr == 0 or cota <= tolerancia:
            intervalo_final = (a_usado, b_usado)
            break
        anterior = xr
        a, b = siguiente
        fa, fb = (fa_usado, fr) if siguiente[1] == xr else (fr, fb_usado)
    else:
        alcanzada = False
        motivo = "Se alcanzó el máximo de iteraciones sin garantizar la tolerancia solicitada."
        ultima = tabla[-1]
        intervalo_final = ultima["intervalo_siguiente"]
        xr, fr, cota = ultima["xr"], ultima["fr"], ultima["cota_error"]

    return {
        "raiz": xr, "f_raiz": fr, "iteraciones": len(tabla),
        "intervalo_final": intervalo_final, "cota_error": cota,
        "error_absoluto_aprox": tabla[-1]["error_absoluto_aprox"],
        "error_relativo": None, "iteraciones_teoricas": teoricas,
        "motivo": motivo, "alcanzada_tolerancia": alcanzada,
        "tabla": tabla, "advertencia": advertencia,
    }
