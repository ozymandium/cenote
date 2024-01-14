use crate::constants::SURFACE_PRESSURE;
use crate::units::{Depth, Pressure};
use crate::water::Water;
use lazy_static::lazy_static;

#[derive(Clone)]
pub struct PartialPressure {
    /// The partial pressure of oxygen in the mix
    pub o2: Pressure,
    /// The partial pressure of nitrogen in the mix
    pub n2: Pressure,
}

/// A gas mixture. The sum of fo2 and fn2 must be 1.0. Helium is not currently supported.
#[derive(Debug, Clone)]
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
            return Err("Mix::new: fo2 must be 0. < fo2 <= 1.0");
        }
        Ok(Mix {
            fo2,
            fn2: 1.0 - fo2,
        })
    }
}

/// The current state of the diver's breathing gas
pub struct Breath {
    /// The absolute ambient pressure
    pub ambient_pressure: Pressure,
    /// The current breathing gas mixture
    pub mix: Mix,
    /// The partial pressure of the breathing gas
    pub partial_pressure: PartialPressure,
}

impl Breath {
    /// Create a new Breath
    ///
    /// # Arguments
    /// * `ambient_pressure` - The absolute ambient pressure
    /// * `mix` - The current breathing gas mixture
    fn new(ambient_pressure: &Pressure, mix: &Mix) -> Self {
        Breath {
            /// FIXME: should we clone the ambient pressure?
            ambient_pressure: *ambient_pressure,
            /// FIXME: does this have to be cloned?
            mix: (*mix).clone(),
            partial_pressure: PartialPressure {
                o2: mix.fo2 * (*ambient_pressure),
                n2: mix.fn2 * (*ambient_pressure),
            },
        }
    }
}

lazy_static! {
    pub static ref AIR: Mix = Mix::new(0.20946).expect("Failed to create AIR Mix");
    pub static ref SURFACE_AIR: Breath = Breath::new(&SURFACE_PRESSURE, &AIR);
}

#[test]
fn test_mix() {
    assert_eq!(
        Mix::new(1.001).unwrap_err(),
        "Mix::new: fo2 must be 0. < fo2 <= 1.0"
    );
    assert_eq!(
        Mix::new(0.0).unwrap_err(),
        "Mix::new: fo2 must be 0. < fo2 <= 1.0"
    );
}

#[test]
fn test_breath() {
    use crate::units::atm;
    let mix = Mix::new(0.5).expect("Failed to create Mix");
    let ambient_pressure = atm(1.0);
    let breath = Breath::new(&ambient_pressure, &mix);
    assert_eq!(breath.partial_pressure.o2, atm(0.5));
    assert_eq!(breath.partial_pressure.n2, atm(0.5));
    assert_eq!(breath.mix.fo2, 0.5);
    assert_eq!(breath.mix.fn2, 0.5);
    assert_eq!(breath.ambient_pressure, atm(1.0));
}
