#include <bungee/Scr.h>

namespace bungee {

// units::volume_rate::liters_per_minute
// ScrFromSac(const Tank& tank, const units::pressure_rate::pounds_per_square_inch_per_minute sac)
// {
//     return sac * (tank.serviceVolume() / tank.servicePressure());
// }

// units::pressure_rate::pounds_per_square_inch_per_minute
// SacFromScr(const Tank& tank, const units::volume_rate::liters_per_minute scr)
// {
//     return scr * (tank.servicePressure() / tank.serviceVolume());
// }

units::volume_rate::liters_per_minute ScrAtDepth(units::volume_rate::liters_per_minute scr,
                                                 units::length::meter_t depth, Water water)
{
    const units::pressure::atmosphere_t atm = PressureFromDepth(depth, water);
    return scr * atm.value();
}

} // namespace bungee
