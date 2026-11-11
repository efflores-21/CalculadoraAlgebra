"""Descomposición exacta y conversión de enteros entre base decimal y binaria."""


def _digitos_y_suma(valor, base):
    magnitud = abs(valor)
    digitos = str(magnitud) if base == 10 else format(magnitud, "b")
    terminos, parciales = [], []
    for indice, digito in enumerate(digitos):
        potencia = len(digitos) - indice - 1
        cifra = int(digito)
        terminos.append(f"{cifra} × {base}^{potencia}")
        parciales.append(cifra * (base ** potencia))
    signo = "-" if valor < 0 else ""
    return {
        "valor": valor, "base": base, "digitos": digitos, "descomposicion": signo + " + ".join(terminos),
        "parciales": parciales, "suma": sum(parciales), "signo": signo,
    }


def descomponer_decimal(valor):
    """Expresa un entero decimal como suma de dígitos por potencias de diez."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError("El valor decimal debe ser un número entero.")
    return _digitos_y_suma(valor, 10)


def decimal_a_binario(valor):
    """Devuelve la representación binaria y la descomposición posicional decimal."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError("El valor decimal debe ser un número entero.")
    resultado = _digitos_y_suma(valor, 2)
    resultado["binario"] = resultado["signo"] + format(abs(valor), "b")
    resultado["decimal"] = valor
    resultado["equivalente"] = int(resultado["binario"], 2) if valor >= 0 else -int(resultado["binario"][1:], 2)
    return resultado


def binario_a_decimal(texto):
    """Valida dígitos binarios, convierte a entero y devuelve la descomposición."""
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Ingrese un número binario.")
    normalizado = texto.strip()
    signo = -1 if normalizado.startswith("-") else 1
    digitos = normalizado[1:] if normalizado[:1] in "+-" else normalizado
    if not digitos or any(digito not in "01" for digito in digitos):
        raise ValueError("El número binario solo puede contener los dígitos 0 y 1, además del signo opcional.")
    valor = signo * int(digitos, 2)
    datos = _digitos_y_suma(valor, 2)
    datos.update({"binario": ("-" if valor < 0 else "") + digitos, "decimal": valor,
                  "equivalente": valor})
    return datos
