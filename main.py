from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.garden.graph import MeshLinePlot
from plyer import accelerometer
from plyer import gps

Builder.load_file("PitsAndRoads.kv")


class GyroscopeScreen(Screen):
    def __init__(self):
        super().__init__()
        self.graph = self.ids.graph_plot
        self.counter = 0

        # For all X, Y and Z axes
        self.plot = []
        self.plot.append(MeshLinePlot(color=[1, 0, 0, 1]))  # X - Red
        self.plot.append(MeshLinePlot(color=[0, 1, 0, 1]))  # Y - Green
        self.plot.append(MeshLinePlot(color=[0, 0, 1, 1]))  # Z - Blue

        self.reset_plots()

        for plot in self.plot:
            self.graph.add_plot(plot)

    facade = ObjectProperty()

    def reset_plots(self):
        for plot in self.plot:
            plot.points = [(0, 0)]

        self.counter = 1

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
            self.reset_plots()
            Clock.unschedule(self.get_rotation)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            status = "Гироскоп не поддерживается ващей платформой"
            self.ids.accel_status.text = status

    def get_rotation(self, dt):
        if self.counter == 100:
            # We re-write our points list if number of values exceed 100.
            # ie. Move each timestamp to the left.
            for plot in self.plot:
                del plot.points[0]
                plot.points[:] = [(i[0] - 1, i[1]) for i in plot.points[:]]

            self.counter = 99

        if self.facade.rotation != (None, None, None):
            self.plot[0].points.append((self.counter, self.facade.rotation[0]))
            self.plot[1].points.append((self.counter, self.facade.rotation[1]))
            self.plot[2].points.append((self.counter, self.facade.rotation[2]))
            self.ids.accel_status.text = f"X: {round(self.facade.rotation[0], 4)}, Y: {round(self.facade.rotation[1], 4)}, Z: {round(self.facade.rotation[2], 4)}"

        self.counter += 1


class AccelerometerScreen(Screen):
    def __init__(self):
        super().__init__()

        self.sensorEnabled = False
        self.graph = self.ids.graph_plot
        self.counter = 0

        # For all X, Y and Z axes
        self.plot = []
        self.plot.append(MeshLinePlot(color=[1, 0, 0, 1]))  # X - Red
        self.plot.append(MeshLinePlot(color=[0, 1, 0, 1]))  # Y - Green
        self.plot.append(MeshLinePlot(color=[0, 0, 1, 1]))  # Z - Blue

        self.reset_plots()

        for plot in self.plot:
            self.graph.add_plot(plot)

    def reset_plots(self):
        for plot in self.plot:
            plot.points = [(0, 0)]

        self.counter = 1

    def do_toggle(self):
        try:
            if not self.sensorEnabled:
                accelerometer.enable()
                Clock.schedule_interval(self.get_acceleration, 1 / 20.)

                self.sensorEnabled = True
                self.ids.accelerometer.text = "Остановить аккселерометр"
            else:
                accelerometer.disable()
                self.reset_plots()
                Clock.unschedule(self.get_acceleration)

                self.sensorEnabled = False
                self.ids.accelerometer.text = "Запустить аккселерометр"
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            status = "Аккселерометр не поддерживается ващей платформой"
            self.ids.accel_status.text = status

    def get_acceleration(self, dt):
        if self.counter == 100:
            # We re-write our points list if number of values exceed 100.
            # ie. Move each timestamp to the left.
            for plot in self.plot:
                del plot.points[0]
                plot.points[:] = [(i[0] - 1, i[1]) for i in plot.points[:]]

            self.counter = 99

        val = accelerometer.acceleration[:3]

        if not val == (None, None, None):
            self.plot[0].points.append((self.counter, val[0]))
            self.plot[1].points.append((self.counter, val[1]))
            self.plot[2].points.append((self.counter, val[2]))
            self.ids.accel_status.text = f"X: {round(val[0], 4)}, Y: {round(val[1], 4)}, Z: {round(val[2], 4)}"

        self.counter += 1


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
        # from android.permissions import request_permissions, Permission
        # request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        return sm

    def on_pause(self):
        return True


if __name__ == "__main__":
    PistAndRoadsApp().run()
