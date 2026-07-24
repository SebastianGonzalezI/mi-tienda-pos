# AGENTS.md — Veterinaria POS

## Stack
- Python 3.11, Kivy 2.1.0 (reqs) / 2.2.1 (buildozer), KivyMD 1.1.1, SQLite.
- Target: Android tablet 1280×800 (landscape), Buildozer APK.
- No tests, no linter, no typechecker — manual only.

## Commands
- **Run**: `python main.py`
- **Deps**: `pip install -r requirements.txt`
- **APK**: `pip install buildozer && buildozer android debug`
- **Reset DB**: delete `veterinaria.db` in project root.

## Screens
| ID | File | Purpose |
|---|---|---|
| `login` | `screens/login_screen.py` | Start jornada: username + caja_chica_inicial ($1–100) |
| `main` | `screens/main_screen.py` | Facturación: search products, cart, finalize sale |
| `inventario` | `screens/inventory_screen.py` | CRUD productos + stock; password-gated (`PASSWORD = "PuercoTonto1"`) |
| `cierre` | `screens/cierre_screen.py` | Close jornada, register egresos, view summary |
| `resumen` | `screens/resumen_screen.py` | Monthly summary with pagination, export CSV |

## Entrypoint
`main.py:30` `POSApp(MDApp)` — builds `ScreenManager`, seeds products via `DatabaseManager.inicializar_datos_ejemplo()`, starts auto-close daemon thread.

## Database (`database/`) — Singleton
- `DatabaseManager` uses `__new__` singleton pattern. DB at `veterinaria.db` in project root.
- `_crear_tablas()` runs `CREATE TABLE IF NOT EXISTS` (never DROP, safe to restart), plus additive `ALTER TABLE` for optional columns (`caja_chica_inicial`, `permiso`).
- Tables: `productos`, `jornada`, `ventas`, `detalle_venta`, `caja` (defined but unused), `egresos`.
- `inicializar_datos_ejemplo()` inserts seed **productos only** — never touches ventas/jornada/egresos.

## Gotchas / Behavioral Contracts
- **Transaction ownership**: `actualizar_stock()` + `incrementar_stock()` never commit — caller owns the commit. `registrar_venta()` commits at its end. Standalone `incrementar_stock()` callers (inventory_screen) **must** call `db.conn.commit()` after.
- **`metodo_pago` case**: DB stores capitalized (`"Efectivo"`, `"Tarjeta"`, `"Transferencia"`). All query comparisons use `.lower()`. Keep this convention.
- **`paga_con >= total` only for Efectivo**: Tarjeta/Transferencia skip this validation.
- **`paga_con` cleared after sale**: reset in `limpiar_carrito()` + successful venta. Both field and vuelto label.
- **Product search**: binds via `busqueda_input.bind(text=...)`, not `on_text` kwarg.
- **Price editing** (EDITAR PRECIO): only enabled when selected product has `permiso == 1`.
- **IVI per-product**: each product has own `impuesto` field (default 12%). `actualizar_totales()` calculates `subtotal * impuesto / 100`.

## Reports
- `reportes/cierre_YYYY-MM-DD.txt` — generated on jornada close (`utils/report_txt.py`)
- `reportes/reporte_mensual_MM-YYYY.csv` — exported from Resumen screen (`utils/export_csv.py`)

## Scheduler (`scheduler.py`)
- Daemon thread, checks every 60s if `hour == 22 and minute == 0`.
- Auto-closes active jornada and navigates to login.
- Logs to `scheduler.log`.

## Buildozer (`buildozer.spec`)
- `android.api = 31`, `android.minapi = 24`, `android.archs = arm64-v8a`, `android.enable_androidx = True`.
- APK version: `1.0.0`. Title: `Mi Tienda POS`.
- buildozer requirements use `kivy==2.2.1` (higher than requirements.txt's `2.1.0`).
- Icon: `assets/icon.png`.
