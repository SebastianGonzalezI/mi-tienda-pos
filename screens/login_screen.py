from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from datetime import datetime

from database.db_manager import DatabaseManager


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.dialog = None
        self._evento_reloj = None
        self.jornada_activa = None
        self._build_ui()

    def _build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(40), dp(30), dp(40), dp(30)],
            size_hint=(0.5, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.bind(minimum_height=layout.setter('height'))

        logo = MDLabel(
            text='VETERINARIA',
            font_style='H2',
            halign='center',
            theme_text_color='Primary',
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        layout.add_widget(logo)

        subtitulo = MDLabel(
            text='Control de Jornada',
            font_style='H6',
            halign='center',
            theme_text_color='Secondary',
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(subtitulo)

        self.fecha_hora_label = MDLabel(
            text='',
            font_style='Subtitle1',
            halign='center',
            theme_text_color='Hint',
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(self.fecha_hora_label)

        layout.add_widget(MDLabel(size_hint_y=None, height=dp(20)))

        self.usuario_input = MDTextField(
            hint_text='Nombre del Usuario',
            mode='rectangle',
            size_hint_y=None,
            height=dp(50),
            max_text_length=50
        )
        layout.add_widget(self.usuario_input)

        self.caja_input = MDTextField(
            hint_text='Caja Chica Inicial $',
            mode='rectangle',
            size_hint_y=None,
            height=dp(50),
            input_filter='float',
            max_text_length=7
        )
        layout.add_widget(self.caja_input)

        self.btn_iniciar = MDRaisedButton(
            text='INICIAR JORNADA',
            size_hint=(0.8, None),
            height=dp(55),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.2, 0.7, 0.2, 1),
            font_size=18
        )
        self.btn_iniciar.bind(on_release=self._iniciar_jornada)
        layout.add_widget(self.btn_iniciar)

        self.jornada_info = MDLabel(
            text='',
            font_style='Body1',
            halign='center',
            theme_text_color='Custom',
            text_color=(1, 0.8, 0, 1),
            size_hint_y=None,
            height=dp(0)
        )
        layout.add_widget(self.jornada_info)

        self.btn_continuar = MDFlatButton(
            text='CONTINUAR CON JORNADA ACTIVA',
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            text_color=(0.2, 0.7, 0.2, 1),
            font_size=16
        )
        self.btn_continuar.bind(on_release=self._continuar_jornada)
        layout.add_widget(self.btn_continuar)

        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def on_enter(self):
        self._actualizar_reloj()
        self._evento_reloj = Clock.schedule_interval(lambda dt: self._actualizar_reloj(), 1)
        self._verificar_jornada_activa()

    def on_leave(self):
        if self._evento_reloj:
            self._evento_reloj.cancel()
            self._evento_reloj = None

    def _actualizar_reloj(self):
        ahora = datetime.now()
        self.fecha_hora_label.text = ahora.strftime('%d/%m/%Y  %H:%M:%S')

    def _verificar_jornada_activa(self):
        self.jornada_activa = self.db.obtener_jornada_activa()
        if self.jornada_activa:
            caja = self.jornada_activa.get('caja_chica_inicial', 0)
            self.jornada_info.text = (
                f"Jornada activa: {self.jornada_activa['usuario']} "
                f"desde {self.jornada_activa['hora_inicio']}\n"
                f"Caja Chica: ${caja:.2f}"
            )
            self.jornada_info.size_hint_y = None
            self.jornada_info.height = dp(50)
            self.btn_continuar.disabled = False
            self.btn_continuar.opacity = 1
        else:
            self.jornada_info.text = ''
            self.jornada_info.size_hint_y = None
            self.jornada_info.height = dp(0)
            self.btn_continuar.disabled = True
            self.btn_continuar.opacity = 0

    def _iniciar_jornada(self, *args):
        usuario = self.usuario_input.text.strip().upper()
        if not usuario:
            self._mostrar_dialogo('Error', 'Ingrese el nombre del usuario')
            return

        caja_str = self.caja_input.text.strip()
        if not caja_str:
            self._mostrar_dialogo('Error', 'Ingrese el monto de caja chica')
            return

        try:
            caja_chica = float(caja_str)
        except ValueError:
            self._mostrar_dialogo('Error', 'Monto de caja chica invalido')
            return

        if caja_chica <= 0:
            self._mostrar_dialogo('Error', 'La caja chica debe ser mayor a 0')
            return
        if caja_chica > 100:
            self._mostrar_dialogo('Error', 'La caja chica no puede ser mayor a $100.00')
            return

        activa = self.db.obtener_jornada_activa()
        if activa:
            self._mostrar_dialogo(
                'Jornada Activa',
                f'Ya hay una jornada activa para hoy:\n{activa["usuario"]} desde {activa["hora_inicio"]}'
            )
            return

        jornada_id = self.db.iniciar_jornada(usuario, caja_chica)
        if jornada_id:
            self._mostrar_dialogo(
                'Jornada Iniciada',
                f'Jornada iniciada correctamente.\nUsuario: {usuario}\nCaja Chica: ${caja_chica:.2f}',
                callback=lambda: self._ir_a_facturacion()
            )

    def _continuar_jornada(self, *args):
        self._ir_a_facturacion()

    def _ir_a_facturacion(self):
        self.manager.current = 'main'
        self.manager.transition.direction = 'left'

    def _mostrar_dialogo(self, titulo, mensaje, callback=None):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=titulo,
            text=mensaje,
            buttons=[
                MDFlatButton(
                    text='ACEPTAR',
                    on_release=lambda x: self._cerrar_dialogo(callback)
                )
            ]
        )
        self.dialog.open()

    def _cerrar_dialogo(self, callback=None):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if callback:
            callback()
