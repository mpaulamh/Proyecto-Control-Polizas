"""Capa modelo: acceso a archivos (solo lectura de data/)."""

import os
from datetime import datetime

import pandas as pd
import pdfplumber

DATA_DIR = "data"
CLIENTES_XLSX = os.path.join(DATA_DIR, "Maestro_Clientes.xlsx")
POLIZAS_DIR = os.path.join(DATA_DIR, "polizas")

# Mapeo: etiqueta tal como aparece en el PDF -> nombre del campo del diccionario
CAMPOS = {
    "Numero de poliza": "numero",
    "Ramo": "ramo",
    "Tomador / Asegurado": "nombre",
    "Cedula": "cedula",
    "Vigencia desde": "desde",
    "Vigencia hasta": "hasta",
    "Prima anual": "prima",
    "Forma de pago": "pago",
    "Suma asegurada": "suma",
    "Asesor": "asesor",
}


def _texto_a_fecha(valor):
    """Convierte 'dd/mm/aaaa' a objeto date. Devuelve None si está vacío."""
    if valor is None or str(valor).strip() == "":
        return None
    return datetime.strptime(str(valor).strip(), "%d/%m/%Y").date()


def _texto_a_numero(valor):
    """Convierte monto tipo 'CRC 228,000.00' a float. Devuelve None si vacío."""
    if valor is None or str(valor).strip() == "":
        return None
    texto = str(valor).strip()
    texto = texto.replace("CRC", "").replace("$", "").replace(",", "").strip()
    try:
        return float(texto)
    except ValueError:
        return None


def cargar_clientes():
    """Lee el Excel de clientes y devuelve un DataFrame con Cedula como texto sin espacios."""
    df = pd.read_excel(CLIENTES_XLSX, sheet_name="Clientes")
    df["Cedula"] = df["Cedula"].astype(str).str.strip()
    return df


def leer_poliza(ruta_pdf):
    """Abre un PDF de póliza y devuelve un diccionario con sus datos."""
    nombre_archivo = os.path.basename(ruta_pdf)

    resultado = {
        "archivo": nombre_archivo,
        "aseguradora": None,
        "numero": None,
        "ramo": None,
        "nombre": None,
        "cedula": None,
        "desde": None,
        "hasta": None,
        "prima": None,
        "pago": None,
        "suma": None,
        "asesor": None,
    }

    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        texto = pagina.extract_text() or ""

    lineas = texto.split("\n")
    if not lineas:
        return resultado

    # Primera línea: nombre de la aseguradora
    resultado["aseguradora"] = lineas[0].strip()

    # Recorrer las demás líneas buscando "Etiqueta: valor"
    for linea in lineas[1:]:
        if ":" in linea:
            etiqueta, valor = linea.split(":", 1)
            etiqueta = etiqueta.strip()
            valor = valor.strip()
            if etiqueta in CAMPOS:
                campo = CAMPOS[etiqueta]
                if campo in ("desde", "hasta"):
                    resultado[campo] = _texto_a_fecha(valor)
                elif campo in ("prima", "suma"):
                    resultado[campo] = _texto_a_numero(valor)
                else:
                    resultado[campo] = valor

    return resultado


def cargar_polizas():
    """Recorre data/polizas en orden alfabético y devuelve una lista de diccionarios."""
    polizas = []
    if not os.path.isdir(POLIZAS_DIR):
        return polizas

    archivos = sorted(
        f for f in os.listdir(POLIZAS_DIR) if f.lower().endswith(".pdf")
    )
    for archivo in archivos:
        ruta = os.path.join(POLIZAS_DIR, archivo)
        polizas.append(leer_poliza(ruta))

    return polizas
