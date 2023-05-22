#pragma once

#include "custom_units.h"

#include <map>

namespace bungee {

enum class Water { FRESH, SALT, COUNT };

/// \brief Look up the density of water.
///
/// \param[in] water Type of water.
///
/// \return Water density in kg/m^3
Density GetWaterDensity(Water water);

/// \param[in] depth Depth under the surface [m].
///
/// \param[in] water Type of water.
///
/// \return Relative pressure resulting from water, excluding ambient surface pressure [bar].
Pressure WaterPressureFromDepth(Depth depth, Water water);

/// \param[in] pressure Relative pressure resulting from water, excluding ambient surface pressure
/// [bar].
///
/// \param[in] water Type of water.
///
/// \return Depth under the surface [m].
Depth DepthFromWaterPressure(Pressure pressure, Water water);

/// \param[in] depth Depth under the surface [m].
///
/// \param[in] water Type of water.
///
/// \return Absolute pressure including ambient surface pressure [bar].
Pressure PressureFromDepth(Depth depth, Water water);

/// \param[in] pressure Absolute pressure including ambient surface pressure [bar].
///
/// \param[in] water Type of water.
///
/// \return Depth under the surface [m].
Depth DepthFromPressure(Pressure pressure, Water water);

} // namespace bungee