from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from datetime import datetime

from database.db_manager import DatabaseManager
from utils.jornada_utils import calcular_duracion_jornada
from utils.report_txt import generar_reporte_cierre


class CierreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.dialog = None
        self.tipo_cierre = 'manual'
        self._build_ui()

    def _lbl(self, text, bold=False, color=None, size=16):
        kwargs = {
            'text': text,
            'size_hint_y': None,
            'height': dp(22),
            'font_size': size
        }
        if bold:
            kwargs['bold'] = True
        if color:
            kwargs['theme_text_color'] = 'Custom'
            kwargs['text_color'] = color
        return MDLabel(**kwargs)

    def _card(self, title, widgets, cols=1):
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(6),
            md_bg_color=(0.18, 0.18, 0.18, 1)
        )
        title_lbl = MDLabel(
            text=title, font_style='Subtitle1', bold=True,
            size_hint_y=None, height=dp(24)
        )
        card.add_widget(title_lbl)
        inner = GridLayout(cols=cols, spacing=dp(4), size_hint_y=None)
        inner.bind(minimum_height=inner.setter('height'))
        for w in widgets:
            inner.add_widget(w)
        card.add_widget(inner)
        card.bind(minimum_height=card.setter('height'))
        return card

    def _set_card(self, card, widgets, cols=None):
        inner = card.children[0]
        if not isinstance(inner, GridLayout):
            return
        inner.clear_widgets()
        if cols:
            inner.cols = cols
        for w in widgets:
            inner.add_widget(w)

    def _build_ui(self):
        toolbar = MDTopAppBar(
            title='Cierre de Jornada',
            md_bg_color=(0.13, 0.13, 0.13, 1),
            specific_text_color='#FFFFFF',
            left_action_items=[['arrow-left', lambda x: self._volver()]]
        )

        scroll = ScrollView()
        self.content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(15), dp(10), dp(15), dp(10)],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))

        self.jornada_card = self._card('Jornada', [
            self._lbl('Sin jornada activa', color=(1, 0.3, 0.3, 1))
        ])
        self.content.add_widget(self.jornada_card)

        grid2 = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        grid2.bind(minimum_height=grid2.setter('height'))

        self.ventas_card = self._card('Ventas', [
            self._lbl('Cargando...')
        ])
        grid2.add_widget(self.ventas_card)

        self.pago_card = self._card('Metodo de Pago', [
            self._lbl('')
        ])
        grid2.add_widget(self.pago_card)

        self.content.add_widget(grid2)

        self.prod_card = self._card('Productos Vendidos', [
            self._lbl('')
        ])
        self.content.add_widget(self.prod_card)

        self.egresos_card = self._card('Egresos', [
            self._lbl('Sin egresos')
        ])
        self.content.add_widget(self.egresos_card)

        self.content.add_widget(MDLabel(text='', size_hint_y=None, height=dp(5)))

        self.caja_card = self._card('Caja Chica', [
            self._lbl('Cargando...')
        ])
        self.content.add_widget(self.caja_card)

        self.content.add_widget(MDLabel(text='', size_hint_y=None, height=dp(5)))

        egreso_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(8),
            md_bg_color=(0.18, 0.18, 0.18, 1)
        )
        egreso_card.bind(minimum_height=egreso_card.setter('height'))
        egreso_card.add_widget(MDLabel(
            text='Registrar Egreso', font_style='Subtitle1', bold=True,
            size_hint_y=None, height=dp(24)
        ))
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        self.egreso_motivo = MDTextField(
            hint_text='Motivo', mode='rectangle', size_hint_x=0.45
        )
        self.egreso_monto = MDTextField(
            hint_text='Monto $', mode='rectangle', size_hint_x=0.25,
            input_filter='float'
        )
        btn_reg = MDFlatButton(
            text='Registrar', size_hint_x=0.2, size_hint_y=None, height=dp(45)
        )
        btn_reg.bind(on_release=self._registrar_egreso)
        row.add_widget(self.egreso_motivo)
        row.add_widget(self.egreso_monto)
        row.add_widget(btn_reg)
        egreso_card.add_widget(row)
        self.content.add_widget(egreso_card)

        self.content.add_widget(MDLabel(text='', size_hint_y=None, height=dp(5)))

        self.btn_cerrar = MDRaisedButton(
            text='CERRAR JORNADA',
            size_hint=(0.6, None),
            height=dp(55),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.8, 0.2, 0.2, 1),
            font_size=18
        )
        self.btn_cerrar.bind(on_release=self._confirmar_cierre)
        self.content.add_widget(self.btn_cerrar)

        scroll.add_widget(self.content)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(toolbar)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self._cargar_resumen()

    def _cargar_resumen(self):
        jornada = self.db.obtener_jornada_activa()
        if not jornada:
            self._set_card(self.jornada_card, [
                self._lbl('No hay jornada activa', color=(1, 0.3, 0.3, 1))
            ])
            self.btn_cerrar.disabled = True
            return

        self.btn_cerrar.disabled = False
        resumen = self.db.obtener_resumen_jornada(jornada['id'])
        duracion = calcular_duracion_jornada(jornada['hora_inicio'])
        verde = (0, 1, 0, 1); rojo = (1, 0.3, 0.3, 1); blanco = (1, 1, 1, 1)

        self._set_card(self.jornada_card, [
            self._lbl(f"Usuario: {jornada['usuario']}", bold=True),
            self._lbl(f"Inicio:  {jornada['hora_inicio']}   Duracion: {duracion}"),
            self._lbl(f"Fecha:   {jornada['fecha']}"),
        ])

        self._set_card(self.ventas_card, [
            self._lbl(f"Cantidad: {resumen['cantidad_ventas']}"),
            self._lbl(f"Total:    ${resumen['total_ventas']:.2f}", bold=True, color=verde),
        ])

        self._set_card(self.pago_card, [
            self._lbl(f"Efectivo:      ${resumen['total_efectivo']:.2f}"),
            self._lbl(f"Tarjeta:       ${resumen['total_tarjeta']:.2f}"),
            self._lbl(f"Transferencia: ${resumen['total_transferencia']:.2f}"),
        ])

        if resumen['productos_vendidos']:
            pw = []
            for nombre, data in sorted(resumen['productos_vendidos'].items(), key=lambda x: -x[1]['cantidad']):
                pw.append(self._lbl(f"{data['cantidad']}x {nombre}  (${data['subtotal']:.2f})"))
            self._set_card(self.prod_card, pw)
        else:
            self._set_card(self.prod_card, [self._lbl('Sin productos vendidos')])

        if resumen['egresos']:
            ew = []
            total_e = 0
            for e in resumen['egresos']:
                ew.append(self._lbl(f"${e['monto']:.2f} - {e['descripcion']}"))
                total_e += e['monto']
            ew.append(self._lbl(f"TOTAL: ${total_e:.2f}", bold=True, color=rojo))
            self._set_card(self.egresos_card, ew)
        else:
            self._set_card(self.egresos_card, [self._lbl('Sin egresos registrados')])

        cc_inicial = resumen.get('caja_chica_inicial', 0)
        cc_final = resumen.get('caja_chica_final', 0)
        self._set_card(self.caja_card, [
            self._lbl(f"Caja chica inicial: ${cc_inicial:.2f}", bold=True),
            self._lbl(f"Total ingresos:     ${resumen['total_ingresos']:.2f}", color=verde),
            self._lbl(f"Total egresos:      ${resumen['total_egresos']:.2f}", color=rojo),
            self._lbl(f"Caja chica final:   ${cc_final:.2f}", bold=True, color=verde if cc_final >= 0 else rojo),
        ])

    def _registrar_egreso(self, *args):
        jornada = self.db.obtener_jornada_activa()
        if not jornada:
            self._mostrar_dialogo('Error', 'No hay jornada activa')
            return

        motivo = self.egreso_motivo.text.strip().upper()
        monto_str = self.egreso_monto.text.strip()

        if not motivo:
            self._mostrar_dialogo('Error', 'Ingrese el motivo del egreso')
            return
        if not monto_str:
            self._mostrar_dialogo('Error', 'Ingrese el monto del egreso')
            return

        try:
            monto = float(monto_str)
            if monto <= 0:
                self._mostrar_dialogo('Error', 'El monto debe ser positivo')
                return
        except ValueError:
            self._mostrar_dialogo('Error', 'Monto invalido')
            return

        self.db.registrar_egreso(jornada['id'], monto, motivo)
        self.egreso_motivo.text = ''
        self.egreso_monto.text = ''
        self._cargar_resumen()
        self._mostrar_dialogo('Egreso Registrado', f'Egreso de ${monto:.2f} registrado: {motivo}')

    def _confirmar_cierre(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        jornada = self.db.obtener_jornada_activa()
        if not jornada:
            self._mostrar_dialogo('Error', 'No hay jornada activa')
            return

        resumen = self.db.obtener_resumen_jornada(jornada['id'])
        duracion = calcular_duracion_jornada(jornada['hora_inicio'])
        texto = f"Usuario: {jornada['usuario']}\nInicio: {jornada['hora_inicio']}\nDuracion: {duracion}\n"
        texto += f"Ventas: {resumen['cantidad_ventas']}\n"
        texto += f"Total: ${resumen['total_ventas']:.2f}\n"
        texto += f"Ingresos: ${resumen['total_ingresos']:.2f}\n"
        texto += f"Egresos: ${resumen['total_egresos']:.2f}\n"
        texto += f"Ganancia: ${resumen['ganancia_neta']:.2f}"

        self.dialog = MDDialog(
            title='Confirmar Cierre de Jornada',
            text=f'Esta seguro de cerrar la jornada?\n\n{texto}',
            size_hint=(0.8, None),
            buttons=[
                MDFlatButton(
                    text='CANCELAR',
                    on_release=lambda x: self._cerrar_dialogo()
                ),
                MDRaisedButton(
                    text='CONFIRMAR CIERRE',
                    md_bg_color=(0.8, 0.2, 0.2, 1),
                    on_release=lambda x: self._ejecutar_cierre()
                )
            ]
        )
        self.dialog.open()

    def _ejecutar_cierre(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

        jornada = self.db.obtener_jornada_activa()
        if not jornada:
            return

        self.db.cerrar_jornada(jornada['id'], self.tipo_cierre)
        resumen = self.db.obtener_resumen_jornada(jornada['id'])
        ruta = generar_reporte_cierre(jornada, resumen)
        self._mostrar_dialogo(
            'Jornada Cerrada',
            f'Jornada cerrada correctamente.\nTipo: {self.tipo_cierre.upper()}\n\nReporte guardado en:\n{ruta}',
            callback=lambda: self._volver_inicio()
        )

    def _volver(self):
        self.manager.current = 'main'
        self.manager.transition.direction = 'right'

    def _volver_inicio(self):
        self.manager.current = 'login'
        self.manager.transition.direction = 'right'

    def _mostrar_dialogo(self, titulo, mensaje, callback=None):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=titulo,
            text=mensaje,
            size_hint=(0.8, None),
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
