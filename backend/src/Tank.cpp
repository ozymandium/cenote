#include <bungee/Tank.h>

#include <map>

using namespace units::literals;

namespace bungee {

Tank::Tank(const Params& params) : _params(params) {}

Tank::Tank(const Params& params, units::pressure::bar_t pressure) : _params(params)
{
    setPressure(pressure);
}

Tank::Tank(const Params& params, units::volume::liter_t volume) : _params(params)
{
    setVolume(volume);
}

units::volume::liter_t Tank::VolumeAtPressure(const Params& params,
                                              const units::pressure::bar_t pressure)
{
    return params.size * pressure / (params.z * 1_atm);
}

units::pressure::bar_t Tank::PressureAtVolume(const Params& params,
                                            const units::volume::liter_t volume)
{
    return volume * params.z * 1_atm / params.size;
}

void Tank::setPressure(units::pressure::bar_t pressure)
{
    _pressure = pressure;
    _volume = VolumeAtPressure(_params, pressure);
}

void Tank::setVolume(units::volume::liter_t volume)
{
    _volume = volume;
    _pressure = PressureAtVolume(_params, volume);
}

// units::volume::liter_t Tank::serviceVolume() const
// {
//     return VolumeAtPressure(_params, _params.servicePressure);
// }

// void Tank::decreasePressure(units::pressure::bar_t diff) { setPressure(_pressure - diff); }

// void Tank::decreaseVolume(units::volume::liter_t diff) { setVolume(_volume - diff); }

static const std::map<Tank::Type, Tank::Params> TANK_PARAMS{
    {Tank::AL40, {.size = 5.8_L, .servicePressure = 3000_psi, .z = 1.045}},
    {Tank::AL80, {.size = 11.1_L, .servicePressure = 3000_psi, .z = 1.0337}},
    {Tank::LP108, {.size = 17_L, .servicePressure = 2640_psi}},
};

// Tank generators for each type

Tank GetTank(const Tank::Type type) { return Tank(TANK_PARAMS.at(type)); }

Tank GetTank(const Tank::Type type, const units::pressure::bar_t pressure)
{
    return Tank(TANK_PARAMS.at(type), pressure);
}

Tank GetTank(const Tank::Type type, const units::volume::liter_t volume)
{
    return Tank(TANK_PARAMS.at(type), volume);
}

} // namespace bungee