import threading
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scheduler.log'
)
logger = logging.getLogger('scheduler')


class JornadaScheduler:
    def __init__(self, app):
        self.app = app
        self._hilo = None
        self._activo = False
        self._intervalo = 60

    def iniciar(self):
        if self._activo:
            return
        self._activo = True
        self._hilo = threading.Thread(target=self._ejecutar, daemon=True)
        self._hilo.start()
        logger.info('Scheduler iniciado')

    def detener(self):
        self._activo = False
        logger.info('Scheduler detenido')

    def _ejecutar(self):
        while self._activo:
            try:
                self._verificar_cierre_automatico()
            except Exception as e:
                logger.error(f'Error en scheduler: {e}')
            for _ in range(self._intervalo):
                if not self._activo:
                    return
                time.sleep(1)

    def _verificar_cierre_automatico(self):
        ahora = datetime.now()
        if ahora.hour == 22 and ahora.minute == 0:
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            jornada = db.obtener_jornada_activa()
            if jornada:
                logger.info('Cierre automatico activado')
                resumen = db.obtener_resumen_jornada(jornada['id'])
                self.app.clock_schedule_once(
                    lambda dt: self._mostrar_popup_cierre_automatico(jornada, resumen),
                    0
                )

    def _mostrar_popup_cierre_automatico(self, jornada, resumen):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton
        from utils.jornada_utils import generar_resumen_texto

        texto = generar_resumen_texto(resumen, jornada)
        dialog = MDDialog(
            title='CIERRE AUTOMATICO DE CAJA',
            text=f'Horario de cierre (22:00) alcanzado.\n\n{texto}',
            size_hint=(0.85, None),
            buttons=[
                MDRaisedButton(
                    text='CONFIRMAR CIERRE AUTOMATICO',
                    md_bg_color=(0.8, 0.5, 0, 1),
                    on_release=lambda x: self._ejecutar_cierre_automatico(jornada, dialog)
                )
            ]
        )
        dialog.open()

    def _ejecutar_cierre_automatico(self, jornada, dialog):
        dialog.dismiss()
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        db.cerrar_jornada(jornada['id'], 'automatico')
        logger.info(f'Cierre automatico ejecutado para jornada {jornada["id"]}')
        self.app.clock_schedule_once(lambda dt: self._volver_inicio(), 0)

    def _volver_inicio(self):
        if hasattr(self.app, 'root') and self.app.root:
            self.app.root.current = 'login'
            self.app.root.transition.direction = 'right'
