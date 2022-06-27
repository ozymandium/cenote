from cenote import config
from cenote.water import Water, pressure_from_depth, depth_from_pressure
from cenote.mix import Mix

# import decotengu.model
# import decotengu.engine

import dipplanner.model.buhlmann.model
import dipplanner.model.buhlmann.gradient


UREG = config.UREG


class BuhlmannParams:
    def __init__(self, gf_low, gf_high):
        self.gf_low = gf_low
        self.gf_high = gf_high


class DecoModelBase:
    pass


# class DecotenguModel(DecoModelBase):

#     def __init__(self, params:BuhlmannParams, water: Water):
#         self.water = water

#         self.model = decotengu.model.ZH_L16C_GF()

#         # set gradient factors
#         self.model.gf_low = params.gf_low
#         self.model.gf_high = params.gf_high

#         # initialize with surface atmospheric pressure
#         self.data = self.model.init((1.0 * UREG.atm).to(UREG.bar).magnitude)

#     def log(self, pt0, pt1, mix: Mix):
       
#         # time is time spent at depth
#         d_time = (pt1.time - pt0.time).to(UREG.minute)
        
#         gas = decotengu.engine.GasMix(
#             # switch depth [m]?
#             # it appears this is when the gas is started during the decompression stage. not sure.
#             # putting mod here but it is probably wrong. doesn't seem to be used.
#             depth=mix.mod(1.4, self.water).to(UREG.meter).magnitude, 
#             o2=mix.po2 * 100, 
#             n2=mix.pn2 * 100, 
#             he=0)

#         pressure_pt0 = pressure_from_depth(pt0.depth, self.water).to(UREG.bar)
#         pressure_pt1 = pressure_from_depth(pt1.depth, self.water).to(UREG.bar)
#         d_pressure = pressure_pt1 - pressure_pt0
#         pressure_rate = d_pressure / d_time

#         avg_pressure = (pressure_pt0 + pressure_pt1) * 0.5

#         self.data = self.model.load(
#             abs_p=avg_pressure.to(UREG.bar).magnitude, 
#             time=d_time.to(UREG.minute).magnitude, 
#             gas=gas,
#             rate=pressure_rate.to(UREG.bar / UREG.minute).magnitude,
#             data=self.data)

#     def ceiling(self):
#         # need to figure out when to use gf high here.
#         pressure_bar = self.model.ceiling_limit(self.data)
#         pressure = pressure_bar * UREG.bar
#         return depth_from_pressure(pressure, self.water)

#     # def compartment_ceilings(self):

class DipplannerModel(DecoModelBase):

    def __init__(self, params:BuhlmannParams, water: Water):
        self.water = water

        # change some global settings in dipplanner
        self.model = dipplanner.model.buhlmann.model.Model()
        self.model.gradient = dipplanner.model.buhlmann.gradient.Gradient(gf_low=params.gf_low, gf_high=params.gf_high)
        # don't pass deco model argument. set the default value above and let the default be
        # used in case the default is referenced elsewhere.
        self.model.set_time_constants(deco_model="ZHL16c") 
        self.model.validate_model()

    def log(self, pt0, pt1, mix:Mix):
        
        d_time = pt1.time - pt0.time

        # update the gf for the average depth of this section
        avg_depth = (pt0.depth + pt1.depth) * 0.5
        self.model.gradient.set_gf_at_depth(avg_depth.to(UREG.meter).magnitude)

        if pt0.depth == pt1.depth:
            pressure = pressure_from_depth(pt0.depth, self.water)
            self.model.const_depth(
                pressure=pressure.to(UREG.bar).magnitude,
                seg_time=d_time.to(UREG.second).magnitude,
                f_he=0.0,
                f_n2=mix.pn2,
                pp_o2=0.0 # use this for open circuit mode
            )
        else:
            pressure_pt0 = pressure_from_depth(pt0.depth, self.water)
            pressure_pt1 = pressure_from_depth(pt1.depth, self.water)
            d_depth = pt1.depth - pt0.depth
            depth_rate = d_depth / d_time
            self.model.asc_desc(
                start=pressure_pt0.to(UREG.bar).magnitude,
                finish=pressure_pt1.to(UREG.bar).magnitude,
                rate=depth_rate.to(UREG.meter / UREG.second).magnitude,
                f_he=0.0,
                f_n2=mix.pn2,
                pp_o2=0.0 # use this for open circuit mode
            )

    def set_gf_from_max_depth(self, depth):
        self.model.gradient.set_gf_slope_at_depth(depth.to(UREG.meter).magnitude)

    def ceiling(self):
        pressure_bar = self.model.ceiling_in_pabs()
        pressure = pressure_bar * UREG.bar
        return depth_from_pressure(pressure, self.water)