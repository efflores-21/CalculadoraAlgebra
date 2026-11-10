"""Muestreo de funciones reales y separación de segmentos para trazado seguro."""

import math

from backend.funciones import compilar_funcion


def muestrear_funcion(expresion, x_min, x_max, cantidad=1200, limites_y=None):
    """Devuelve puntos y segmentos, omitiendo dominios inválidos y saltos grandes."""
    funcion = compilar_funcion(expresion)
    try:
        x_min, x_max = float(x_min), float(x_max)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Los límites x deben ser números reales finitos.") from error
    if not math.isfinite(x_min) or not math.isfinite(x_max) or x_min >= x_max:
        raise ValueError("El límite inferior debe ser finito y menor que el superior.")
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not 1000 <= cantidad <= 10000:
        raise ValueError("La cantidad de puntos debe ser un entero entre 1000 y 10000.")
    if limites_y is not None:
        y_min, y_max = map(float, limites_y)
        if not math.isfinite(y_min) or not math.isfinite(y_max) or y_min >= y_max:
            raise ValueError("Los límites verticales deben ser finitos y el mínimo menor que el máximo.")
    else:
        y_min = y_max = None

    dx = (x_max - x_min) / (cantidad - 1)
    puntos, valores_y = [], []
    for indice in range(cantidad):
        x = x_min + indice * dx
        try:
            y = funcion(x)
            if limites_y is not None and not y_min <= y <= y_max:
                puntos.append(None)
                continue
            puntos.append((x, y))
            valores_y.append(y)
        except ValueError:
            puntos.append(None)

    # IQR es resistente a los valores enormes junto a una asíntota.
    ordenados = sorted(valores_y)
    if len(ordenados) >= 4:
        q1 = ordenados[len(ordenados) // 4]
        q3 = ordenados[(3 * len(ordenados)) // 4]
        umbral_salto = max(1e-12, 4.0 * (q3 - q1))
    else:
        umbral_salto = 0.0

    segmentos, actual = [], []
    for punto in puntos:
        if punto is None or (actual and abs(punto[1] - actual[-1][1]) > umbral_salto):
            if len(actual) >= 2:
                segmentos.append(actual)
            actual = []
            if punto is None:
                continue
        actual.append(punto)
    if len(actual) >= 2:
        segmentos.append(actual)
    return {"puntos": puntos, "segmentos": segmentos, "x_min": x_min, "x_max": x_max,
            "y_min": y_min if limites_y is not None else None,
            "y_max": y_max if limites_y is not None else None}
