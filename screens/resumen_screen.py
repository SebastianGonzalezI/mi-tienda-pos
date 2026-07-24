import calendar
from datetime import datetime

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog

from database.db_manager import DatabaseManager
from utils.export_csv import exportar_mensual_csv

PASSWORD = "PuercoTonto1"


class DailyChartBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(1)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        self.daily_totals = []

        self.bar_area = Widget(size_hint_y=None, height=dp(130))
        self.bar_area.bind(pos=self._draw, size=self._draw)
        self.add_widget(self.bar_area)

        self.labels_row = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(16),
            padding=[dp(8), 0, dp(8), 0]
        )
        self.add_widget(self.labels_row)

    def set_data(self, daily_totals):
        self.daily_totals = daily_totals
        self.labels_row.clear_widgets()
        days = len(daily_totals)
        for d in range(days):
            if d % 5 == 0 or d == days - 1:
                lbl = MDLabel(text=str(d + 1), halign='center', font_size=10)
            else:
                lbl = Widget()
            self.labels_row.add_widget(lbl)
        self._draw()

    def _draw(self, *args):
        self.bar_area.canvas.clear()
        if not self.bar_area.size[0] or not self.daily_totals:
            return
        days = len(self.daily_totals)
        max_val = max(self.daily_totals) or 1

        w = self.bar_area.width
        h = self.bar_area.height
        left = dp(8)
        right = dp(8)
        top = dp(5)
        bottom = dp(5)
        chart_w = w - left - right
        chart_h = h - top - bottom
        bar_w = chart_w / days
        bar_draw_w = max(dp(3), bar_w - dp(1))

        with self.bar_area.canvas:
            for i, val in enumerate(self.daily_totals):
                bar_h = (val / max_val) * chart_h
                x = self.bar_area.x + left + i * bar_w + (bar_w - bar_draw_w) / 2
                if val > 0:
                    Color(0.13, 0.59, 0.95, 1)
                else:
                    Color(0.15, 0.15, 0.15, 0.15)
                Rectangle(pos=(x, self.bar_area.y + bottom), size=(bar_draw_w, max(bar_h, 1)))


class ResumenScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.dialog = None
        self._accion_password = None
        ahora = datetime.now()
        self.mes = ahora.month
        self.anio = ahora.year
        self._build_ui()

    def _crear_card(self, title, content_widgets, cols=1):
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(6),
            md_bg_color=(0.18, 0.18, 0.18, 1)
        )
        title_lbl = MDLabel(
            text=title,
            font_style='Subtitle1',
            bold=True,
            size_hint_y=None,
            height=dp(24)
        )
        card.add_widget(title_lbl)
        inner = GridLayout(cols=cols, spacing=dp(4), size_hint_y=None)
        inner.bind(minimum_height=inner.setter('height'))
        for w in content_widgets:
            inner.add_widget(w)
        card.add_widget(inner)
        card.bind(minimum_height=card.setter('height'))
        return card

    def _lbl(self, text, bold=False, color=None):
        kwargs = {
            'text': text,
            'size_hint_y': None,
            'height': dp(22),
            'font_style': 'Body1'
        }
        if bold:
            kwargs['bold'] = True
        if color:
            kwargs['theme_text_color'] = 'Custom'
            kwargs['text_color'] = color
        return MDLabel(**kwargs)

    def _build_ui(self):
        toolbar = MDTopAppBar(
            title='Resumen Mensual',
            md_bg_color=(0.13, 0.13, 0.13, 1),
            specific_text_color='#FFFFFF',
            left_action_items=[['arrow-left', lambda x: self._volver()]]
        )

        nav = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[dp(20), dp(5), dp(20), dp(5)]
        )
        self.mes_label = MDLabel(
            text='',
            halign='center',
            font_style='H6',
            size_hint_x=1
        )
        btn_prev = MDIconButton(icon='chevron-left', on_release=lambda x: self._cambiar_mes(-1))
        btn_next = MDIconButton(icon='chevron-right', on_release=lambda x: self._cambiar_mes(1))
        nav.add_widget(btn_prev)
        nav.add_widget(self.mes_label)
        nav.add_widget(btn_next)

        scroll = ScrollView()
        self.content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(15), dp(10), dp(15), dp(10)],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))

        self.summary_card = self._crear_card('Resumen', [
            self._lbl('', bold=True),
            self._lbl('', bold=True),
            self._lbl('', bold=True),
            self._lbl('', bold=True),
        ], cols=1)
        self.content.add_widget(self.summary_card)

        grid2 = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        grid2.bind(minimum_height=grid2.setter('height'))

        self.pago_card = self._crear_card('Metodos de Pago', [
            self._lbl(''),
            self._lbl(''),
            self._lbl(''),
        ], cols=1)
        grid2.add_widget(self.pago_card)

        self.egresos_card = self._crear_card('Egresos', [
            self._lbl('Sin egresos'),
        ], cols=1)
        grid2.add_widget(self.egresos_card)

        self.content.add_widget(grid2)

        self.chart_card = self._crear_card('Ventas por Dia', [
            self._lbl(''),
        ], cols=1)
        self.content.add_widget(self.chart_card)

        self.top_card = self._crear_card('Top 5 Productos', [
            self._lbl('Sin ventas'),
        ], cols=1)
        self.content.add_widget(self.top_card)

        self.ventas_card = self._crear_card('Ventas del Mes', [
            self._lbl('Sin ventas'),
        ], cols=2)
        self.content.add_widget(self.ventas_card)

        self.content.add_widget(MDLabel(text='', size_hint_y=None, height=dp(5)))

        self.btn_exportar = MDRaisedButton(
            text='Exportar a CSV',
            size_hint=(0.5, None),
            height=dp(48),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0, 0.6, 0.3, 1),
            font_size=16,
            on_release=self._exportar_csv
        )
        self.content.add_widget(self.btn_exportar)

        scroll.add_widget(self.content)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(toolbar)
        layout.add_widget(nav)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self._pedir_password()

    def _pedir_password(self):
        if self.dialog:
            self.dialog.dismiss()
        self._accion_password = self._actualizar
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
            text="Ingrese la contrasena para acceder al resumen mensual",
            type="custom",
            content_cls=content,
            size_hint=(0.5, None),
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: self._cancelar_acceso()),
                MDRaisedButton(text="CONFIRMAR", on_release=lambda x: self._verificar_password()),
            ]
        )
        self.dialog.open()

    def _verificar_password(self):
        if self.pw_input.text == PASSWORD:
            if self.dialog:
                self.dialog.dismiss()
                self.dialog = None
            if self._accion_password:
                self._accion_password()
        else:
            self.pw_input.text = ""
            self.pw_input.hint_text = "Contrasena incorrecta. Intente nuevamente."

    def _cancelar_acceso(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        self._volver()

    def _actualizar(self):
        self.mes_label.text = f"{self.mes:02d} - {self.anio}"
        resumen = self.db.obtener_resumen_mensual(self.mes, self.anio)
        top = self.db.obtener_top_productos(self.mes, self.anio)
        verde = (0, 1, 0, 1)
        rojo = (1, 0.3, 0.3, 1)
        blanco = (1, 1, 1, 1)

        self._set_card_text(self.summary_card, [
            self._lbl(f"Ventas: {resumen['cantidad_ventas']}", bold=True),
            self._lbl(f"Ingresos:    ${resumen['total_ingresos']:.2f}", color=verde),
            self._lbl(f"Egresos:     ${resumen['total_egresos']:.2f}", color=rojo),
            self._lbl(f"Ganancia:    ${resumen['ganancia_neta']:.2f}", color=verde if resumen['ganancia_neta'] >= 0 else rojo),
        ])

        self._set_card_text(self.pago_card, [
            self._lbl(f"Efectivo:      ${resumen['total_efectivo']:.2f}"),
            self._lbl(f"Tarjeta:       ${resumen['total_tarjeta']:.2f}"),
            self._lbl(f"Transferencia: ${resumen['total_transferencia']:.2f}"),
        ])

        # Daily sales bar chart
        days_in_month = calendar.monthrange(self.anio, self.mes)[1]
        daily_totals = [0.0] * days_in_month
        days_with_sales = 0
        for v in resumen['detalle_ventas']:
            day = int(v['fecha_hora'][8:10])
            if daily_totals[day - 1] == 0:
                days_with_sales += 1
            daily_totals[day - 1] += v['total']
        chart = DailyChartBar()
        chart.set_data(daily_totals)
        self._set_card_text(self.chart_card, [
            chart,
            self._lbl(f"Total: ${resumen['total_ventas']:.2f}  |  Dias con venta: {days_with_sales}", bold=True),
        ], cols=1)

        if resumen['egresos']:
            egreso_widgets = []
            for e in resumen['egresos']:
                egreso_widgets.append(self._lbl(f"${e['monto']:.2f} - {e['descripcion']}"))
            self._set_card_text(self.egresos_card, egreso_widgets)
        else:
            self._set_card_text(self.egresos_card, [self._lbl('Sin egresos')])

        if top:
            top_widgets = []
            for i, p in enumerate(top, 1):
                top_widgets.append(self._lbl(f"{i}. {p['nombre']} ({p['total_qty']} und) ${p['total_sub']:.2f}"))
            self._set_card_text(self.top_card, top_widgets)
        else:
            self._set_card_text(self.top_card, [self._lbl('Sin ventas')])

        if resumen['detalle_ventas']:
            v_widgets = []
            v_widgets.append(self._lbl("Cliente", bold=True))
            v_widgets.append(self._lbl("Usuario", bold=True))
            v_widgets.append(self._lbl("Total", bold=True))
            v_widgets.append(self._lbl("Pago", bold=True))
            for v in resumen['detalle_ventas']:
                v_widgets.append(self._lbl(f"{v['cliente'][:20]}"))
                v_widgets.append(self._lbl(f"{v['usuario']}"))
                v_widgets.append(self._lbl(f"${v['total']:.2f}"))
                v_widgets.append(self._lbl(f"{v['metodo_pago']}"))
            self._set_card_text(self.ventas_card, v_widgets, cols=4)
        else:
            self._set_card_text(self.ventas_card, [self._lbl('Sin ventas')], cols=1)

    def _set_card_text(self, card, widgets, cols=None):
        inner = card.children[0]
        if not isinstance(inner, GridLayout):
            return
        inner.clear_widgets()
        if cols:
            inner.cols = cols
        for w in widgets:
            inner.add_widget(w)

    def _cambiar_mes(self, delta):
        self.mes += delta
        if self.mes > 12:
            self.mes = 1
            self.anio += 1
        elif self.mes < 1:
            self.mes = 12
            self.anio -= 1
        self._actualizar()

    def _exportar_csv(self, *args):
        resumen = self.db.obtener_resumen_mensual(self.mes, self.anio)
        try:
            ruta = exportar_mensual_csv(resumen, self.mes, self.anio)
            self._mostrar_dialogo('Exportado', f'Reporte guardado en:\n{ruta}')
        except Exception as e:
            self._mostrar_dialogo('Error', f'No se pudo exportar:\n{e}')

    def _volver(self):
        self.manager.current = 'main'
        self.manager.transition.direction = 'right'

    def _mostrar_dialogo(self, titulo, mensaje):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=titulo, text=mensaje, size_hint=(0.8, None),
            buttons=[MDFlatButton(text='OK', on_release=lambda x: self._cerrar_dialogo())]
        )
        self.dialog.open()

    def _cerrar_dialogo(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
