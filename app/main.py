from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

from kivy.lang import Builder
from kivy.properties import ObjectProperty

import cenote.tank
import cenote.config
import cenote.usage

import sys


_TANK_NAMES = [tank.name for tank in list(cenote.tank.Tank)]
_PRESSURE_RATE_UNITS = [
        "psi/min",
        "bar/min",
]
_VOLUME_RATE_UNITS = [
    "ft^3/min",
    "L/min",
]


class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class MenuHeader(MDBoxLayout):
    """Used by the Selector Menus, no clue why I need this."""


class SelectorMenu(MDDropdownMenu):
    def __init__(self, caller, callback, options: list[str]):
        self._external_callback = callback
        super().__init__(
            header_cls=MenuHeader(),
            caller=caller,
            items=[
                {
                    "viewclass": "OneLineListItem", 
                    "text": option,
                    "on_release": lambda x=f"{option}": self._select_callback(x),
                }
                for option in options
            ],
            width_mult=4,
        )
    
    def _select_callback(self, selection: str):
        self._external_callback(selection)
        self.dismiss()   
        self.caller.text = selection


class ScrFromSacTool:
    def __init__(self, app):
        self.app = app
        # ui elements created here
        self.sac_unit_menu = SelectorMenu(
            caller=app.screen.ids.scr_from_sac_sac_unit_button,
            callback = self.sac_unit_select_callback,
            options=_PRESSURE_RATE_UNITS,
        )
        self.tank_menu = SelectorMenu(
            caller=app.screen.ids.scr_from_sac_tank_button, 
            callback=self.tank_select_callback,
            options = _TANK_NAMES,
        )
        self.scr_unit_menu = SelectorMenu(
            caller=app.screen.ids.scr_from_sac_scr_unit_button,
            callback=self.scr_unit_select_callback,
            options=_VOLUME_RATE_UNITS,
        )
        # internal variables
        self.sac_unit = None
        self.tank = None
        self.scr_unit = None

    def sac_unit_select_callback(self, selection: str):
        self.sac_unit = cenote.config.UREG.parse_expression(selection)

    def tank_select_callback(self, selection: str):
        self.tank = cenote.tank.TYPES[cenote.tank.Tank[selection]].create_full(cenote.mix.AIR)

    def scr_unit_select_callback(self, selection: str):
        self.scr_unit = cenote.config.UREG.parse_expression(selection)

    def calc_callback(self):
        sac = float(self.app.screen.ids.scr_from_sac_sac_box.text) * self.sac_unit
        scr = cenote.usage.Scr.from_sac(sac, self.tank)
        scr_text = "{:.2f}".format(scr.volume_rate.to(self.scr_unit).magnitude)
        self.app.screen.ids.scr_from_sac_scr_box.text = scr_text


class CenoteApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("cenote.kv", "r") as f:
            self.screen = Builder.load_string(f.read())

        self.scr_from_sac = ScrFromSacTool(self)

    def build(self):
        # Theme
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "100"

        return self.screen


if __name__ == "__main__":
    CenoteApp().run()