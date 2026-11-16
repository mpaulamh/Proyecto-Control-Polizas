"""Capa controlador: rutas de Flask (Blueprint). No calcula."""

import io
import zipfile

from flask import Blueprint, render_template, send_file, abort

from models.polizas import (
    calcular_resultados,
    contar_por_estado,
    primas_por_aseguradora,
    buscar_inconsistencias,
    FECHA_CORTE,
    buscar_por_numero,
)
from services.generador_aviso import crear_aviso_pdf

polizas_bp = Blueprint("polizas", __name__)


@polizas_bp.route("/")
def inicio():
    """Tablero principal: resultados, conteo, primas, inconsistencias y fecha de corte."""
    resultados = calcular_resultados()
    conteo = contar_por_estado(resultados)
    primas = primas_por_aseguradora(resultados)
    inconsistencias = buscar_inconsistencias(resultados)
    return render_template(
        "inicio.html",
        resultados=resultados,
        conteo=conteo,
        primas=primas,
        inconsistencias=inconsistencias,
        fecha_corte=FECHA_CORTE,
    )


@polizas_bp.route("/aviso/<numero>")
def aviso(numero):
    """Devuelve el PDF de aviso de la póliza solicitada; 404 si no existe o está Vigente."""
    poliza = buscar_por_numero(numero)
    if poliza is None:
        abort(404)
    if poliza.get("estado") == "Vigente":
        abort(404)

    pdf_bytes = crear_aviso_pdf(poliza)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"aviso_{numero}.pdf",
    )


@polizas_bp.route("/descargar-avisos")
def descargar_avisos():
    """Arma en memoria un .zip con los avisos de pólizas Por vencer y Vencidas."""
    resultados = calcular_resultados()
    avisos = [
        r for r in resultados if r.get("estado") in ("Por vencer", "Vencida")
    ]

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in avisos:
            pdf_bytes = crear_aviso_pdf(r)
            nombre_archivo = f"aviso_{r.get('numero', 'desconocida')}.pdf"
            zf.writestr(nombre_archivo, pdf_bytes)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="avisos.zip",
    )
