# Veterinaria POS - Sistema de Punto de Venta

Aplicacion POS para tablet Android desarrollada con Python, KivyMD y SQLite.

## Caracteristicas

- Control de Jornada (inicio/cierre de caja)
- Facturacion con IVA 12%
- Gestion de inventario
- Cierre automatico a las 22:00
- Reportes de cierre de jornada
- Multiples metodos de pago (Efectivo/Tarjeta/Transferencia)

## Requisitos

- Python 3.8+
- Dependencias en requirements.txt

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion

```bash
python main.py
```

## Control de Jornada

### Inicio de Jornada
1. Al abrir la app, se muestra la pantalla de inicio
2. Ingrese el nombre del usuario
3. Presione "INICIAR JORNADA"

### Cierre de Jornada Manual
1. Desde cualquier pantalla, abra el menu (icono 3 puntos)
2. Seleccione "Cerrar Jornada"
3. Confirme el cierre

### Cierre Automatico (22:00)
- La app revisa automaticamente si son las 22:00
- Si hay una jornada activa, aparece un popup de cierre automatico
- Confirme para cerrar la jornada
- El cierre automatico se registra como "automatico" en la base de datos

### Simulacion de Cierre Automatico para Pruebas
Cambie la hora del sistema a 21:59 y espere 1 minuto, o modifique la condicion
en scheduler.py (`if ahora.hour == 22`).

## Estructura del Proyecto

```
Inventario/
├── main.py                 # Punto de entrada
├── scheduler.py            # Programador de cierre automatico
├── screens/                # Pantallas de la aplicacion
│   ├── login_screen.py     # Inicio de jornada
│   ├── main_screen.py      # Facturacion
│   ├── inventory_screen.py # Inventario
│   └── cierre_screen.py    # Cierre de jornada
├── database/               # Base de datos
│   ├── models.py           # Definicion de tablas
│   └── db_manager.py       # Gestor de base de datos
├── utils/                  # Utilidades
│   ├── excel_loader.py     # Carga de Excel
│   ├── validators.py       # Validaciones
│   └── jornada_utils.py    # Funciones de jornada
├── data/                   # Datos de ejemplo
│   └── productos_ejemplo.xlsx
├── assets/                 # Recursos
│   └── icon.png
└── requirements.txt        # Dependencias
```

## Generar APK

```bash
pip install buildozer
buildozer init   # Si no existe buildozer.spec
buildozer android debug
```

## Base de Datos

- Tablas: productos, jornada, ventas, detalle_venta, egresos
- Cada venta se vincula a una jornada
- El cierre de jornada registra hora y tipo (manual/automatico)
