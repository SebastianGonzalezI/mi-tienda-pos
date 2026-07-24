import os
from datetime import datetime


def generar_reporte_cierre(jornada, resumen):
    reportes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reportes')
    os.makedirs(reportes_dir, exist_ok=True)

    ahora = datetime.now()
    filename = f"cierre_{ahora.strftime('%Y-%m-%d')}.txt"
    filepath = os.path.join(reportes_dir, filename)

    duracion = _calcular_duracion(jornada['hora_inicio'], jornada.get('hora_cierre'))

    lines = []
    lines.append("=" * 50)
    lines.append("           REPORTE DE CIERRE DE JORNADA")
    lines.append("=" * 50)
    lines.append(f"Fecha:       {jornada['fecha']}")
    lines.append(f"Usuario:     {jornada['usuario']}")
    lines.append(f"Inicio:      {jornada['hora_inicio']}")
    lines.append(f"Cierre:      {jornada.get('hora_cierre', 'N/A')}")
    lines.append(f"Duracion:    {duracion}")
    lines.append(f"Tipo cierre: {(jornada.get('tipo_cierre') or 'manual').upper()}")
    lines.append("-" * 50)
    lines.append(f"Total Ventas:         {resumen['cantidad_ventas']}")
    lines.append(f"Monto Ventas:         ${resumen['total_ventas']:.2f}")
    lines.append("")

    if resumen['productos_vendidos']:
        lines.append("PRODUCTOS VENDIDOS:")
        for nombre, data in sorted(resumen['productos_vendidos'].items(), key=lambda x: -x[1]['cantidad']):
            lines.append(f"  {data['cantidad']}x {nombre} (${data['subtotal']:.2f})")
        lines.append("")

    lines.append("INGRESOS POR METODO DE PAGO:")
    lines.append(f"  Efectivo:      ${resumen['total_efectivo']:.2f}")
    lines.append(f"  Tarjeta:       ${resumen['total_tarjeta']:.2f}")
    lines.append(f"  Transferencia: ${resumen['total_transferencia']:.2f}")
    lines.append(f"  TOTAL INGRESOS: ${resumen['total_ingresos']:.2f}")
    lines.append("")

    if resumen['egresos']:
        lines.append("EGRESOS:")
        for e in resumen['egresos']:
            lines.append(f"  ${e['monto']:.2f} - {e['descripcion']}")
        lines.append(f"  TOTAL EGRESOS: ${resumen['total_egresos']:.2f}")
        lines.append("")

    lines.append("-" * 50)
    lines.append(f"GANANCIA NETA:       ${resumen['ganancia_neta']:.2f}")
    lines.append("")
    lines.append("-" * 50)
    lines.append("CAJA CHICA")
    lines.append("-" * 50)
    lines.append(f"Caja chica inicial:  ${resumen['caja_chica_inicial']:.2f}")
    lines.append(f"Total ingresos:      ${resumen['total_ingresos']:.2f}")
    lines.append(f"Total egresos:       ${resumen['total_egresos']:.2f}")
    lines.append(f"Caja chica final:    ${resumen['caja_chica_final']:.2f}")
    lines.append("=" * 50)
    lines.append(f"Generado: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return filepath


def _calcular_duracion(hora_inicio, hora_cierre=None):
    if not hora_inicio:
        return "N/A"
    try:
        inicio = datetime.strptime(hora_inicio, '%H:%M:%S')
        if hora_cierre:
            fin = datetime.strptime(hora_cierre, '%H:%M:%S')
        else:
            fin = datetime.now().replace(microsecond=0)
        minutos = int((fin - inicio).total_seconds() // 60)
        horas = minutos // 60
        mins = minutos % 60
        return f"{horas}h {mins}m"
    except ValueError:
        return "N/A"
