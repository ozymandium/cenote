#pragma once

#include <units.h>

namespace bungee {

constexpr units::volume::liter_t VolumeAtPressure(const units::volume::liter_t volume,
                                        const units::pressure::bar_t pressure, 
                                        const units::dimensionless::dimensionless_t z) {
    return volume * pressure / units::pressure::atmosphere_t(1.0) / z;
}

template <units::volume::liter_t _VOLUME, 
          units::pressure::bar_t _SERVICE_PRESSURE,
          units::dimensionless::dimensionless_t _Z_FACTOR>
class Tank {
public:
    static constexpr units::volume::liter_t EMPTY_VOLUME = _VOLUME;
    static constexpr units::pressure::bar_t ServicePressure = _SERVICE_PRESSURE;
    static constexpr units::dimensionless::dimensionless_t ZFactor = _Z_FACTOR;

    Tank(units::pressure::bar_t pressure);

    static Tank CreateFull();

    static constexpr units::volume::liter_t SERVICE_VOLUME = ;

    units::pressure::bar_t pressure() const { return _pressure; }
    units::volume::liter_t volume() const;

    void decreasePressure(units::pressure::bar_t diff);
    void decreaseVolume(units::volume::liter_t diff);

private:
    void pressureChange(units::pressure::bar_t diff);
    void volumeChange(units::volume::liter_t diff);

    // const Params _params;

    units::pressure::bar_t _pressure;
};


using Aluminum80 = Tank<units::volume::liter_t(11.1), 
                            units::pressure::bar_t(206.8),
                            units::dimensionless::dimensionless_t(1.0337)>;

// enum class Tank { AL80, COUNT };

} // namespace bungee

#include "Tank.inl"