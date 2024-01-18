use crate::mix::Mix;
use crate::tank::TankKind;
use crate::units::{Bar, Pressure};

pub struct TankConfig {
    /// The kind of tank
    pub kind: TankKind,
    /// The pressure of the gas in the tank relative to ambient pressure.
    pub pressure: Pressure,
    /// What gas is in the tank
    pub mix: Mix,
}

impl TankConfig {
    pub fn new(kind: TankKind, pressure: Pressure, mix: Mix) -> Result<Self, &'static str> {
        if pressure.get::<Bar>() <= 0.0 {
            return Err("tank_config::TankConfig::new: pressure must be > 0.0");
        }
        Ok(TankConfig {
            kind,
            pressure,
            mix,
        })
    }
}
