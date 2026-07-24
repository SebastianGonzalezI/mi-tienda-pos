CREATE_TABLES = '''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    cantidad INTEGER DEFAULT 0,
    precio_sin_iva REAL DEFAULT 0,
    impuesto REAL DEFAULT 12,
    precio_con_iva REAL DEFAULT 0,
    descuento REAL DEFAULT 0,
    permiso INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS jornada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_cierre TEXT,
    usuario TEXT NOT NULL,
    estado TEXT DEFAULT 'activa',
    tipo_cierre TEXT,
    caja_chica_inicial REAL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jornada_id INTEGER NOT NULL,
    fecha_hora TEXT NOT NULL,
    cliente TEXT DEFAULT 'Consumidor Final',
    cedula TEXT DEFAULT '',
    total REAL DEFAULT 0,
    subtotal REAL DEFAULT 0,
    iva REAL DEFAULT 0,
    metodo_pago TEXT DEFAULT 'efectivo',
    FOREIGN KEY (jornada_id) REFERENCES jornada(id)
);

CREATE TABLE IF NOT EXISTS detalle_venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER DEFAULT 1,
    precio_unitario REAL DEFAULT 0,
    subtotal REAL DEFAULT 0,
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE TABLE IF NOT EXISTS caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    jornada_id INTEGER NOT NULL,
    ingreso REAL DEFAULT 0,
    egreso REAL DEFAULT 0,
    total REAL DEFAULT 0,
    detalle TEXT DEFAULT '',
    tipo TEXT DEFAULT 'ingreso',
    FOREIGN KEY (jornada_id) REFERENCES jornada(id)
);

CREATE TABLE IF NOT EXISTS egresos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    jornada_id INTEGER NOT NULL,
    monto REAL DEFAULT 0,
    descripcion TEXT DEFAULT '',
    FOREIGN KEY (jornada_id) REFERENCES jornada(id)
);
'''
