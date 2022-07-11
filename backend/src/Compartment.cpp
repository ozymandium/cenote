#include <bungee/Compartment.h>
#include <bungee/Constants.h>

#include <cassert>
#include <cmath>

namespace bungee {

Compartment::Params Compartment::Params::Create(const units::time::minute_t t) {
    return Params{.halfLife = t,
                  .a = units::pressure::bar_t(2. / std::cbrt(t.value())),
                  .b = 1.005 - 1.0 / std::sqrt(t.value())};
}

Compartment::Compartment(const Params& params) : _params(params) {}

void Compartment::init(const units::pressure::bar_t P) { _pressure = P; }

void Compartment::update(const units::pressure::bar_t ambientPressure,
                         const units::time::minute_t time) {
    assert(_pressure.has_value());
    const units::pressure::bar_t pressureDiff =
        ambientPressure - WATER_VAPOR_PRESSURE - _pressure.value();
    const units::dimensionless::dimensionless_t timeRatio = time / _params.halfLife;
    _pressure.value() += pressureDiff * (1 - std::pow(2, -timeRatio.value()));
}

units::pressure::bar_t Compartment::ceiling() const {
    assert(_pressure.has_value());
    return (_pressure.value() - _params.a) * _params.b;
}

} // namespace bungee
