pub use uom::si::f64::{Acceleration, MassDensity as Density, Pressure, Length as Depth};
use uom::si::acceleration::meter_per_second_squared;
use uom::si::mass_density::kilogram_per_cubic_meter;
use uom::si::pressure::atmosphere;

pub fn m_per_s2(value: f64) -> Acceleration {
    Acceleration::new::<meter_per_second_squared>(value)
}

pub fn kg_per_m3(value: f64) -> Density {
    Density::new::<kilogram_per_cubic_meter>(value)
}

pub fn atm(value: f64) -> Pressure {
    Pressure::new::<atmosphere>(value)
}