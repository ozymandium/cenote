#include <bungee/Tank.h>

#include <map>

using namespace units::literals;

namespace bungee {

Tank::Tank(const Params& params, Pressure pressure) : _params(params) { setPressure(pressure); }

Tank::Tank(const Params& params, Volume volume) : _params(params) { setVolume(volume); }

Volume Tank::VolumeAtPressure(const Params& params, const Pressure pressure)
{
    return params.size * pressure / (params.z * 1_atm);
}

Pressure Tank::PressureAtVolume(const Params& params, const Volume volume)
{
    return volume * params.z * 1_atm / params.size;
}

void Tank::setPressure(Pressure pressure)
{
    _pressure = pressure;
    _volume = VolumeAtPressure(_params, pressure);
}

void Tank::setVolume(Volume volume)
{
    _volume = volume;
    _pressure = PressureAtVolume(_params, volume);
}

Volume Tank::serviceVolume() const { return VolumeAtPressure(_params, _params.servicePressure); }

// void Tank::decreasePressure(Pressure diff) { setPressure(_pressure - diff); }

void Tank::decreaseVolume(Volume diff) { setVolume(_volume - diff); }

static const std::map<Tank::Type, Tank::Params> TANK_PARAMS{
    {Tank::AL40, {.size = 5.8_L, .servicePressure = 3000_psi, .z = 1.045}},
    {Tank::AL80, {.size = 11.1_L, .servicePressure = 3000_psi, .z = 1.0337}},
    {Tank::LP108, {.size = 17_L, .servicePressure = 2640_psi, .z = 1.0}},
};

/*
 * Tank generators for each type
 */

Tank GetEmptyTank(const Tank::Type type) { return Tank(TANK_PARAMS.at(type), 0_bar); }

Tank GetFullTank(const Tank::Type type)
{
    const auto& params = TANK_PARAMS.at(type);
    return Tank(params, params.servicePressure);
}

Tank GetTankAtPressure(const Tank::Type type, const Pressure pressure)
{
    return Tank(TANK_PARAMS.at(type), pressure);
}

Tank GetTankAtVolume(const Tank::Type type, const Volume volume)
{
    return Tank(TANK_PARAMS.at(type), volume);
}

} // namespace bungee