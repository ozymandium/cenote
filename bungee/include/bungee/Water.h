#pragma once

#include <map>

namespace bungee {

enum class Water {
    FRESH,
    SALT,
    COUNT
};

using WaterDensityLookup = std::map<Water, double>;

/// Density of water in kg/m^3
extern const WaterDensityLookup WATER_DENSITY_KGM3;

/// \brief Look up the density of water.
///
/// \param[in] water Type of water.
///
/// \return Water density in kg/m^3
double GetWaterDensity(Water water);

/// \param[in] depth Depth under the surface [m].
///
/// \param[in] water Type of water.
///
/// \return Relative pressure resulting from water, excluding ambient surface pressure [bar].
double WaterPressureFromDepth(double depth, Water water);

/// \param[in] pressure Relative pressure resulting from water, excluding ambient surface pressure [bar].
///
/// \param[in] water Type of water.
///
/// \return Depth under the surface [m].
double DepthFromWaterPressure(double pressure, Water water);

/// \param[in] depth Depth under the surface [m].
///
/// \param[in] water Type of water.
///
/// \return Absolute pressure including ambient surface pressure [bar].
double PressureFromDepth(double depth, Water water);

/// \param[in] pressure Absolute pressure including ambient surface pressure [bar].
///
/// \param[in] water Type of water.
///
/// \return Depth under the surface [m].
double DepthFromPressure(double pressure, Water water);

}