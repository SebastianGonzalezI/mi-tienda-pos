from datetime import datetime


def formatear_tiempo(minutos):
    if minutos < 0:
        minutos = 0
    horas = minutos // 60
    mins = minutos % 60
    if horas > 0:
        return f"{horas}h {mins}m"
    return f"{mins}m"


def calcular_duracion_jornada(hora_inicio, hora_cierre=None):
    if not hora_inicio:
        return "0h 0m"
    try:
        inicio = datetime.strptime(hora_inicio, '%H:%M:%S')
        if hora_cierre:
            fin = datetime.strptime(hora_cierre, '%H:%M:%S')
        else:
            fin = datetime.now().replace(microsecond=0)
        diferencia = fin - inicio
        minutos = int(diferencia.total_seconds() // 60)
        return formatear_tiempo(minutos)
    except ValueError:
        try:
            inicio = datetime.strptime(hora_inicio, '%H:%M')
            if hora_cierre:
                fin = datetime.strptime(hora_cierre, '%H:%M')
            else:
                fin = datetime.now().replace(microsecond=0)
            diferencia = fin - inicio
            minutos = int(diferencia.total_seconds() // 60)
            return formatear_tiempo(minutos)
        except ValueError:
            return "0h 0m"


def generar_resumen_texto(resumen, jornada):
    texto = ""
    texto += f"USUARIO: {jornada['usuario']}\n"
    texto += f"INICIO: {jornada['hora_inicio']}\n"
    duracion = calcular_duracion_jornada(jornada['hora_inicio'], jornada.get('hora_cierre'))
    texto += f"DURACIÓN: {duracion}\n"
    texto += f"FECHA: {jornada['fecha']}\n"
    texto += "-" * 30 + "\n"
    texto += f"Total Ventas: {resumen['cantidad_ventas']}\n"
    texto += f"Monto Ventas: ${resumen['total_ventas']:.2f}\n"

    if resumen['productos_vendidos']:
        texto += "\nProductos Vendidos:\n"
        for nombre, data in resumen['productos_vendidos'].items():
            texto += f"  - {nombre}: {data['cantidad']} und (${data['subtotal']:.2f})\n"

    texto += "\nINGRESOS:\n"
    texto += f"  Efectivo: ${resumen['total_efectivo']:.2f}\n"
    texto += f"  Tarjeta: ${resumen['total_tarjeta']:.2f}\n"
    texto += f"  Transferencia: ${resumen['total_transferencia']:.2f}\n"
    texto += f"  TOTAL: ${resumen['total_ingresos']:.2f}\n"

    if resumen['egresos']:
        texto += f"\nEGRESOS:\n"
        for e in resumen['egresos']:
            texto += f"  - {e['descripcion']}: ${e['monto']:.2f}\n"
    texto += f"  TOTAL EGRESOS: ${resumen['total_egresos']:.2f}\n"

    texto += "-" * 30 + "\n"
    texto += f"GANANCIA NETA: ${resumen['ganancia_neta']:.2f}\n"
    texto += "\n"
    texto += "CAJA CHICA\n"
    texto += f"  Inicial:   ${resumen['caja_chica_inicial']:.2f}\n"
    texto += f"  Ingresos:  ${resumen['total_ingresos']:.2f}\n"
    texto += f"  Egresos:   ${resumen['total_egresos']:.2f}\n"
    texto += f"  Final:     ${resumen['caja_chica_final']:.2f}\n"

    return texto


def validar_hora_cierre():
    ahora = datetime.now()
    return ahora.hour >= 22
