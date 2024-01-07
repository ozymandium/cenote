use crate::units::*;
use lazy_static::lazy_static;

// constants are not necessarily defined using the units in which they are stored, so evaluate them at runtime
lazy_static! {
    /// Magnitude of gravitational force in m/s^2 take a value close to the mean
    /// https://en.wikipedia.org/wiki/Gravity_of_Earth
    ///
    /// TODO: Allow varying this based on latitude
    pub static ref GRAVITY: Acceleration = m_per_s2(9.80665);

    /// Atmospheric pressure at sea level is 1 atm.
    pub static ref SURFACE_PRESSURE: Pressure = atm(1.0);
}
