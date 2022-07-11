#pragma once

#include <units.h>

#include <memory>

namespace bungee {

class Tank {
public:

    Tank(units::pressure::bar_t pressure);

    // overridden
    virtual units::volume::liter_t emptyVolume() const = 0;
    // overridden
    virtual units::pressure::bar_t servicePressure() const = 0;
    // overridden
    virtual units::dimensionless::dimensionless_t zFactor() const = 0;

    // function of overridden functions
    units::volume::liter_t serviceVolume() const;

    // getters
    units::pressure::bar_t pressure() const { return _pressure; }

    /// TODO: make this part of internal state instead of calculating every time?
    units::volume::liter_t volume() const;

    void decreasePressure(units::pressure::bar_t diff);
    void decreaseVolume(units::volume::liter_t diff);

private:
    void pressureChange(units::pressure::bar_t diff);
    void volumeChange(units::volume::liter_t diff);

    units::pressure::bar_t _pressure;
};

template <units::volume::liter_t VOLUME, 
          units::pressure::bar_t SERVICE_PRESSURE,
          units::dimensionless::dimensionless_t Z_FACTOR>
class TankImpl : public Tank {
public:
    virtual units::volume::liter_t emptyVolume() const override { return VOLUME; }
    virtual units::pressure::bar_t servicePressure() const override { return SERVICE_PRESSURE; }
    virtual units::dimensionless::dimensionless_t zFactor() const override { return Z_FACTOR; }

    static std::shared_ptr<Tank> CreateFull() {
        return std::make_shared<Tank>(SERVICE_PRESSURE);
    }

};

using Aluminum80 = TankImpl<units::volume::liter_t(11.1), 
                            units::pressure::bar_t(206.8),
                            units::dimensionless::dimensionless_t(1.0337)>;

// enum class TankE { AL80, COUNT };

// Tank GetTank(TankE type);

} // namespace bungee
