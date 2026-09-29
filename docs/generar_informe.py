"""Genera el informe PDF del Módulo 2 usando solo la biblioteca estándar."""

from pathlib import Path


RAIZ = Path(__file__).resolve().parent


def escapar_texto_pdf(texto):
    """Codifica texto compatible con Helvetica y escapa delimitadores PDF."""
    datos = texto.encode("cp1252", errors="replace")
    return datos.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def agregar_texto(operaciones, x, y, texto, tamano=11, fuente="F1", color=(0, 0, 0)):
    """Agrega una línea de texto a una página PDF en coordenadas de puntos."""
    r, g, b = color
    operaciones.append(
        f"{r:.3f} {g:.3f} {b:.3f} rg BT /{fuente} {tamano} Tf "
        f"{x} {y} Td ".encode("ascii")
        + b"(" + escapar_texto_pdf(texto) + b") Tj ET\n"
    )


def agregar_rectangulo(operaciones, x, y, ancho, alto, color):
    """Pinta un rectángulo relleno, equivalente a una banda de portada."""
    r, g, b = color
    operaciones.append(
        f"q {r:.3f} {g:.3f} {b:.3f} rg {x} {y} {ancho} {alto} re f Q\n".encode("ascii")
    )


def flujo_pdf(operaciones):
    """Convierte operaciones de dibujo en el flujo de contenido de una página."""
    return b"".join(operaciones)


def objeto_stream(datos, diccionario=""):
    """Empaqueta bytes en un stream PDF con su longitud exacta."""
    cabecera = f"<< {diccionario} /Length {len(datos)} >>\nstream\n".encode("ascii")
    return cabecera + datos + b"\nendstream"


def escribir_pdf(destino, paginas):
    """Escribe páginas, fuentes e imágenes JPEG en un PDF válido sin dependencias."""
    objetos = [
        None,
        b"<< /Type /Catalog /Pages 2 0 R >>",
        None,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>",
    ]
    paginas_ids = []

    def agregar_objeto(objeto):
        """Añade un objeto indirecto y devuelve su identificador PDF."""
        objetos.append(objeto)
        return len(objetos) - 1

    for pagina in paginas:
        imagen_id = None
        if pagina.get("imagen"):
            jpeg = pagina["imagen"].read_bytes()
            imagen_id = agregar_objeto(objeto_stream(
                jpeg,
                "/Type /XObject /Subtype /Image /Width 1050 /Height 700 "
                "/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode",
            ))
        contenido_id = agregar_objeto(objeto_stream(flujo_pdf(pagina["operaciones"])))
        recursos = "/Font << /F1 3 0 R /F2 4 0 R >>"
        if imagen_id is not None:
            recursos += f" /XObject << /Im1 {imagen_id} 0 R >>"
        pagina_id = agregar_objeto(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << {recursos} >> /Contents {contenido_id} 0 R >>".encode("ascii")
        )
        paginas_ids.append(pagina_id)

    objetos[2] = (
        f"<< /Type /Pages /Kids [{' '.join(str(i) + ' 0 R' for i in paginas_ids)}] "
        f"/Count {len(paginas_ids)} >>"
    ).encode("ascii")

    salida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for identificador, objeto in enumerate(objetos[1:], 1):
        offsets.append(len(salida))
        salida.extend(f"{identificador} 0 obj\n".encode("ascii"))
        salida.extend(objeto)
        salida.extend(b"\nendobj\n")
    inicio_xref = len(salida)
    salida.extend(f"xref\n0 {len(objetos)}\n".encode("ascii"))
    salida.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        salida.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    salida.extend(
        f"trailer\n<< /Size {len(objetos)} /Root 1 0 R >>\n"
        f"startxref\n{inicio_xref}\n%%EOF\n".encode("ascii")
    )
    destino.write_bytes(salida)


def crear_portada():
    """Diseña la portada del informe con título, objetivo y datos académicos."""
    operaciones = []
    agregar_rectangulo(operaciones, 0, 590, 612, 202, (0.07, 0.20, 0.36))
    agregar_texto(operaciones, 48, 735, "PROGRAMA 4", 17, color=(1, 1, 1))
    agregar_texto(operaciones, 48, 686, "CALCULADORA DE ALGEBRA LINEAL", 23, color=(1, 1, 1))
    agregar_texto(operaciones, 48, 645, "Modulo 2: Vectores e Independencia Lineal", 16, color=(0.84, 0.91, 1))
    agregar_texto(operaciones, 48, 526, "INFORME TECNICO", 15, color=(0.07, 0.20, 0.36))
    agregar_texto(operaciones, 48, 485, "Tema: prueba computacional de independencia lineal", 12)
    agregar_texto(operaciones, 48, 445, "Metodo: sistema homogeneo A*c=0 y reduccion Gauss-Jordan", 12)
    agregar_texto(operaciones, 48, 378, "Estudiante(s): __________________________________________", 12)
    agregar_texto(operaciones, 48, 344, "Asignatura: Algebra Lineal", 12)
    agregar_texto(operaciones, 48, 310, "Fecha: 28 de septiembre de 2026", 12)
    agregar_rectangulo(operaciones, 48, 252, 516, 2, (0.12, 0.43, 0.70))
    agregar_texto(operaciones, 48, 222, "Implementacion modular con CustomTkinter y Fraction.", 11, color=(0.25, 0.30, 0.36))
    return {"operaciones": operaciones}


