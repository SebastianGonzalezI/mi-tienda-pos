from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
import datetime


class MainScreen(Screen):
    def __init__(self, db, app, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.app = app
        self.carrito = []
        self.total = 0.0
        self.producto_seleccionado = None
        self.caja_chica = 0.0
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical', spacing=dp(4))
        FH = dp(36)
        SP = dp(5)

        # ========== TOOLBAR ==========
        toolbar = MDTopAppBar(
            title="FACTURACION",
            md_bg_color=(0.13, 0.59, 0.95, 1),
            specific_text_color=(1, 1, 1, 1),
            left_action_items=[["menu", lambda x: self.app.mostrar_menu()]],
            right_action_items=[
                ["account", lambda x: self.mostrar_usuario()],
                ["clock", lambda x: self.mostrar_hora()],
                ["wallet", lambda x: self.mostrar_caja_chica()]
            ]
        )
        root.add_widget(toolbar)

        # ========== TOP BAR: VENTA RAPIDA / LIMPIAR / FINALIZAR VENTA ==========
        top_bar = BoxLayout(orientation='horizontal', spacing=SP, size_hint_y=None, height=dp(40), padding=[dp(8), dp(4), dp(8), 0])
        btn_vr = MDRaisedButton(text="VENTA RAPIDA", size_hint_x=0.32, height=dp(36), md_bg_color=(0.9, 0.6, 0, 1), on_release=self.venta_rapida)
        btn_limp = MDRaisedButton(text="LIMPIAR", size_hint_x=0.30, height=dp(36), on_release=lambda x: (self.limpiar_cliente(x), self.limpiar_carrito(x)))
        btn_final = MDRaisedButton(
            text="FINALIZAR VENTA", size_hint_x=0.34,
            md_bg_color=(0.3, 0.8, 0.3, 1), font_size=13, on_release=self.finalizar_venta
        )
        top_bar.add_widget(btn_vr)
        top_bar.add_widget(btn_limp)
        top_bar.add_widget(btn_final)
        root.add_widget(top_bar)

        # ========== MAIN 2-COLUMN CONTENT ==========
        main_top = BoxLayout(orientation='horizontal', spacing=SP, padding=[dp(6), dp(6), dp(6), 0])

        # --- LEFT COLUMN (65%): Nombres, Cédula, Buscar, Productos ---
        left = BoxLayout(orientation='vertical', spacing=SP, size_hint_x=0.65)
        self.nombres_input = MDTextField(hint_text="Nombres", mode="rectangle", size_hint_y=None, height=FH)
        self.cedula_input = MDTextField(hint_text="C\u00e9dula", mode="rectangle", size_hint_y=None, height=FH)
        left.add_widget(self.nombres_input)
        left.add_widget(self.cedula_input)

        self.busqueda_input = MDTextField(
            hint_text="Buscar producto por c\u00f3digo o nombre",
            mode="rectangle", size_hint_y=None, height=dp(38)
        )
        self.busqueda_input.bind(text=self.buscar_productos)
        left.add_widget(self.busqueda_input)

        # Cant / AGREGAR / EDITAR PRECIO (misma linea)
        act_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=SP)
        lbl_cant = Label(text="Cant:", size_hint_x=0.10, font_size=13)
        self.cantidad_input = TextInput(text='1', multiline=False, input_filter='int', size_hint_x=0.22, font_size=15)
        btn_agregar = Button(text='AGREGAR', background_color=(0.3, 0.8, 0.3, 1), size_hint_x=0.34, on_release=self.agregar_al_carrito)
        self.btn_editar = MDFlatButton(text="EDITAR PRECIO", size_hint_x=0.32, on_release=self._editar_precio)
        self.btn_editar.disabled = True
        act_row.add_widget(lbl_cant)
        act_row.add_widget(self.cantidad_input)
        act_row.add_widget(btn_agregar)
        act_row.add_widget(self.btn_editar)
        left.add_widget(act_row)

        scroll_prod = ScrollView()
        self.productos_grid = GridLayout(cols=3, spacing=3, size_hint_y=None, padding=[0, 0, 0, 0])
        self.productos_grid.bind(minimum_height=self.productos_grid.setter('height'))
        scroll_prod.add_widget(self.productos_grid)
        left.add_widget(scroll_prod)

        # --- RIGHT COLUMN (35%): Apellidos, Direcci\u00f3n, Tel\u00e9fono, Carrito, Pago ---
        right = BoxLayout(orientation='vertical', spacing=SP, size_hint_x=0.35)
        self.apellidos_input = MDTextField(hint_text="Apellidos", mode="rectangle", size_hint_y=None, height=FH)
        self.direccion_input = MDTextField(hint_text="Direcci\u00f3n", mode="rectangle", size_hint_y=None, height=FH)
        self.telefono_input = MDTextField(hint_text="Tel\u00e9fono", mode="rectangle", size_hint_y=None, height=FH)
        right.add_widget(self.apellidos_input)
        right.add_widget(self.direccion_input)
        right.add_widget(self.telefono_input)

        right.add_widget(MDLabel(text="CARRITO", font_style="H6", halign="center", size_hint_y=None, height=dp(22)))
        self.carrito_lista = MDList()
        scroll_cart = ScrollView()
        scroll_cart.add_widget(self.carrito_lista)
        right.add_widget(scroll_cart)

        btn_limp_cart = MDRaisedButton(text="LIMPIAR CARRITO", size_hint=(1, None), height=dp(34), on_release=self.limpiar_carrito)
        right.add_widget(btn_limp_cart)

        self.subtotal_label = MDLabel(text="Subtotal: $0.00", font_style="H6", size_hint_y=None, height=dp(18))
        self.iva_label = MDLabel(text="IVA: $0.00", font_style="H6", size_hint_y=None, height=dp(18))
        self.total_label = MDLabel(text="TOTAL: $0.00", font_style="H6", theme_text_color="Primary", size_hint_y=None, height=dp(20))
        right.add_widget(self.subtotal_label)
        right.add_widget(self.iva_label)
        right.add_widget(self.total_label)

        main_top.add_widget(left)
        main_top.add_widget(right)
        root.add_widget(main_top)



        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.cargar_productos(), 0.5)

    def on_enter(self):
        self.cargar_productos()

    def cargar_productos(self, busqueda=''):
        self.productos_grid.clear_widgets()
        productos = self.db.buscar_productos(busqueda) if busqueda else self.db.obtener_productos()
        for prod in productos:
            check = "\u2713 " if prod.get('permiso') else ""
            btn = Button(
                text=f"{check}{prod['codigo']}\n{prod['nombre']}\n${prod['precio_con_iva']:.2f}",
                size_hint_y=None,
                height=dp(64),
                background_color=(0.22, 0.22, 0.22, 1),
                background_normal='',
                halign='left',
                valign='middle',
                padding=(dp(6), dp(2), dp(6), dp(2)),
                on_release=lambda x, p=prod: self.seleccionar_producto(p)
            )
            btn.bind(size=lambda s, ws: setattr(s, 'text_size', (ws[0] - dp(12), ws[1])))
            self.productos_grid.add_widget(btn)

    def buscar_productos(self, instance, value):
        self.cargar_productos(value)

    def seleccionar_producto(self, producto):
        self.producto_seleccionado = producto
        self.busqueda_input.text = f"{producto['codigo']} - {producto['nombre']}  ${producto['precio_con_iva']:.2f}"
        self.btn_editar.disabled = not producto.get('permiso')

    def agregar_al_carrito(self, instance):
        if not self.producto_seleccionado:
            return

        try:
            cantidad = int(self.cantidad_input.text)
        except ValueError:
            self.mostrar_dialogo("Error", "Cantidad invalida. Ingrese un numero entero.")
            return

        if cantidad <= 0:
            self.mostrar_dialogo("Error", "La cantidad debe ser mayor a 0.")
            return

        if cantidad > self.producto_seleccionado['cantidad']:
            self.mostrar_dialogo("Error", f"Stock insuficiente. Disponible: {self.producto_seleccionado['cantidad']}")
            return

        prod_id = self.producto_seleccionado['id']
        for item in self.carrito:
            if item['producto_id'] == prod_id:
                new_cant = item['cantidad'] + cantidad
                if new_cant > self.producto_seleccionado['cantidad']:
                    self.mostrar_dialogo("Error", f"Stock insuficiente. Disponible: {self.producto_seleccionado['cantidad']}")
                    return
                item['cantidad'] = new_cant
                item['subtotal'] = new_cant * item['precio_unitario']
                self.actualizar_carrito()
                self.actualizar_totales()
                self.cantidad_input.text = '1'
                self.busqueda_input.text = ''
                self.producto_seleccionado = None
                self.btn_editar.disabled = True
                return

        prod = {
            'producto_id': self.producto_seleccionado['id'],
            'codigo': self.producto_seleccionado['codigo'],
            'nombre': self.producto_seleccionado['nombre'],
            'precio_unitario': self.producto_seleccionado['precio_sin_iva'],
            'impuesto': self.producto_seleccionado['impuesto'],
            'cantidad': cantidad,
            'subtotal': cantidad * self.producto_seleccionado['precio_sin_iva']
        }

        self.carrito.append(prod)
        self.actualizar_carrito()
        self.actualizar_totales()
        self.cantidad_input.text = '1'
        self.busqueda_input.text = ''
        self.producto_seleccionado = None
        self.btn_editar.disabled = True

    def actualizar_carrito(self):
        self.carrito_lista.clear_widgets()
        for i, prod in enumerate(self.carrito):
            item = OneLineListItem(
                text=f"{prod['nombre']} x{prod['cantidad']} = ${prod['subtotal']:.2f}",
                on_release=lambda x, idx=i: self.eliminar_del_carrito(idx)
            )
            self.carrito_lista.add_widget(item)

    def eliminar_del_carrito(self, idx):
        if 0 <= idx < len(self.carrito):
            del self.carrito[idx]
            self.actualizar_carrito()
            self.actualizar_totales()

    def limpiar_carrito(self, instance):
        self.carrito = []
        self.actualizar_carrito()
        self.actualizar_totales()
        self.producto_seleccionado = None
        self.btn_editar.disabled = True
        self.busqueda_input.text = ''
        self.cantidad_input.text = '1'

    def actualizar_totales(self):
        subtotal = sum(prod['subtotal'] for prod in self.carrito)
        iva = sum(prod['subtotal'] * prod['impuesto'] / 100 for prod in self.carrito)
        self.total = subtotal + iva

        self.subtotal_label.text = f"Subtotal: ${subtotal:.2f}"
        self.iva_label.text = f"IVA: ${iva:.2f}"
        self.total_label.text = f"TOTAL: ${self.total:.2f}"

    def finalizar_venta(self, instance):
        if not self.carrito:
            self.mostrar_dialogo("Error", "No hay productos en el carrito")
            return
        jornada = self.db.obtener_jornada_activa()
        if not jornada:
            self.mostrar_dialogo("Error", "No hay jornada activa. Inicie jornada primero.")
            return

        cliente = f"{self.nombres_input.text} {self.apellidos_input.text}".strip().upper()
        if not cliente:
            cliente = "CLIENTE SIN NOMBRE"
        cedula = self.cedula_input.text.strip()
        subtotal = sum(item['subtotal'] for item in self.carrito)
        iva_total = sum(item['subtotal'] * item['impuesto'] / 100 for item in self.carrito)

        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        lbl_pago = MDLabel(text="PAGO EN EFECTIVO", font_style="Subtitle1", bold=True, size_hint_y=None, height=dp(22))
        method_row = BoxLayout(orientation='horizontal', spacing=dp(4), size_hint_y=None, height=dp(38))
        content.add_widget(method_row)
        content.add_widget(lbl_pago)

        metodo_pago = ["Efectivo"]
        pago_btns = {}

        banco_panel = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None, height=0, opacity=0, disabled=True)
        txt_banco = MDTextField(hint_text="Nombre del Banco", mode="rectangle", size_hint_y=None, height=dp(34))
        txt_trans = MDTextField(hint_text="Numero de Transaccion", mode="rectangle", size_hint_y=None, height=dp(34))
        banco_panel.add_widget(txt_banco)
        banco_panel.add_widget(txt_trans)
        content.add_widget(banco_panel)

        paga_panel = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None, height=dp(56), opacity=1)
        txt_paga = MDTextField(hint_text=f"Paga con (Total: ${self.total:.2f})", mode="rectangle", size_hint_y=None, height=dp(34))
        lbl_vuelto = MDLabel(text="", font_style="H6", theme_text_color="Custom", text_color=(0, 1, 0, 1), bold=True, size_hint_y=None, height=dp(18))

        def calc_vuelto(*_):
            if txt_paga.text.strip():
                try:
                    v = float(txt_paga.text) - self.total
                    lbl_vuelto.text = f"Vuelto: ${v:.2f}" if v >= 0 else "Monto insuficiente"
                except ValueError:
                    lbl_vuelto.text = ""
            else:
                lbl_vuelto.text = ""

        txt_paga.bind(text=calc_vuelto)
        paga_panel.add_widget(txt_paga)
        paga_panel.add_widget(lbl_vuelto)
        content.add_widget(paga_panel)

        def _on_metodo_click(metodo):
            metodo_pago[0] = metodo
            for k, b in pago_btns.items():
                b.background_color = (0.2, 0.6, 1, 1) if k == metodo else (0.3, 0.3, 0.3, 1)
            if metodo == "Efectivo":
                lbl_pago.text = "PAGO EN EFECTIVO"
                paga_panel.height = dp(56)
                paga_panel.opacity = 1
                paga_panel.disabled = False
                banco_panel.height = 0
                banco_panel.opacity = 0
                banco_panel.disabled = True
            else:
                lbl_pago.text = "DATOS BANCARIOS"
                banco_panel.height = dp(72)
                banco_panel.opacity = 1
                banco_panel.disabled = False
                paga_panel.height = 0
                paga_panel.opacity = 0
                paga_panel.disabled = True

        for m in ['Efectivo', 'Tarjeta', 'Transferencia']:
            color = (0.2, 0.6, 1, 1) if m == 'Efectivo' else (0.3, 0.3, 0.3, 1)
            btn = Button(text=m, size_hint_x=0.3, height=dp(36), font_size=14,
                background_color=color, background_normal='')
            btn.bind(on_release=lambda instance, metodo=m: _on_metodo_click(metodo))
            method_row.add_widget(btn)
            pago_btns[m] = btn

        dialog = MDDialog(
            title=f"PAGO - Total: ${self.total:.2f}",
            type="custom",
            content_cls=content,
            size_hint=(0.5, None),
            height=dp(340),
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="CONFIRMAR", md_bg_color=(0.3, 0.8, 0.3, 1),
                    on_release=lambda x: self._procesar_pago(dialog, cliente, cedula, subtotal, iva_total,
                        metodo_pago[0], txt_paga, txt_banco, txt_trans)),
            ]
        )
        dialog.open()

    def _procesar_pago(self, dialog, cliente, cedula, subtotal, iva_total,
                        metodo_pago, txt_paga, txt_banco, txt_trans):
        dialog.dismiss()

        if metodo_pago == "Efectivo":
            try:
                paga_con = float(txt_paga.text)
            except ValueError:
                self.mostrar_dialogo("Error", "Ingrese el monto con que paga")
                return
            if paga_con < self.total:
                self.mostrar_dialogo("Error", f"Monto insuficiente (${paga_con:.2f} < ${self.total:.2f})")
                return
        else:
            if not txt_banco.text.strip() or not txt_trans.text.strip():
                self.mostrar_dialogo("Error", "Ingrese banco y numero de transaccion")
                return

        jornada = self.db.obtener_jornada_activa()
        if not jornada:
            self.mostrar_dialogo("Error", "No hay jornada activa")
            return

        venta_id = self.db.registrar_venta(
            jornada['id'], cliente, cedula, self.total, subtotal, iva_total, metodo_pago, self.carrito
        )
        if venta_id:
            self.mostrar_dialogo("\u2705 Venta Exitosa",
                f"Venta #{venta_id}\nCliente: {cliente}\nTotal: ${self.total:.2f}\nM\u00e9todo: {metodo_pago}")
            self.limpiar_carrito(None)
            self.limpiar_cliente(None)
        else:
            self.mostrar_dialogo("\u274c Error", "No se pudo registrar la venta")

    def venta_rapida(self, instance):
        self.nombres_input.text = 'CONSUMIDOR FINAL'
        self.apellidos_input.text = ''
        self.direccion_input.text = 'SAN PEDRO'
        self.telefono_input.text = 'NA'
        self.cedula_input.text = '9999999999'

    def limpiar_cliente(self, instance):
        self.nombres_input.text = ''
        self.apellidos_input.text = ''
        self.cedula_input.text = ''
        self.direccion_input.text = ''
        self.telefono_input.text = ''

    def _editar_precio(self, *args):
        if not self.producto_seleccionado:
            return
        prod = self.producto_seleccionado
        content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        txt_nombre = MDTextField(hint_text="Nombre del producto", text=prod['nombre'],
            mode="rectangle", size_hint_y=None, height=dp(45))
        txt_precio = MDTextField(hint_text=f"Precio sin IVA (actual: ${prod['precio_sin_iva']:.2f})",
            text=str(prod['precio_sin_iva']), mode="rectangle", size_hint_y=None, height=dp(45), input_filter='float')
        txt_iva = MDTextField(hint_text=f"IVA % (actual: {prod['impuesto']}%)",
            text=str(prod['impuesto']), mode="rectangle", size_hint_y=None, height=dp(45), input_filter='float')
        content.add_widget(txt_nombre)
        content.add_widget(txt_precio)
        content.add_widget(txt_iva)

        dialog = MDDialog(
            title=f"Editar: {prod['codigo']}",
            type="custom",
            content_cls=content,
            size_hint=(0.5, None),
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_release=lambda x: self._guardar_edicion(dialog, txt_nombre, txt_precio, txt_iva)),
            ]
        )
        dialog.open()

    def _guardar_edicion(self, dialog, txt_nombre, txt_precio, txt_iva):
        dialog.dismiss()
        if not self.producto_seleccionado:
            return
        prod_id = self.producto_seleccionado['id']
        nombre = txt_nombre.text.strip().upper()
        try:
            precio = float(txt_precio.text.strip())
        except ValueError:
            self.mostrar_dialogo("Error", "Precio invalido")
            return
        if precio <= 0:
            self.mostrar_dialogo("Error", "El precio debe ser mayor a 0")
            return
        try:
            impuesto = float(txt_iva.text.strip()) if txt_iva.text.strip() else 0
        except ValueError:
            self.mostrar_dialogo("Error", "IVA invalido")
            return
        if impuesto < 0 or impuesto > 100:
            self.mostrar_dialogo("Error", "El IVA debe estar entre 0 y 100")
            return
        precio_con_iva = precio * (1 + impuesto / 100)
        self.db.conn.execute(
            'UPDATE productos SET nombre = ?, precio_sin_iva = ?, precio_con_iva = ?, impuesto = ? WHERE id = ?',
            (nombre, precio, precio_con_iva, impuesto, prod_id)
        )
        self.db.conn.commit()

        item = {
            'producto_id': prod_id,
            'codigo': self.producto_seleccionado['codigo'],
            'nombre': nombre,
            'precio_unitario': precio,
            'impuesto': impuesto,
            'cantidad': 1,
            'subtotal': precio
        }
        self.carrito.append(item)
        self.actualizar_carrito()
        self.actualizar_totales()

        self.producto_seleccionado = None
        self.btn_editar.disabled = True
        self.cantidad_input.text = '1'
        self.busqueda_input.text = ''

    def mostrar_dialogo(self, titulo, mensaje):
        dialog = MDDialog(
            title=titulo,
            text=mensaje,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def mostrar_usuario(self):
        jornada = self.db.obtener_jornada_activa()
        if jornada:
            self.mostrar_dialogo("Usuario", f"Usuario: {jornada['usuario']}\nInicio: {jornada['hora_inicio']}")
        else:
            self.mostrar_dialogo("Usuario", "No hay jornada activa")

    def mostrar_caja_chica(self):
        jornada = self.db.obtener_jornada_activa()
        if jornada:
            caja = jornada.get('caja_chica_inicial', 0)
            self.mostrar_dialogo("Caja Chica", f"Caja Chica Inicial: ${caja:.2f}")
        else:
            self.mostrar_dialogo("Caja Chica", "No hay jornada activa")

    def mostrar_hora(self):
        ahora = datetime.datetime.now().strftime("%H:%M:%S")
        self.mostrar_dialogo("Hora", f"Hora actual: {ahora}")
