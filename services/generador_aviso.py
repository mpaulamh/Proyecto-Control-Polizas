"""Capa servicio: generación de avisos de renovación en PDF con fpdf2."""

from fpdf import FPDF

ROJO = (174, 24, 0)        # #AE1800
NEGRO = (32, 30, 29)       # #201E1D
GRIS_CLARO = (243, 242, 242)  # #F3F2F2
GRIS_PIE = (150, 150, 150)


def _to_latin1(texto):
    """Convierte texto a latin-1 para evitar fallos con tildes en Helvetica."""
    if texto is None:
        return ""
    return str(texto).encode("latin-1", "replace").decode("latin-1")


def _fecha_a_str(fecha):
    """Convierte date a 'dd/mm/aaaa' o None."""
    if fecha is None:
        return None
    return fecha.strftime("%d/%m/%Y")


def _moneda_a_str(valor):
    """Convierte prima a 'CRC 228,000.00' o 'No registrada'."""
    if valor is None:
        return "No registrada"
    return f"CRC {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class AvisoPDF(FPDF):
    """PDF con pie de página gris y documento ficticio académico."""

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRIS_PIE)
        self.cell(
            0,
            10,
            _to_latin1("Documento ficticio de uso académico - Control de Pólizas"),
            align="C",
        )


def crear_aviso_pdf(poliza):
    """Crea un aviso de renovación en PDF (A4 vertical) y lo devuelve en bytes."""
    pdf = AvisoPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    nombre = _to_latin1(poliza.get("nombre") or "Cliente")
    numero = _to_latin1(poliza.get("numero") or "")
    aseguradora = _to_latin1(poliza.get("aseguradora") or "")
    ramo = _to_latin1(poliza.get("ramo") or "")
    cedula = _to_latin1(poliza.get("cedula") or "")
    desde = _fecha_a_str(poliza.get("desde"))
    hasta = _fecha_a_str(poliza.get("hasta"))
    prima = poliza.get("prima")
    pago = _to_latin1(poliza.get("pago") or "")
    asesor = _to_latin1(poliza.get("asesor") or "")
    estado = poliza.get("estado") or ""
    dias = poliza.get("dias_hasta_vencer")

    # --- Banda superior roja ---
    pdf.set_fill_color(*ROJO)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(
        0,
        14,
        _to_latin1("CORREDORA DE SEGUROS HORIZONTE"),
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
        fill=True,
    )
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0,
        10,
        _to_latin1("AVISO DE RENOVACIÓN DE PÓLIZA"),
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
        fill=True,
    )
    pdf.ln(8)

    # --- Saludo ---
    pdf.set_text_color(*NEGRO)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, _to_latin1(f"Estimado(a) {nombre}:"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- Párrafo según estado ---
    pdf.set_font("Helvetica", "", 11)
    if estado == "Vencida":
        fecha_venc = _fecha_a_str(poliza.get("hasta")) or "fecha desconocida"
        texto = f"Su póliza número {numero} venció el {fecha_venc}. Por favor renueve lo antes posible."
    elif estado == "Por vencer":
        fecha_vence = _fecha_a_str(poliza.get("hasta")) or "fecha desconocida"
        texto = (
            f"Su póliza número {numero} vence el {fecha_vence} (en {dias} días). "
            f"Su asesor {asesor} se comunicará con usted para gestionar la renovación."
        )
    elif estado == "Vigente":
        texto = f"Su póliza número {numero} está vigente. Este aviso es informativo."
    else:
        texto = f"Su póliza número {numero} tiene estado: {estado}."
    pdf.multi_cell(0, 6, _to_latin1(texto))
    pdf.ln(6)

    # --- Tabla ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*GRIS_CLARO)
    pdf.set_text_color(*NEGRO)
    ancho_col = 60
    pdf.cell(ancho_col, 8, _to_latin1("Campo"), border=1, fill=True)
    pdf.cell(
        ancho_col,
        8,
        _to_latin1("Valor"),
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
        fill=True,
    )

    filas = [
        ("Número de póliza", numero),
        ("Aseguradora", aseguradora),
        ("Ramo", ramo),
        ("Cédula", cedula),
        (
            "Vigencia",
            f"{desde} al {hasta}" if desde and hasta else (desde or hasta or "No registrada"),
        ),
        ("Prima anual", _moneda_a_str(prima)),
        ("Forma de pago", pago),
    ]

    pdf.set_font("Helvetica", "", 10)
    for campo, valor in filas:
        pdf.cell(ancho_col, 7, _to_latin1(campo), border=1)
        pdf.cell(
            ancho_col,
            7,
            _to_latin1(valor),
            border=1,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(6)

    # --- Asesor asignado ---
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, _to_latin1(f"Asesor asignado: {asesor}"), new_x="LMARGIN", new_y="NEXT")

    # --- Salida a bytes ---
    salida = pdf.output(dest="S")
    if isinstance(salida, bytearray):
        return bytes(salida)
    return salida
