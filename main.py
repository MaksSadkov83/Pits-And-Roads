from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from plyer import accelerometer
from plyer import gps

Builder.load_file("PitsAndRoads.kv")


class GyroscopeScreen(Screen):
    x_calib = NumericProperty(0)
    y_calib = NumericProperty(0)
    z_calib = NumericProperty(0)

    facade = ObjectProperty()

    def enable(self):
        try:
            self.facade.enable()
            Clock.schedule_interval(self.get_rotation, 1 / 20.)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            status = "Гироскоп не поддерживается ващей платформой"
            self.ids.accel_status.text = status

    def disable(self):
        try:
            self.facade.disable()
            Clock.unschedule(self.get_rotation)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            status = "Гироскоп не поддерживается ващей платформой"
            self.ids.accel_status.text = status

    def get_rotation(self, dt):
        if self.facade.rotation != (None, None, None):
            self.x_calib, self.y_calib, self.z_calib = self.facade.rotation


class AccelerometerScreen(Screen):
    def __init__(self):
        super().__init__()
        self.sensorEnabled = False

    def do_toggle(self):
        try:
            if not self.sensorEnabled:
                accelerometer.enable()
                Clock.schedule_interval(self.get_acceleration, 1 / 20.)

                self.sensorEnabled = True
                self.ids.accelerometer.text = "Остановить аккселерометр"
            else:
                accelerometer.disable()
                Clock.unschedule(self.get_acceleration)

                self.sensorEnabled = False
                self.ids.accelerometer.text = "Запустить аккселерометр"
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            status = "Аккселерометр не поддерживается ващей платформой"
            self.ids.accel_status.text = status

    def get_acceleration(self, dt):
        val = accelerometer.acceleration[:3]

        if not val == (None, None, None):
            self.ids.x_accelerometer.text = "X: " + str(round(val[0], 4)) + " g"
            self.ids.y_accelerometer.text = "Y: " + str(round(val[1], 4)) + " g"
            self.ids.z_accelerometer.text = "Z: " + str(round(val[2], 4)) + " g"


class CompassScreen(Screen):
    x_calib = NumericProperty(0)
    y_calib = NumericProperty(0)
    z_calib = NumericProperty(0)
    facade = ObjectProperty()

    def enable(self):
        try:
            self.facade.enable()
            Clock.schedule_interval(self.get_field, 1 / 20.)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            status = "Компасс не поддерживается ващей платформой"
            self.ids.accel_status.text = status

    def disable(self):
        try:
            self.facade.disable()
            Clock.unschedule(self.get_field)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            status = "Компасс не поддерживается ващей платформой"
            self.ids.accel_status.text = status

    def get_field(self, dt):
        if self.facade.field != (None, None, None):
            self.x_calib, self.y_calib, self.z_calib = self.facade.field


class GPSScreen(Screen):
    gps_location = StringProperty()
    gps_status = StringProperty('Нажмите на кнопку Старт для запуска GPS')

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def start(self, minTime, minDistance):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
            gps.start(minTime, minDistance)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS не поддерживается вашей платформой'


    def stop(self):
        try:
            gps.stop()
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS не поддерживается вашей платформой'

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(500, 0)
        pass


class MainMenuScreen(Screen):
    pass


class PistAndRoadsApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="MainMenu"))
        sm.add_widget(AccelerometerScreen())
        sm.add_widget(CompassScreen())
        sm.add_widget(GPSScreen(name="GPS"))
        sm.add_widget(GyroscopeScreen())
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        return sm

    def on_pause(self):
        return True


if __name__ == "__main__":
    PistAndRoadsApp().run()
