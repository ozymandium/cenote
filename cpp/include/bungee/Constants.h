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
static constexpr Pressure SURFACE_PRESSURE = units::pressure::atmosphere_t(1);

/// Magnitude of gravitational force in m/s^2 take a value close to the mean
/// https://en.wikipedia.org/wiki/Gravity_of_Earth
///
/// TODO: Allow varying this based on latitude
static const Acceleration GRAVITY = units::acceleration::meters_per_second_squared_t(9.80665);

/// When planning decompression stops, this is the smallest increment that will be used for the
/// output plan. See Planner.cpp.
static constexpr Time STOP_TIME_INC = units::time::minute_t(1);

/// When planning decompression stops, this is the depth between each successive stop. Currently
/// It is also the depth of the last stop, which cannot yet be independently set.
static constexpr Depth STOP_DEPTH_INC = units::length::foot_t(10);

/// When the planner is ascending this is the ascent rate. It is fixed throughout the ascent, though
/// each stop time will be rounded up to the nearest STOP_TIME_INC.
static constexpr auto ASCENT_RATE = units::velocity::feet_per_minute_t(20);

/// When running tissue computations, the model iterates at a smaller increment than the planner.
/// The model currently uses constant average depth instead of integrating over a variable depth, so
/// this value should be as small as possible to maintain accuracy. If the planner is slow, increase
/// this? Must be clean divisor of 60 to get an even number of sampling points each minute.
static constexpr Time MODEL_TIME_INC = units::time::second_t(1);

/// Best mix computations will rule out any gas whose PPO2 is greater than this for a needed stop
/// inside the planner.
static constexpr Pressure MAX_DECO_PPO2 = units::pressure::atmosphere_t(1.6);

} // namespace bungee