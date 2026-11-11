"""Cálculos de errores numéricos y ejemplos de representación en punto flotante."""

import math
import sys


def _finito(valor, nombre):
    try:
        valor = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número real finito.") from error
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    return valor


def calcular_errores(verdadero, aproximado):
    """Calcula errores absoluto, relativo y porcentual sin dividir entre cero."""
    verdadero = _finito(verdadero, "El valor verdadero")
    aproximado = _finito(aproximado, "El valor aproximado")
    absoluto = abs(verdadero - aproximado)
    if not math.isfinite(absoluto):
        raise ValueError("La diferencia entre los valores excede el rango finito de float.")
    relativo = absoluto / abs(verdadero) if verdadero != 0 else None
    return {"verdadero": verdadero, "aproximado": aproximado, "absoluto": absoluto,
            "relativo": relativo, "porcentual": relativo * 100 if relativo is not None else None}


def analizar_punto_flotante():
    """Genera ejemplos reproducibles de redondeo, épsilon, overflow y underflow."""
    suma = 0.1 + 0.2
    overflow = 1e308 * 1e308
    underflow = 1e-300 * 1e-300
    perdida = (1e16 + 1.0) - 1e16
    return {
        "suma": suma, "suma_repr": repr(suma), "igual_a_03": suma == 0.3,
        "diferencia": suma - 0.3, "epsilon": sys.float_info.epsilon,
        "epsilon_explicacion": "Distancia entre 1.0 y el siguiente float representable; no es la precisión relativa uniforme para cualquier magnitud.",
        "overflow": overflow, "overflow_es_finito": math.isfinite(overflow),
        "underflow": underflow, "perdida": perdida,
        "razon_binaria": "Algunas fracciones decimales, como 1/10, tienen expansión binaria infinita y se almacenan redondeadas.",
    }


def propagar_error(x, delta_x):
    """Compara el cambio real de sin(x)+x² con la linealización f'(x)·Δx."""
    x, delta_x = _finito(x, "x"), _finito(delta_x, "La perturbación Δx")
    x_perturbado = x + delta_x
    if not math.isfinite(x_perturbado):
        raise ValueError("x + Δx excede el rango finito de float.")
    try:
        original = math.sin(x) + x ** 2
        perturbado = math.sin(x_perturbado) + x_perturbado ** 2
    except (ValueError, OverflowError) as error:
        raise ValueError("La función no puede evaluarse finitamente para esos valores.") from error
    real = perturbado - original
    derivada = math.cos(x) + 2 * x
    aproximado = derivada * delta_x
    if not all(math.isfinite(valor) for valor in (original, perturbado, real, derivada, aproximado)):
        raise ValueError("El cálculo de propagación excede el rango finito de float.")
    return {"x": x, "delta_x": delta_x, "f_x": original, "f_perturbado": perturbado,
            "delta_y_real": real, "derivada": derivada, "delta_y_aproximado": aproximado,
            "diferencia_absoluta": abs(real - aproximado)}


def resumen_tipos_error():
    """Devuelve definiciones breves que distinguen fuentes de error numéricas y de modelo."""
    return [
        ("Inherente", "Incertidumbre ya presente en los datos de entrada, por ejemplo una longitud medida con resolución limitada."),
        ("Redondeo", "Diferencia al representar o redondear un valor finito, como 0.1 en binario de precisión finita."),
        ("Truncamiento", "Error al reemplazar un proceso infinito por uno finito, como cortar una serie de Taylor."),
        ("Modelado", "Diferencia entre el fenómeno real y sus ecuaciones idealizadas; no se elimina aumentando la precisión aritmética."),
        ("Absoluto", "|valor verdadero − valor aproximado|."),
        ("Relativo", "Error absoluto dividido entre |valor verdadero|; no está definido si el valor verdadero es cero."),
    ]
