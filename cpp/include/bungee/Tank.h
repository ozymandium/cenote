#pragma once

#include "custom_units.h"

#include <memory>

namespace bungee {

class Tank {
public:
    /// Implemented types of cylinders
    enum Type {
        // aluminum 40 cuft
        AL40,
        // aluminum 80 cuft / 11.1 L
        AL80,
        // Faber low pressure 108 cuft / 17 L
        LP108,
        // Double / sidemounted LP108
        D_LP108,
        COUNT,
    };

    /// Specs of the cylinder that describe capacity and max pressure. Volume is determined
    /// as a dependent variable, rather than volume being used as an independent spec.
    struct Params {
        /// volume of the physical interior of the tank, the storage capacity of gas at 1 atm
        Volume size;
        Pressure servicePressure;
        Scalar z;
    };

    Tank() = delete;

    /// \brief Create tank with specific pressure.
    Tank(const Params& params, Pressure pressure);

    /// \brief Create tank with specified gas volume.
    Tank(const Params& params, Volume volume);

    /// \brief compute gas volume for a given pressure
    static Volume VolumeAtPressure(const Params& params, Pressure pressure);

    /// \brief compute gas pressure for a given volume
    static Pressure PressureAtVolume(const Params& params, Volume volume);

    Pressure servicePressure() const { return _params.servicePressure; }
    Volume serviceVolume() const;

    // getters
    Pressure pressure() const { return _pressure; }
    Volume volume() const { return _volume; }

    // setters
    void setPressure(Pressure pressure);
    void setVolume(Volume volume);

    // void decreasePressure(Pressure diff);
    void decreaseVolume(Volume diff);

private:
    const Params _params;

    /// The pressure of gas in the tank relative to surface pressure (1 atm).
    ///
    /// FIXME: this does not account for ambient pressure at depth, but rather always considers
    /// the tank to be at the surface.
    Pressure _pressure;

    /// Volume of gas in the tank which corresponds to relative pressures above 1 atm at the
    /// surface. This does not include the gas at 1 atm which remains in the tank when the pressure
    /// relative to surface conditions is zero.
    Volume _volume;
};

Tank GetEmptyTank(Tank::Type type);
Tank GetFullTank(Tank::Type type);
Tank GetTankAtPressure(Tank::Type type, Pressure pressure);
Tank GetTankAtVolume(Tank::Type type, Volume volume);

} // namespace bungee
