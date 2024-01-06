use crate::units::{Acceleration, Density, Pressure};
use dimensioned::si::{ATM, KG, M, M3, S2};
use lazy_static::lazy_static;

// constants are not necessarily defined using the units in which they are stored, so evaluate them at runtime
lazy_static! {
    /// # Fresh water density
    /// water density varies with temperature, being more dense at lower temperatures. pure
    /// water at 0C is 1000 kg/m3. pick a value of pure water at 25C, since contaminnts
    /// generally decrease the density, and this will offset changes due to colder water.
    /// https://en.wikipedia.org/wiki/Properties_of_water
    pub static ref FRESH_WATER_DENSITY: Density = 997.0474 * KG / M3;

    /// # Salt water density
    /// Deep salt water has higher density (1050 kg/m3) than surface water, which varies from
    /// 1020-1029 kg/m3. Pick a median value of surface seawater at 25C.
    /// https://en.wikipedia.org/wiki/Seawater
    pub static ref SALT_WATER_DENSITY: Density = 1023.6 * KG / M3;

    /// Magnitude of gravitational force in m/s^2 take a value close to the mean
    /// https://en.wikipedia.org/wiki/Gravity_of_Earth
    ///
    /// TODO: Allow varying this based on latitude
    pub static ref GRAVITY: Acceleration = 9.80665 * M / S2;

    /// Atmospheric pressure at sea level is 1 atm.
    pub static ref SURFACE_PRESSURE: Pressure = 1.0 * ATM;
}
