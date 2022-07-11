#include <bungee/Constants.h>
#include <bungee/Water.h>

namespace bungee {

/// https://bluerobotics.com/learn/pressure-depth-calculator/#hydrostatic-water-pressure-formula
const WaterDensityLookup WATER_DENSITY{
    /// water density varies with temperature, being more dense at lower temperatures. pure water at
    /// 0C is 1000 kg/m3. pick a value of pure water at 25C, since contaminnts generally decrease
    /// the density, and this will offset changes due to colder water.
    /// https://en.wikipedia.org/wiki/Properties_of_water
    {Water::FRESH, units::density::kilograms_per_cubic_meter_t(997.0474)},
    /// Deep salt water has higher density (1050 kg/m3) than surface water, which varies from
    /// 1020-1029 kg/m3. Pick a median value of surface seawater at 25C.
    /// https://en.wikipedia.org/wiki/Seawater
    {Water::SALT, units::density::kilograms_per_cubic_meter_t(1023.6)},
};

units::density::kilograms_per_cubic_meter_t GetWaterDensity(const Water water) {
    return WATER_DENSITY.at(water);
}

units::pressure::bar_t WaterPressureFromDepth(units::length::meter_t depth, Water water) {
    // density in kg/m^3
    const units::density::kilograms_per_cubic_meter_t density = GetWaterDensity(water);
    // pressure from water in Pascal. 1 Pa = 1 kg/(m*s^2)
    const auto pressure = density * GRAVITY * depth;
    // convert Pa to bar
    return pressure;
}

units::length::meter_t DepthFromWaterPressure(units::pressure::bar_t pressure, Water water) {
    // density in kg/m^3
    const units::density::kilograms_per_cubic_meter_t density = GetWaterDensity(water);
    // depth in m
    const units::length::meter_t depth = pressure / (density * GRAVITY);
    return depth;
}

units::pressure::bar_t PressureFromDepth(units::length::meter_t depth, Water water) {
    return WaterPressureFromDepth(depth, water) + SURFACE_PRESSURE;
}

units::length::meter_t DepthFromPressure(units::pressure::bar_t pressure, Water water) {
    return DepthFromWaterPressure(pressure - SURFACE_PRESSURE, water);
}

} // namespace bungee