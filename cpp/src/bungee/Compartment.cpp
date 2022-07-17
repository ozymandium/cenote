#include <bungee/Compartment.h>
#include <bungee/Constants.h>

#include <cassert>
#include <cmath>

namespace bungee {

Compartment::Params Compartment::Params::Create(const Time t)
{
    return Params{.halfLife = t,
                  .a = Pressure(2. / std::cbrt(t.value())),
                  .b = 1.005 - 1.0 / std::sqrt(t.value())};
}

Compartment::Compartment(const Params& params) : _params(params) {}

void Compartment::set(const Pressure pressure) { _pressure = pressure; }

void Compartment::update(const Pressure ambientPressure, const Time time)
{
    assert(_pressure.has_value());
    const Pressure pressureDiff = ambientPressure - WATER_VAPOR_PRESSURE - _pressure.value();
    const Scalar timeRatio = time / _params.halfLife;
    _pressure.value() += pressureDiff * (1 - std::pow(2, -timeRatio.value()));
}

Pressure Compartment::ceiling() const
{
    assert(_pressure.has_value());
    return (_pressure.value() - _params.a) * _params.b;
}

} // namespace bungee
