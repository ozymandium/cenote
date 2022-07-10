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

}