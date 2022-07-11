#pragma once

#include <units.h>

#include <map>

namespace bungee {

enum class Water { FRESH, SALT, COUNT };

using WaterDensityLookup = std::map<Water, units::density::kilograms_per_cubic_meter_t>;

/// Density of water in kg/m^3
extern const WaterDensityLookup WATER_DENSITY;

/// \brief Look up the density of water.
///
/// \param[in] water Type of water.
///
/// \return Water density in kg/m^3
units::density::kilograms_per_cubic_meter_t GetWaterDensity(Water water);

/// \param[in] depth Depth under the surface [m].
///
/// \param[in] water Type of water.
///
/// \return Relative pressure resulting from
/// water, excluding ambient surface pressure
/// [bar].
units::pressure::bar_t WaterPressureFromDepth(units::length::meter_t depth, Water water);

/// \param[in] pressure Relative pressure
/// resulting from water, excluding ambient
/// surface pressure [bar].
///
/// \param[in] water Type of water.
///
/// \return Depth under the surface [m].
units::length::meter_t DepthFromWaterPressure(units::pressure::bar_t pressure, Water water);

/// \param[in] depth Depth under the surface [m].
///
/// \param[in] water Type of water.
///
/// \return Absolute pressure including ambient
/// surface pressure [bar].
units::pressure::bar_t PressureFromDepth(units::length::meter_t depth, Water water);

/// \param[in] pressure Absolute pressure
/// including ambient surface pressure [bar].
///
/// \param[in] water Type of water.
///
/// \return Depth under the surface [m].
units::length::meter_t DepthFromPressure(units::pressure::bar_t pressure, Water water);

} // namespace bungee