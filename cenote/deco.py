from cenote import config
from cenote.water import Water, pressure_from_depth, depth_from_pressure
from cenote.mix import Mix

from decotengu.model import ZH_L16C_GF
from decotengu.engine import GasMix


UREG = config.UREG


class BuhlmannParams:
    def __init__(self, gf_low, gf_high):
        self.gf_low = gf_low
        self.gf_high = gf_high


class DecoModelBase:
    pass


class DecotenguModel(DecoModelBase):

    def __init__(self, params:BuhlmannParams, water: Water):
        self.water = water

        self.model = ZH_L16C_GF()

        # set gradient factors
        self.model.gf_low = params.gf_low
        self.model.gf_high = params.gf_high

        # initialize with surface atmospheric pressure
        self.data = self.model.init((1.0 * UREG.atm).to(UREG.bar).magnitude)

    def log(self, pt0, pt1, mix: Mix):
       
        # time is time spent at depth
        d_time = (pt1.time - pt0.time).to(UREG.minute)
        
        gas = GasMix(
            # switch depth [m]?
            # it appears this is when the gas is started during the decompression stage. not sure.
            # putting mod here but it is probably wrong. doesn't seem to be used.
            depth=mix.mod(1.4, self.water).to(UREG.meter).magnitude, 
            o2=mix.po2 * 100, 
            n2=mix.pn2 * 100, 
            he=0)

        pressure_pt0 = pressure_from_depth(pt0.depth, self.water).to(UREG.bar)
        pressure_pt1 = pressure_from_depth(pt1.depth, self.water).to(UREG.bar)
        d_pressure = pressure_pt1 - pressure_pt0
        pressure_rate = d_pressure / d_time

        avg_pressure = (pressure_pt0 + pressure_pt1) * 0.5

        self.data = self.model.load(
            abs_p=avg_pressure.to(UREG.bar).magnitude, 
            time=d_time.to(UREG.minute).magnitude, 
            gas=gas,
            rate=pressure_rate.to(UREG.bar / UREG.minute).magnitude,
            data=self.data)

    def ceiling(self):
        # need to figure out when to use gf high here.
        pressure_bar = self.model.ceiling_limit(self.data)
        pressure = pressure_bar * UREG.bar
        return depth_from_pressure(pressure, self.water)

    # def compartment_ceilings(self):
