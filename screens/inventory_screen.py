from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox

from database.db_manager import DatabaseManager

PASSWORD = "PuercoTonto1"


class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.dialog = None
        self._accion_password = None
        self._build_ui()

    def _build_ui(self):
        toolbar = MDTopAppBar(
            title='Inventario',
            md_bg_color=(0.13, 0.13, 0.13, 1),
            specific_text_color='#FFFFFF',
            left_action_items=[['arrow-left', lambda x: self._volver()]]
        )

        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(15),
            padding=[dp(10), dp(5), dp(10), dp(5)]
        )

        btn_nuevo = MDRaisedButton(
            text="+ NUEVO PRODUCTO",
            size_hint_x=0.5,
            height=dp(50),
            md_bg_color=(0, 0.6, 0.3, 1),
            font_size=15,
            on_release=lambda x: self._pedir_password(self._mostrar_formulario_producto)
        )
        btn_stock = MDRaisedButton(
            text="+ AGREGAR STOCK",
            size_hint_x=0.5,
            height=dp(50),
            md_bg_color=(0, 0.4, 0.7, 1),
            font_size=15,
            on_release=lambda x: self._pedir_password(self._mostrar_dialogo_stock)
        )

        btn_row.add_widget(btn_nuevo)
        btn_row.add_widget(btn_stock)

        content = ScrollView()
        self.productos_layout = MDGridLayout(
            cols=1, spacing=dp(5),
            padding=[dp(10), dp(10), dp(10), dp(10)],
            size_hint_y=None, adaptive_height=True
        )
        content.add_widget(self.productos_layout)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(toolbar)
        layout.add_widget(btn_row)
        layout.add_widget(content)
        self.add_widget(layout)

    def on_enter(self):
        self._cargar_productos()

    def _cargar_productos(self):
        self.productos_layout.clear_widgets()
        productos = self.db.obtener_productos()

        header = MDGridLayout(cols=5, spacing=dp(5), size_hint_y=None, height=dp(40))
        for h in ['Codigo', 'Nombre', 'Stock', 'P.Unit', 'P.IVA']:
            lbl = MDLabel(text=h, bold=True, halign='center')
            header.add_widget(lbl)
        self.productos_layout.add_widget(header)

        for p in productos:
            card = MDCard(
                orientation='horizontal',
                size_hint_y=None, height=dp(50),
                padding=[dp(5), dp(5), dp(5), dp(5)],
                spacing=dp(5)
            )
            for valor in [p['codigo'], p['nombre'], str(p['cantidad']),
                          f"${p['precio_sin_iva']:.2f}", f"${p['precio_con_iva']:.2f}"]:
                lbl = MDLabel(text=valor, halign='center')
                card.add_widget(lbl)
            self.productos_layout.add_widget(card)

    # ---- Password ----
    def _pedir_password(self, accion):
        self._accion_password = accion
        if self.dialog:
            self.dialog.dismiss()
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(80))
        self.pw_input = MDTextField(
            hint_text="Contrasena",
            password=True,
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(self.pw_input)
        self.dialog = MDDialog(
            title="Autorizacion Requerida",
            text="Ingrese la contrasena para continuar",
            type="custom",
            content_cls=content,
            size_hint=(0.5, None),
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: self._cerrar_dialogo()),
                MDRaisedButton(text="CONFIRMAR", on_release=lambda x: self._verificar_password()),
            ]
        )
        self.dialog.open()

    def _verificar_password(self):
        if self.pw_input.text == PASSWORD:
            self._cerrar_dialogo()
            if self._accion_password:
                self._accion_password()
        else:
            self.pw_input.text = ""
            self.pw_input.hint_text = "Contrasena incorrecta. Intente nuevamente."

    # ---- Nuevo Producto ----
    def _mostrar_formulario_producto(self):
        if self.dialog:
            self.dialog.dismiss()
        content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        self.f_codigo = MDTextField(hint_text="Codigo *", mode="rectangle", size_hint_y=None, height=dp(45))
        self.f_nombre = MDTextField(hint_text="Nombre *", mode="rectangle", size_hint_y=None, height=dp(45))
        self.f_cantidad = MDTextField(hint_text="Cantidad *", mode="rectangle", size_hint_y=None, height=dp(45), input_filter='int')
        self.f_precio = MDTextField(hint_text="Precio sin IVA *", mode="rectangle", size_hint_y=None, height=dp(45), input_filter='float')
        self.f_impuesto = MDTextField(hint_text="Impuesto %", mode="rectangle", size_hint_y=None, height=dp(45), input_filter='float', text="12")
        self.f_descuento = MDTextField(hint_text="Descuento %", mode="rectangle", size_hint_y=None, height=dp(45), input_filter='float', text="0")

        permiso_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        self.f_permiso_chk = MDCheckbox(size_hint=(None, None), size=(dp(30), dp(30)))
        permiso_row.add_widget(MDLabel(text="Permiso editar precio", size_hint_x=0.8))
        permiso_row.add_widget(self.f_permiso_chk)

        for w in [self.f_codigo, self.f_nombre, self.f_cantidad, self.f_precio, self.f_impuesto, self.f_descuento, permiso_row]:
            content.add_widget(w)

        self.dialog = MDDialog(
            title="Nuevo Producto",
            type="custom",
            content_cls=content,
            size_hint=(0.6, None),
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: self._cerrar_dialogo()),
                MDRaisedButton(text="GUARDAR", on_release=lambda x: self._guardar_producto()),
            ]
        )
        self.dialog.open()

    def _guardar_producto(self):
        codigo = self.f_codigo.text.strip().upper()
        nombre = self.f_nombre.text.strip().upper()
        cantidad_str = self.f_cantidad.text.strip()
        precio_str = self.f_precio.text.strip()
        impuesto_str = self.f_impuesto.text.strip()
        descuento_str = self.f_descuento.text.strip()

        if not codigo or not nombre or not cantidad_str or not precio_str:
            self._mostrar_error("Complete todos los campos obligatorios.")
            return

        try:
            cantidad = int(cantidad_str)
        except ValueError:
            self._mostrar_error("La cantidad debe ser un numero entero.")
            return
        if cantidad < 0:
            self._mostrar_error("La cantidad debe ser mayor o igual a 0.")
            return

        try:
            precio_sin_iva = float(precio_str)
        except ValueError:
            self._mostrar_error("El precio debe ser un numero valido.")
            return
        if precio_sin_iva <= 0:
            self._mostrar_error("El precio debe ser mayor a 0.")
            return

        try:
            impuesto = float(impuesto_str) if impuesto_str else 12
        except ValueError:
            self._mostrar_error("Impuesto invalido.")
            return
        if impuesto < 0 or impuesto > 100:
            self._mostrar_error("El impuesto debe estar entre 0 y 100.")
            return

        try:
            descuento = float(descuento_str) if descuento_str else 0
        except ValueError:
            self._mostrar_error("Descuento invalido.")
            return
        if descuento < 0 or descuento > 100:
            self._mostrar_error("El descuento debe estar entre 0 y 100.")
            return

        precio_con_iva = precio_sin_iva * (1 + impuesto / 100)

        permiso = 1 if self.f_permiso_chk.active else 0
        result = self.db.agregar_producto(codigo, nombre, cantidad, precio_sin_iva, impuesto, precio_con_iva, descuento, permiso)
        if result is None:
            self._mostrar_error("El codigo ya existe. Use un codigo diferente.")
            return

        self._cerrar_dialogo()
        self._cargar_productos()

    # ---- Agregar Stock ----
    def _mostrar_dialogo_stock(self):
        if self.dialog:
            self.dialog.dismiss()

        content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        self.s_codigo = MDTextField(
            hint_text="Codigo del producto *",
            mode="rectangle",
            size_hint_y=None,
            height=dp(45)
        )
        self.s_codigo.bind(text=self._buscar_producto_stock)
        content.add_widget(self.s_codigo)

        self.s_info = MDLabel(
            text="",
            size_hint_y=None,
            height=dp(25),
            font_size=14
        )
        content.add_widget(self.s_info)

        self.s_cantidad = MDTextField(
            hint_text="Cantidad a agregar (max 100) *",
            mode="rectangle",
            size_hint_y=None,
            height=dp(45),
            input_filter='int'
        )
        content.add_widget(self.s_cantidad)

        self.dialog = MDDialog(
            title="Agregar Stock",
            type="custom",
            content_cls=content,
            size_hint=(0.6, None),
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: self._cerrar_dialogo()),
                MDRaisedButton(text="CONFIRMAR", on_release=lambda x: self._confirmar_stock()),
            ]
        )
        self.dialog.open()

    def _buscar_producto_stock(self, instance, value):
        cod = value.strip().upper()
        if not cod:
            self.s_info.text = ""
            return
        prod = self.db.obtener_producto_por_codigo(cod)
        if prod:
            self.s_info.text = f"{prod['codigo']} - {prod['nombre']} (Stock actual: {prod['cantidad']})"
        else:
            self.s_info.text = "Producto no encontrado"

    def _confirmar_stock(self):
        codigo = self.s_codigo.text.strip().upper()
        cantidad_str = self.s_cantidad.text.strip()

        if not codigo or not cantidad_str:
            self._mostrar_error("Complete todos los campos.")
            return

        producto = self.db.obtener_producto_por_codigo(codigo)
        if not producto:
            self._mostrar_error("Producto no encontrado. Verifique el codigo.")
            return

        try:
            cantidad = int(cantidad_str)
        except ValueError:
            self._mostrar_error("Cantidad invalida.")
            return
        if cantidad <= 0:
            self._mostrar_error("La cantidad debe ser mayor a 0.")
            return
        if cantidad > 100:
            self._mostrar_error("No puede agregar mas de 100 unidades por vez.")
            return

        self.db.incrementar_stock(producto['id'], cantidad)
        self.db.conn.commit()
        self._cerrar_dialogo()
        self._cargar_productos()

    # ---- Utilidades ----
    def _mostrar_error(self, msg):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title="Error",
            text=msg,
            size_hint=(0.5, None),
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self._cerrar_dialogo())]
        )
        self.dialog.open()

    def _cerrar_dialogo(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

    def _volver(self):
        self.manager.current = 'main'
        self.manager.transition.direction = 'right'
