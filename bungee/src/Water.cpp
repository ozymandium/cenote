#include <bungee/Water.h>


namespace bungee {

/// https://bluerobotics.com/learn/pressure-depth-calculator/#hydrostatic-water-pressure-formula
const WaterDensityLookup WATER_DENSITY_KGM3{
    /// water density varies with temperature, being more dense at lower temperatures.
    /// pure water at 0C is 1000 kg/m3.
    /// pick a value of pure water at 25C, since contaminnts generally decrease the density, and this
    /// will offset changes due to colder water.
    /// https://en.wikipedia.org/wiki/Properties_of_water
    {Water::FRESH, 997.0474},
    /// Deep salt water has higher density (1050 kg/m3) than surface water, which varies from
    /// 1020-1029 kg/m3. Pick a median value of surface seawater at 25C.
    /// https://en.wikipedia.org/wiki/Seawater
    {Water::SALT, 1023.6},
};

double GetWaterDensity(const Water water) {
    return WATER_DENSITY_KGM3.at(water);
}

}