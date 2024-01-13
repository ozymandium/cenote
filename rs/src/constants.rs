use crate::units::{atm, bar, m_per_s2, Acceleration, Pressure};
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

    /// Water vapor pressure in the lungs
    ///
    /// This is the Buhlmann value used by Subsurface, which also uses the Schreiner value of 0.0493 for
    /// the VPMB model. See the equations and explanation in deco.c for more information. It indicates
    /// that a "respiratory quotient" is sometimes used to compute alveolar pressure.
    ///
    /// Dipplanner uses a temperature dependent calculation (via `calculate_pp_h2o_surf`) that results
    /// in a value of 0.0626 at the human body temperature (37 C), and 0.0233 at 20C as a default. For
    /// the deco model, dipplanner stores the water vapor partial pressure using the surface
    /// temperature.
    ///
    /// TODO: Treat this as a variable, and figure out
    /// how to compute it.
    pub static ref WATER_VAPOR_PRESSURE: Pressure = bar(0.0627);
}
