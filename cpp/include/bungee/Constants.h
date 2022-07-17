#pragma once

#include "custom_units.h"

namespace bungee {

/// \brief Water vapor pressure in the lungs
/// [bar].
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
static constexpr Pressure WATER_VAPOR_PRESSURE = units::pressure::bar_t(0.0627);

/// \brief Atmospheric pressure at sea level, equivalent to 1 atm [bar].
///
/// TODO: Allow varying this, compute based on altitude and temperature.
/// TODO: define in atmospheres.
static constexpr Pressure SURFACE_PRESSURE = units::pressure::bar_t(1.01325);

/// Magnitude of gravitational force in m/s^2 take a value close to the mean
/// https://en.wikipedia.org/wiki/Gravity_of_Earth
///
/// TODO: Allow varying this based on latitude
static const Acceleration GRAVITY = units::acceleration::meters_per_second_squared_t (9.80665);

} // namespace bungee