def crear_pagina_logica():
    """Explica la construcción y la decisión matemática del algoritmo."""
    operaciones = []
    agregar_texto(operaciones, 45, 750, "LOGICA DEL MODULO 2", 18, color=(0.07, 0.20, 0.36))
    lineas = [
        ("OBJETIVO", 715, 13),
        ("Determinar si v1,...,vk son linealmente independientes en R^n.", 694, 10),
        ("", 676, 10),
        ("1. MATRIZ DE COLUMNAS", 655, 13),
        ("Los vectores ingresados se organizan como columnas de A (n por k).", 634, 10),
        ("Cada fila representa una coordenada; cada columna, un vector.", 616, 10),
        ("", 598, 10),
        ("2. SISTEMA HOMOGENEO", 577, 13),
        ("Se plantea A*c=0, es decir c1*v1 + ... + ck*vk = 0.", 556, 10),
        ("La independencia exige que la unica solucion sea c=0.", 538, 10),
        ("", 520, 10),
        ("3. REDUCCION POR FILAS", 499, 13),
        ("Se aplica Gauss-Jordan manualmente con Fraction y listas.", 478, 10),
        ("Se buscan pivotes, se intercambian filas y se eliminan entradas.", 460, 10),
        ("Las operaciones elementales conservan el conjunto de soluciones.", 442, 10),
        ("", 424, 10),
        ("4. VEREDICTO", 403, 13),
        ("Si hay k pivotes, no hay variables libres: los vectores son L.I.", 382, 10),
        ("Si pivotes<k, hay soluciones no triviales: los vectores son L.D.", 364, 10),
        ("Si k>n, el conjunto es L.D. porque rango(A)<=n<k.", 346, 10),
        ("", 328, 10),
        ("RESTRICCIONES", 307, 13),
        ("No se utilizan NumPy, SciPy ni operaciones matriciales automaticas.", 286, 10),
        ("CustomTkinter se usa para la interfaz; Fraction conserva exactitud.", 268, 10),
        ("", 248, 10),
        ("PRUEBAS", 227, 13),
        ("Caso L.I.: {(1,0),(0,1)}; rango 2, dos pivotes y cero libres.", 206, 10),
        ("Caso L.D.: {(1,2),(2,4)}; rango 1, un pivote y una libre.", 188, 10),
    ]
    for texto, y, size in lineas:
        if texto:
            agregar_texto(operaciones, 48, y, texto, size, color=(0.07, 0.20, 0.36) if size == 13 else (0.12, 0.14, 0.18))
    return {"operaciones": operaciones}


def crear_pagina_captura(ruta_imagen, titulo, descripcion, ejemplo):
    """Crea una página explicativa que incluye una captura real de la GUI."""
    operaciones = []
    agregar_texto(operaciones, 42, 755, titulo, 17, color=(0.07, 0.20, 0.36))
    agregar_texto(operaciones, 42, 727, descripcion, 10)
    agregar_texto(operaciones, 42, 706, ejemplo, 10, fuente="F2")
    operaciones.append(b"q 536 0 0 357 38 315 cm /Im1 Do Q\n")
    agregar_texto(operaciones, 42, 285, "La salida muestra matriz reducida, pivotes, variables libres y veredicto.", 10)
    return {"operaciones": operaciones, "imagen": ruta_imagen}


def generar_informe():
    """Compone el PDF con portada, explicación y casos de prueba L.I. y L.D."""
    capturas = RAIZ / "capturas"
    salida = RAIZ / "Informe_Programa_4.pdf"
    paginas = [
        crear_portada(),
        crear_pagina_logica(),
        crear_pagina_captura(
            capturas / "caso_LI.jpg",
            "CASO DE PRUEBA: VECTORES L.I.",
            "Vectores de la base canonica en R^2; son independientes.",
            "v1=(1,0), v2=(0,1); rango=2, pivotes=2, variables libres=0.",
        ),
        crear_pagina_captura(
            capturas / "caso_LD.jpg",
            "CASO DE PRUEBA: VECTORES L.D.",
            "El segundo vector es dos veces el primero; existe dependencia.",
            "v1=(1,2), v2=(2,4); rango=1, pivotes=1, variable libre=1.",
        ),
    ]
    escribir_pdf(salida, paginas)
    print("Informe creado:", salida)


if __name__ == "__main__":
    generar_informe()
