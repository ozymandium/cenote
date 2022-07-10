from cenote import config
from cenote.water import water_pressure_from_depth, depth_from_pressure
from cenote.mix import Mix
import bungee

import dipplanner.model.buhlmann.model
import dipplanner.model.buhlmann.gradient


UREG = config.UREG


class BuhlmannParams:
    def __init__(self, gf_low, gf_high):
        self.gf_low = gf_low
        self.gf_high = gf_high


class DecoModelBase:
    pass


class DipplannerModel(DecoModelBase):
    def __init__(self, params: BuhlmannParams, water: bungee.Water):
        self.water = water

        # change some global settings in dipplanner
        self.model = dipplanner.model.buhlmann.model.Model()
        self.model.gradient = dipplanner.model.buhlmann.gradient.Gradient(
            gf_low=params.gf_low, gf_high=params.gf_high
        )
        # don't pass deco model argument. set the default value above and let the default be
        # used in case the default is referenced elsewhere.
        self.model.set_time_constants(deco_model="ZHL16b")
        self.model.validate_model()

    def log(self, pt0, pt1, mix: Mix):

        d_time = pt1.time - pt0.time

        # update the gf for the average depth of this section
        avg_depth = (pt0.depth + pt1.depth) * 0.5
        self.model.gradient.set_gf_at_depth(avg_depth.to(UREG.meter).magnitude)

        if pt0.depth == pt1.depth:
            # dipplanner adds the surface pressure to the pressure that is passed in here.
            # use water pressure, not absolute pressure.
            water_pressure = water_pressure_from_depth(pt0.depth, self.water)
            self.model.const_depth(
                pressure=water_pressure.to(UREG.bar).magnitude,
                seg_time=d_time.to(UREG.second).magnitude,
                f_he=0.0,
                f_n2=mix.pn2,
                pp_o2=0.0,  # use this for open circuit mode
            )
        else:
            # dipplanner adds the surface pressure to the pressure that is passed in here.
            # use water pressure, not absolute pressure.
            water_pressure_pt0 = water_pressure_from_depth(pt0.depth, self.water)
            water_pressure_pt1 = water_pressure_from_depth(pt1.depth, self.water)
            d_depth = pt1.depth - pt0.depth
            depth_rate = d_depth / d_time
            self.model.asc_desc(
                start=water_pressure_pt0.to(UREG.bar).magnitude,
                finish=water_pressure_pt1.to(UREG.bar).magnitude,
                rate=depth_rate.to(UREG.meter / UREG.second).magnitude,
                f_he=0.0,
                f_n2=mix.pn2,
                pp_o2=0.0,  # use this for open circuit mode
            )

    def set_gf_from_max_depth(self, depth):
        self.model.gradient.set_gf_slope_at_depth(depth.to(UREG.meter).magnitude)

    def ceiling(self):
        pressure_bar = self.model.ceiling_in_pabs()
        pressure = pressure_bar * UREG.bar
        return depth_from_pressure(pressure, self.water)
