#include <bungee/Tank.h>

namespace {

// keep stuff in this namespace from leaking out to the rest of the module
using namespace units::literals;

constexpr units::volume::liter_t VolumeAtPressure(const units::volume::liter_t emptyVolume,
                                        const units::pressure::bar_t pressure, 
                                        const units::dimensionless::dimensionless_t z) {
    return emptyVolume * (pressure / 1_atm) / z;
}

}

namespace bungee {

Tank::Tank(units::pressure::bar_t pressure) : _pressure(pressure) {}

units::volume::liter_t Tank::serviceVolume() const {
    return VolumeAtPressure(emptyVolume(), servicePressure(), zFactor());
}

units::volume::liter_t Tank::volume() const {
    return VolumeAtPressure(emptyVolume(), pressure(), zFactor());
}

void Tank::decreasePressure(units::pressure::bar_t diff) { pressureChange(-diff); }

void Tank::decreaseVolume(units::volume::liter_t diff) { volumeChange(-diff); }

void Tank::pressureChange(units::pressure::bar_t diff) { _pressure += diff; }

void Tank::volumeChange(units::volume::liter_t diff) {
    // FIXME
    pressureChange(diff / serviceVolume() * units::pressure::atmosphere_t(1.0));
}

// Tank GetTank(TankE type) {
//     switch(type) {
//         case TankE::AL80:
//             return 
//     }
// }

} // namespace bungee