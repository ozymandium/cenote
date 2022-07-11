#include <bungee/Tank.h>

using namespace units::literals;

units::volume::liter_t Tank::VolumeAtPressure(const Params& params,
                                              const units::pressure::bar_t pressure) {
    return params.size * pressure / (params.z * 1_atm);
}

units::volume::bar_t Tank::PressureAtVolume(const Params& params,
                                            const units::volume::liter_t volume) {
    return volume * params.z * 1_atm / params.size;
}

namespace bungee {

Tank::Tank(units::pressure::bar_t pressure) : _params(params) { setPressure(pressure); }

Tank::Tank(units::volume::liter_t volume) : _params(params) { setVolume(volume); }

units::volume::liter_t Tank::serviceVolume() const {
    return VolumeAtPressure(size(), servicePressure(), zFactor());
}

void Tank::decreasePressure(units::pressure::bar_t diff) { setPressure(_pressure - diff); }

void Tank::decreaseVolume(units::volume::liter_t diff) { setVolume(_volume - diff); }

void setPressure(units::pressure::bar_t pressure) {
    _pressure = pressure;
    _volume = VolumeAtPressure()
}

void setVolume(units::volume::liter_t volume) {}

// Tank GetTank(TankE type) {
//     switch(type) {
//         case TankE::AL80:
//             return
//     }
// }

} // namespace bungee