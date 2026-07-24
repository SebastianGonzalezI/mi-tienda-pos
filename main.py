import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', False)
Config.set('kivy', 'exit_on_escape', '1')

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivy.lang import Builder

from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen
from screens.inventory_screen import InventoryScreen
from screens.cierre_screen import CierreScreen
from screens.resumen_screen import ResumenScreen
from database.db_manager import DatabaseManager
from scheduler import JornadaScheduler
from utils.excel_loader import crear_excel_ejemplo


class POSApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scheduler = None
        self.theme_cls = ThemeManager()
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.accent_palette = 'Blue'
        self.theme_cls.primary_hue = '600'
        self.theme_cls.material_style = 'M3'

    def build(self):
        Window.size = (1280, 800)
        Window.minimum_width = 1280
        Window.minimum_height = 800

        db = DatabaseManager()
        db.inicializar_datos_ejemplo()

        try:
            crear_excel_ejemplo()
        except Exception as e:
            print(f'Error creating example Excel: {e}')

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main', db=db, app=self))
        sm.add_widget(InventoryScreen(name='inventario'))
        sm.add_widget(CierreScreen(name='cierre'))
        sm.add_widget(ResumenScreen(name='resumen'))

        jornada = db.obtener_jornada_activa()
        if jornada:
            sm.current = 'main'
        else:
            sm.current = 'login'

        self.scheduler = JornadaScheduler(self)
        self.scheduler.iniciar()

        return sm

    def mostrar_menu(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        dialog = MDDialog(
            title="Menu",
            size_hint=(0.4, None),
            buttons=[
                MDFlatButton(text="Inventario", on_release=lambda x: self._ir_a('inventario', dialog)),
                MDFlatButton(text="Resumen Mensual", on_release=lambda x: self._ir_a('resumen', dialog)),
                MDFlatButton(text="Cerrar Dia", on_release=lambda x: self._ir_a('cierre', dialog)),
                MDFlatButton(text="Cerrar Sesion", on_release=lambda x: self._ir_a('login', dialog)),
            ]
        )
        dialog.open()

    def _ir_a(self, screen, dialog):
        dialog.dismiss()
        if self.root:
            self.root.current = screen
            self.root.transition.direction = 'left'

    def on_stop(self):
        if self.scheduler:
            self.scheduler.detener()


if __name__ == '__main__':
    POSApp().run()
