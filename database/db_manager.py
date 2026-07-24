import sqlite3
import os
import json
from datetime import datetime

from database.models import CREATE_TABLES


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'veterinaria.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._crear_tablas()

    def _crear_tablas(self):
        self.conn.executescript(CREATE_TABLES)
        for col, sql in [
            ('caja_chica_inicial', 'ALTER TABLE jornada ADD COLUMN caja_chica_inicial REAL DEFAULT 0.00'),
            ('permiso', 'ALTER TABLE productos ADD COLUMN permiso INTEGER DEFAULT 0'),
        ]:
            try:
                self.conn.execute(sql)
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    # ---- Productos ----
    def obtener_productos(self):
        cursor = self.conn.execute('SELECT * FROM productos ORDER BY nombre')
        return [dict(row) for row in cursor.fetchall()]

    def obtener_producto_por_codigo(self, codigo):
        cursor = self.conn.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def obtener_producto_por_id(self, producto_id):
        cursor = self.conn.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def buscar_productos(self, query):
        cursor = self.conn.execute(
            'SELECT * FROM productos WHERE nombre LIKE ? OR codigo LIKE ? ORDER BY nombre',
            (f'%{query}%', f'%{query}%')
        )
        return [dict(row) for row in cursor.fetchall()]

    def actualizar_stock(self, producto_id, cantidad):
        self.conn.execute(
            'UPDATE productos SET cantidad = cantidad - ? WHERE id = ? AND cantidad >= ?',
            (cantidad, producto_id, cantidad)
        )
        return self.conn.total_changes > 0

    def incrementar_stock(self, producto_id, cantidad):
        self.conn.execute(
            'UPDATE productos SET cantidad = cantidad + ? WHERE id = ?',
            (cantidad, producto_id)
        )
        return self.conn.total_changes > 0

    def get_db_path(self):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'veterinaria.db')

    # ---- Jornada ----
    def iniciar_jornada(self, usuario, caja_chica=0.0):
        ahora = datetime.now()
        fecha = ahora.strftime('%Y-%m-%d')
        hora = ahora.strftime('%H:%M:%S')
        cursor = self.conn.execute(
            'INSERT INTO jornada (fecha, hora_inicio, usuario, estado, caja_chica_inicial) VALUES (?, ?, ?, ?, ?)',
            (fecha, hora, usuario, 'activa', caja_chica)
        )
        self.conn.commit()
        return cursor.lastrowid

    def cerrar_jornada(self, jornada_id, tipo_cierre='manual'):
        ahora = datetime.now()
        hora = ahora.strftime('%H:%M:%S')
        self.conn.execute(
            'UPDATE jornada SET hora_cierre = ?, estado = ?, tipo_cierre = ? WHERE id = ?',
            (hora, 'cerrada', tipo_cierre, jornada_id)
        )
        self.conn.commit()
        return True

    def obtener_jornada_activa(self):
        cursor = self.conn.execute(
            'SELECT * FROM jornada WHERE estado = ? ORDER BY id DESC LIMIT 1',
            ('activa',)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def obtener_jornada_por_id(self, jornada_id):
        cursor = self.conn.execute('SELECT * FROM jornada WHERE id = ?', (jornada_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def obtener_resumen_jornada(self, jornada_id):
        jornada = self.obtener_jornada_por_id(jornada_id)
        caja_inicial = jornada['caja_chica_inicial'] if jornada else 0.0
        resumen = {
            'total_ventas': 0,
            'cantidad_ventas': 0,
            'total_efectivo': 0,
            'total_tarjeta': 0,
            'total_transferencia': 0,
            'total_ingresos': 0,
            'total_egresos': 0,
            'ganancia_neta': 0,
            'caja_chica_inicial': caja_inicial,
            'caja_chica_final': 0.0,
            'detalle_ventas': [],
            'productos_vendidos': {},
            'egresos': []
        }

        ventas = self.conn.execute(
            'SELECT * FROM ventas WHERE jornada_id = ?', (jornada_id,)
        ).fetchall()

        resumen['cantidad_ventas'] = len(ventas)
        for venta in ventas:
            v = dict(venta)
            resumen['total_ventas'] += v['total']
            mp = v['metodo_pago'].lower()
            if mp == 'efectivo':
                resumen['total_efectivo'] += v['total']
            elif mp == 'tarjeta':
                resumen['total_tarjeta'] += v['total']
            elif mp == 'transferencia':
                resumen['total_transferencia'] += v['total']

            detalles = self.conn.execute(
                '''SELECT dv.*, p.nombre, p.codigo
                   FROM detalle_venta dv
                   JOIN productos p ON dv.producto_id = p.id
                   WHERE dv.venta_id = ?''',
                (v['id'],)
            ).fetchall()

            venta_detalle = {
                'id': v['id'],
                'fecha_hora': v['fecha_hora'],
                'cliente': v['cliente'],
                'total': v['total'],
                'metodo_pago': v['metodo_pago'],
                'items': []
            }
            for det in detalles:
                d = dict(det)
                venta_detalle['items'].append(d)
                clave = d['nombre']
                if clave in resumen['productos_vendidos']:
                    resumen['productos_vendidos'][clave]['cantidad'] += d['cantidad']
                    resumen['productos_vendidos'][clave]['subtotal'] += d['subtotal']
                else:
                    resumen['productos_vendidos'][clave] = {
                        'codigo': d['codigo'],
                        'cantidad': d['cantidad'],
                        'subtotal': d['subtotal']
                    }
            resumen['detalle_ventas'].append(venta_detalle)

        resumen['total_ingresos'] = resumen['total_ventas']

        egresos = self.conn.execute(
            'SELECT * FROM egresos WHERE jornada_id = ?', (jornada_id,)
        ).fetchall()
        for egreso in egresos:
            e = dict(egreso)
            resumen['total_egresos'] += e['monto']
            resumen['egresos'].append(e)

        resumen['ganancia_neta'] = resumen['total_ingresos'] - resumen['total_egresos']
        resumen['caja_chica_final'] = resumen['caja_chica_inicial'] + resumen['total_ingresos'] - resumen['total_egresos']

        return resumen

    def verificar_cierre_automatico(self):
        ahora = datetime.now()
        return ahora.hour == 22 and ahora.minute == 0

    def obtener_ultimo_cierre(self):
        cursor = self.conn.execute(
            'SELECT * FROM jornada WHERE estado = ? ORDER BY id DESC LIMIT 1',
            ('cerrada',)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    # ---- Ventas ----
    def registrar_venta(self, jornada_id, cliente, cedula, total, subtotal, iva, metodo_pago, items):
        ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.conn.execute(
            '''INSERT INTO ventas (jornada_id, fecha_hora, cliente, cedula, total, subtotal, iva, metodo_pago)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (jornada_id, ahora, cliente, cedula, total, subtotal, iva, metodo_pago)
        )
        venta_id = cursor.lastrowid

        for item in items:
            self.conn.execute(
                'INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)',
                (venta_id, item['producto_id'], item['cantidad'], item['precio_unitario'], item['subtotal'])
            )
            self.actualizar_stock(item['producto_id'], item['cantidad'])

        self.conn.commit()
        return venta_id

    # ---- Egresos ----
    def registrar_egreso(self, jornada_id, monto, descripcion):
        ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.conn.execute(
            'INSERT INTO egresos (fecha, jornada_id, monto, descripcion) VALUES (?, ?, ?, ?)',
            (ahora, jornada_id, monto, descripcion)
        )
        self.conn.commit()
        return True

    # ---- Reportes Mensuales ----
    def obtener_resumen_mensual(self, mes, anio):
        filtro = (f"{anio:04d}-{mes:02d}%",)
        resumen = {
            'total_ventas': 0, 'cantidad_ventas': 0,
            'total_efectivo': 0, 'total_tarjeta': 0, 'total_transferencia': 0,
            'total_ingresos': 0, 'total_egresos': 0, 'ganancia_neta': 0,
            'detalle_ventas': [], 'productos_vendidos': {}, 'egresos': [],
            'usuarios': []
        }

        rows = self.conn.execute(
            'SELECT DISTINCT usuario FROM jornada WHERE fecha LIKE ? ORDER BY usuario', filtro
        ).fetchall()
        resumen['usuarios'] = [r['usuario'] for r in rows]

        ventas = self.conn.execute(
            'SELECT v.*, j.usuario FROM ventas v JOIN jornada j ON v.jornada_id = j.id WHERE v.fecha_hora LIKE ?', filtro
        ).fetchall()
        resumen['cantidad_ventas'] = len(ventas)
        for venta in ventas:
            v = dict(venta)
            resumen['total_ventas'] += v['total']
            mp = v['metodo_pago'].lower()
            if mp == 'efectivo':
                resumen['total_efectivo'] += v['total']
            elif mp == 'tarjeta':
                resumen['total_tarjeta'] += v['total']
            elif mp == 'transferencia':
                resumen['total_transferencia'] += v['total']

            detalles = self.conn.execute(
                '''SELECT dv.*, p.nombre, p.codigo
                   FROM detalle_venta dv JOIN productos p ON dv.producto_id = p.id
                   WHERE dv.venta_id = ?''', (v['id'],)
            ).fetchall()
            for d in detalles:
                det = dict(d)
                clave = det['nombre']
                if clave in resumen['productos_vendidos']:
                    resumen['productos_vendidos'][clave]['cantidad'] += det['cantidad']
                    resumen['productos_vendidos'][clave]['subtotal'] += det['subtotal']
                else:
                    resumen['productos_vendidos'][clave] = {
                        'codigo': det['codigo'], 'cantidad': det['cantidad'], 'subtotal': det['subtotal']
                    }
            resumen['detalle_ventas'].append({
                'id': v['id'], 'fecha_hora': v['fecha_hora'],
                'cliente': v['cliente'], 'total': v['total'],
                'metodo_pago': v['metodo_pago'],
                'usuario': v['usuario']
            })

        resumen['total_ingresos'] = resumen['total_ventas']
        egresos = self.conn.execute(
            'SELECT * FROM egresos WHERE fecha LIKE ?', filtro
        ).fetchall()
        for egreso in egresos:
            e = dict(egreso)
            resumen['total_egresos'] += e['monto']
            resumen['egresos'].append(e)
        resumen['ganancia_neta'] = resumen['total_ingresos'] - resumen['total_egresos']
        return resumen

    def obtener_top_productos(self, mes, anio, limite=5):
        filtro = (f"{anio:04d}-{mes:02d}%",)
        rows = self.conn.execute(
            '''SELECT p.nombre, p.codigo, SUM(dv.cantidad) as total_qty, SUM(dv.subtotal) as total_sub
               FROM detalle_venta dv
               JOIN ventas v ON dv.venta_id = v.id
               JOIN productos p ON dv.producto_id = p.id
               WHERE v.fecha_hora LIKE ?
               GROUP BY dv.producto_id
               ORDER BY total_qty DESC LIMIT ?''', (filtro[0], limite)
        ).fetchall()
        return [dict(r) for r in rows]

    # ---- Productos CRUD ----
    def agregar_producto(self, codigo, nombre, cantidad, precio_sin_iva, impuesto, precio_con_iva, descuento, permiso=0):
        try:
            cursor = self.conn.execute(
                '''INSERT INTO productos (codigo, nombre, cantidad, precio_sin_iva, impuesto, precio_con_iva, descuento, permiso)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (codigo, nombre, cantidad, precio_sin_iva, impuesto, precio_con_iva, descuento, permiso)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    # ---- Inicializar datos de ejemplo ----
    def inicializar_datos_ejemplo(self):
        productos = [
            ('VET001', 'Vacuna Triple Felina', 50, 25.00, 12, 28.00, 0, 1),
            ('VET002', 'Desparasitante Oral Perros', 80, 15.00, 12, 16.80, 0, 1),
            ('VET003', 'Shampoo Antipulgas', 40, 18.50, 12, 20.72, 0, 1),
            ('VET004', 'Collar Antipulgas', 30, 22.00, 12, 24.64, 0, 1),
            ('VET005', 'Comida Premium Perro 3kg', 25, 35.00, 12, 39.20, 0, 1),
            ('VET006', 'Comida Gato Adulto 1.5kg', 20, 28.50, 12, 31.92, 0, 1),
            ('VET007', 'Jeringas 5ml (x100)', 60, 12.00, 12, 13.44, 0, 0),
            ('VET008', 'Vendas Elásticas (x10)', 45, 8.50, 12, 9.52, 0, 0),
            ('VET009', 'Antibiótico Amoxicilina 500mg', 35, 42.00, 12, 47.04, 0, 1),
            ('VET010', 'Guantes Quirúrgicos (x50)', 100, 6.00, 12, 6.72, 0, 0),
        ]
        for p in productos:
            try:
                self.conn.execute(
                    'INSERT INTO productos (codigo, nombre, cantidad, precio_sin_iva, impuesto, precio_con_iva, descuento, permiso) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    p
                )
            except sqlite3.IntegrityError:
                pass
        self.conn.commit()
