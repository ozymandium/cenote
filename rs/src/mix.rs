use crate::units::{Pressure, Depth};
use crate::water::Water;
use crate::constants::SURFACE_PRESSURE;
use lazy_static::lazy_static;

pub struct PartialPressure {
    /// The partial pressure of oxygen in the mix
    pub o2: Pressure,
    /// The partial pressure of nitrogen in the mix
    pub n2: Pressure,
}

/// A gas mixture. The sum of fo2 and fn2 must be 1.0. Helium is not currently supported.
pub struct Mix {
    /// The fraction of oxygen in the mix (0.0 - 1.0)
    pub fo2: f64,
    /// The fraction of nitrogen in the mix (0.0 - 1.0)
    pub fn2: f64,
}

impl Mix {
    pub fn new(fo2: f64) -> Result<Self, &'static str> {
        // o2 must be 0. < fo2 <= 1.0
        if fo2 <= 0.0 || 1.0 < fo2 {
            return Err("Mix::new: fo2 must be 0. < fo2 <= 1.0")
        }
        Ok(Mix { fo2, fn2: 1.0 - fo2 })
    }

    pub fn pp(&self, depth: Depth, water: Water) -> PartialPressure {
        let abs_pressure = water.abs_pressure_at_depth(depth);
        PartialPressure {
            o2: self.fo2 * abs_pressure,
            n2: self.fn2 * abs_pressure,
        }
    }
}

lazy_static! {
    pub static ref AIR: Mix = Mix::new(0.20946).expect("Failed to create AIR Mix");
    pub static ref SURFACE_AIR_PP: PartialPressure = PartialPressure {
        o2: (*SURFACE_PRESSURE) * (*AIR).fo2,
        n2: (*SURFACE_PRESSURE) * (*AIR).fn2,
    };
}

#[test]
fn test_mix() {
    use crate::assert_approx_val;
    use crate::units::{atm, meter};

    let mix = Mix::new(0.1).unwrap();
    let depth = meter(30.3);
    let water = Water::Salt;
    let pp = mix.pp(depth, water);
    assert_approx_val!(pp.o2, atm(0.4), atm(2e-3));
    assert_approx_val!(pp.n2, atm(3.6), atm(2e-3));
}