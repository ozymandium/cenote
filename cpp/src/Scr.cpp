#include <bungee/Scr.h>

namespace bungee {

units::volume_rate::liter_per_minute_t
ScrFromSac(const units::pressure_rate::pounds_per_square_inch_minute_t sac, const Tank& tank)
{
    return sac * (tank.serviceVolume() / tank.servicePressure());
}

units::pressure_rate::pounds_per_square_inch_minute_t
SacFromScr(const units::volume_rate::liter_per_minute_t scr, const Tank& tank)
{
    return scr * (tank.servicePressure() / tank.serviceVolume());
}

units::volume_rate::liter_per_minute_t ScrAtDepth(units::volume_rate::liter_per_minute_t scr,
                                                  units::length::meter_t depth, Water water)
{
    const units::pressure::atmosphere_t atm = PressureFromDepth(depth, water);
    return scr * atm.value();
}

} // namespace bungee
