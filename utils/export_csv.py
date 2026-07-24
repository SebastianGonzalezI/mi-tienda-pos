import os
import csv


def exportar_mensual_csv(resumen, mes, anio):
    reportes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reportes')
    os.makedirs(reportes_dir, exist_ok=True)

    filename = f"reporte_mensual_{mes:02d}-{anio}.csv"
    filepath = os.path.join(reportes_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        writer.writerow(['RESUMEN MENSUAL', f'{mes:02d}-{anio}'])
        writer.writerow([])
        writer.writerow(['Total Ventas', resumen['cantidad_ventas']])
        writer.writerow(['Total Ingresos', f"${resumen['total_ingresos']:.2f}"])
        writer.writerow(['Total Egresos', f"${resumen['total_egresos']:.2f}"])
        writer.writerow(['Ganancia Neta', f"${resumen['ganancia_neta']:.2f}"])
        writer.writerow(['Efectivo', f"${resumen['total_efectivo']:.2f}"])
        writer.writerow(['Tarjeta', f"${resumen['total_tarjeta']:.2f}"])
        writer.writerow(['Transferencia', f"${resumen['total_transferencia']:.2f}"])
        if resumen.get('usuarios'):
            writer.writerow(['Usuarios', ', '.join(resumen['usuarios'])])

        writer.writerow([])
        writer.writerow(['VENTAS DEL MES'])
        writer.writerow(['#', 'Fecha', 'Cliente', 'Total', 'Metodo Pago'])
        for i, v in enumerate(resumen['detalle_ventas'], 1):
            writer.writerow([i, v['fecha_hora'], v['cliente'], f"${v['total']:.2f}", v['metodo_pago']])

        if resumen['productos_vendidos']:
            writer.writerow([])
            writer.writerow(['PRODUCTOS VENDIDOS'])
            writer.writerow(['Producto', 'Codigo', 'Cantidad', 'Subtotal'])
            for nombre, data in sorted(resumen['productos_vendidos'].items(), key=lambda x: -x[1]['cantidad']):
                writer.writerow([nombre, data['codigo'], data['cantidad'], f"${data['subtotal']:.2f}"])

        if resumen['egresos']:
            writer.writerow([])
            writer.writerow(['EGRESOS'])
            writer.writerow(['Fecha', 'Descripcion', 'Monto'])
            for e in resumen['egresos']:
                writer.writerow([e['fecha'], e['descripcion'], f"${e['monto']:.2f}"])

    return filepath
