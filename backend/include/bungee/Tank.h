#pragma once

#include <units.h>

#include <memory>

namespace bungee {

class Tank {
public:
    struct Params {
        /// volume of the physical interior of the tank, the storage capacity of gas at 1 atm
        units::volume::liter_t size;
        units::pressure::bar_t servicePressure;
        units::dimensionless::dimensionless_t z;
    };

    Tank(const Params& params, units::pressure::bar_t pressure);
    Tank(const Params& params, units::volume::liter_t volume);

    static units::volume::liter_t VolumeAtPressure(const Params& params,
                                                   units::pressure::bar_t pressure);

    static units::pressure::bar_t PressureAtVolume(const Params& params,
                                                   units::volume::liter_t volume);

    units::volume::liter_t serviceVolume() const;

    // getters
    units::pressure::bar_t pressure() const { return _pressure; }
    units::volume::liter_t volume() const { return _volume; }

    void decreasePressure(units::pressure::bar_t diff);
    void decreaseVolume(units::volume::liter_t diff);

private:
    // setters
    void setPressure(units::pressure::bar_t pressure);
    void setVolume(units::volume::liter_t volume);

    const Params _params;
    units::pressure::bar_t _pressure;
    units::volume::liter_t _volume;
};

// using Aluminum80 = TankImpl<units::volume::liter_t(11.1),
//                             units::pressure::bar_t(206.8),
//                             units::dimensionless::dimensionless_t(1.0337)>;

enum class TankE {
    // aluminum 40 cuft
    AL40,
    // aluminum 80 cuft / 11.1 L
    AL80,
    // Faber low pressure 108 cuft / 17 L
    LP108
        // // Double / sidemounted LP108
        // DLP108,
        COUNT
};

// Tank GetTank(TankE type);

} // namespace bungee
