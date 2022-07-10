#include <bungee/Water.h>
#include <bungee/Constants.h>

namespace {

/// bar = BAR_FROM_PA * pa
static constexpr double BAR_FROM_PA = 1e-5;
static constexpr double PA_FROM_BAR = 1e5;

}

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

double WaterPressureFromDepth(double depth, Water water) {
    // density in kg/m^3
    const double density = GetWaterDensity(water);
    // pressure from water in Pascal. 1 Pa = 1 kg/(m*s^2)
    const double pressurePa = density * GRAVITY_MS2 * depth;
    // convert Pa to bar
    return BAR_FROM_PA * pressurePa;
}

double DepthFromWaterPressure(double pressure, Water water) {
    // density in kg/m^3
    const double density = GetWaterDensity(water);
    // pressure in Pa
    const double pressurePa = PA_FROM_BAR * pressure;
    // depth in m
    const double depth = pressurePa / (density * GRAVITY_MS2);
    return depth;
}

double PressureFromDepth(double depth, Water water) {
    return WaterPressureFromDepth(depth, water) + SURFACE_PRESSURE_BAR;
}

double DepthFromPressure(double pressure, Water water) {
    return DepthFromWaterPressure(pressure - SURFACE_PRESSURE_BAR, water);
}

}