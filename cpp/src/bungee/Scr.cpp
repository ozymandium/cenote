#include <bungee/Scr.h>
#include <bungee/Constants.h>

namespace bungee {

VolumeRate
ScrFromSac(const PressureRate sac, const Tank& tank)
{
    return sac * (tank.serviceVolume() / tank.servicePressure());
}

PressureRate
SacFromScr(const VolumeRate scr, const Tank& tank)
{
    return scr * (tank.servicePressure() / tank.serviceVolume());
}

VolumeRate ScrAtDepth(VolumeRate scr,
                                                  Depth depth, Water water)
{
    const auto pressure = PressureFromDepth(depth, water);
    const Scalar scaling = pressure / SURFACE_PRESSURE;
    return scr * scaling();
}

} // namespace bungee
