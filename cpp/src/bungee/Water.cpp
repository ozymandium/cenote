#include <bungee/Constants.h>
#include <bungee/Water.h>

#include <stdexcept>

using namespace units::literals;

namespace bungee {

Density GetWaterDensity(const Water water)
{
    /// https://bluerobotics.com/learn/pressure-depth-calculator/#hydrostatic-water-pressure-formula
    switch (water) {
    case Water::FRESH:
        /// water density varies with temperature, being more dense at lower temperatures. pure
        /// water at 0C is 1000 kg/m3. pick a value of pure water at 25C, since contaminnts
        /// generally decrease the density, and this will offset changes due to colder water.
        /// https://en.wikipedia.org/wiki/Properties_of_water
        return 997.0474_kg_per_cu_m;
    case Water::SALT:
        /// Deep salt water has higher density (1050 kg/m3) than surface water, which varies from
        /// 1020-1029 kg/m3. Pick a median value of surface seawater at 25C.
        /// https://en.wikipedia.org/wiki/Seawater
        return 1023.6_kg_per_cu_m;
    default:
        throw std::invalid_argument("unimplemented water type");
    };
}

Pressure WaterPressureFromDepth(Depth depth, Water water)
{
    // density in kg/m^3
    const Density density = GetWaterDensity(water);
    // pressure from water in Pascal. 1 Pa = 1 kg/(m*s^2)
    const auto pressure = density * GRAVITY * depth;
    // convert Pa to bar
    return pressure;
}

Depth DepthFromWaterPressure(Pressure pressure, Water water)
{
    // density in kg/m^3
    const Density density = GetWaterDensity(water);
    // depth in m
    const Depth depth = pressure / (density * GRAVITY);
    return depth;
}

Pressure PressureFromDepth(Depth depth, Water water)
{
    return WaterPressureFromDepth(depth, water) + SURFACE_PRESSURE;
}

Depth DepthFromPressure(Pressure pressure, Water water)
{
    return DepthFromWaterPressure(pressure - SURFACE_PRESSURE, water);
}

} // namespace bungee