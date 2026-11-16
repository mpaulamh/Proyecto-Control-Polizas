"""Capa modelo: reglas del negocio para pólizas."""

from collections import defaultdict
from datetime import date

from models.datos import cargar_clientes, cargar_polizas

# Constantes de negocio (según instrucción del usuario; AGENTS.md indica 2 de noviembre)
FECHA_CORTE = date(2026, 11, 9)
DIAS_AVISO = 30


def estado_poliza(hasta, fecha_corte=FECHA_CORTE):
    """Devuelve 'Vencida', 'Por vencer', 'Vigente' o 'Sin fecha'."""
    if hasta is None:
        return "Sin fecha"
    if hasta < fecha_corte:
        return "Vencida"
    dias = (hasta - fecha_corte).days
    if 0 <= dias <= DIAS_AVISO:
        return "Por vencer"
    return "Vigente"


def calcular_resultados(fecha_corte=FECHA_CORTE):
    """Cruza pólizas con el maestro por cédula, calcula días y estado, y devuelve lista ordenada."""
    polizas = cargar_polizas()
    clientes = cargar_clientes()

    # Indexar clientes por cédula (texto sin espacios)
    clientes_por_cedula = {}
    for _, row in clientes.iterrows():
        ced = str(row["Cedula"]).strip()
        clientes_por_cedula[ced] = row

    # Detectar columna de correo en el maestro
    col_correo = None
    for col in clientes.columns:
        if "correo" in col.lower():
            col_correo = col
            break

    resultados = []
    for p in polizas:
        cedula_poliza = str(p.get("cedula") or "").strip()
        info_cliente = clientes_por_cedula.get(cedula_poliza)

        correo = None
        if info_cliente is not None and col_correo is not None:
            correo = info_cliente[col_correo]

        en_maestro = info_cliente is not None

        hasta = p.get("hasta")
        estado = estado_poliza(hasta, fecha_corte)

        if hasta is None:
            dias = None
        else:
            dias = (hasta - fecha_corte).days

        resultado = dict(p)
        resultado["correo"] = correo
        resultado["en_maestro"] = en_maestro
        resultado["dias_hasta_vencer"] = dias
        resultado["estado"] = estado
        resultados.append(resultado)

    # Ordenar de menos a más días (lo urgente primero); None al final
    resultados.sort(
        key=lambda r: (
            r["dias_hasta_vencer"] is None,
            r["dias_hasta_vencer"] if r["dias_hasta_vencer"] is not None else float("inf"),
        )
    )

    return resultados


def contar_por_estado(resultados):
    """Devuelve diccionario con la cantidad de pólizas por estado."""
    conteo = {"Vigente": 0, "Por vencer": 0, "Vencida": 0, "Sin fecha": 0}
    for r in resultados:
        estado = r["estado"]
        if estado in conteo:
            conteo[estado] += 1
        else:
            conteo[estado] = 1
    return conteo


def primas_por_aseguradora(resultados):
    """Suma primas de pólizas no vencidas por aseguradora, de mayor a menor."""
    sumas = defaultdict(float)
    for r in resultados:
        if r["estado"] != "Vencida":
            aseguradora = r.get("aseguradora") or "Sin aseguradora"
            prima = r.get("prima") or 0
            sumas[aseguradora] += prima
    return dict(sorted(sumas.items(), key=lambda x: x[1], reverse=True))


def buscar_inconsistencias(resultados):
    """Devuelve lista de textos con los 3 tipos de problema de AGENTS.md."""
    inconsistencias = []
    clientes = cargar_clientes()

    cedulas_con_poliza = set()
    for r in resultados:
        cedula = str(r.get("cedula") or "").strip()
        cedulas_con_poliza.add(cedula)

        # Tipo 2: póliza cuya cédula no está en el maestro
        if not r.get("en_maestro"):
            inconsistencias.append(
                f"Póliza {r.get('numero')} con cédula {cedula} no está en el maestro de clientes"
            )

        # Tipo 3: póliza sin prima o con fecha ilegible
        if r.get("prima") is None:
            inconsistencias.append(
                f"Póliza {r.get('numero')} sin prima anual"
            )
        if r.get("hasta") is None:
            inconsistencias.append(
                f"Póliza {r.get('numero')} con fecha de vigencia hasta ilegible"
            )

    # Tipo 1: cliente del maestro sin ninguna póliza
    for _, row in clientes.iterrows():
        ced = str(row["Cedula"]).strip()
        if ced not in cedulas_con_poliza:
            inconsistencias.append(
                f"Cliente cédula {ced} sin ninguna póliza"
            )

    return inconsistencias


def buscar_por_numero(numero):
    """Busca una póliza por su número en los resultados calculados."""
    for r in calcular_resultados():
        if r.get("numero") == numero:
            return r
    return None
