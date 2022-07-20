#include <bungee/Constants.h>
#include <bungee/deco/buhlmann/Compartment.h>
#include <bungee/ensure.h>

#include <cassert>
#include <cmath>

namespace bungee::deco::buhlmann {

Compartment::Params Compartment::Params::Create(const Time t)
{
    return Params{.halfLife = t,
                  .a = units::pressure::bar_t(2. / std::cbrt(t.value())),
                  .b = 1.005 - 1.0 / std::sqrt(t.value())};
}

Compartment::Compartment(const Params& params) : _params(params) {}

void Compartment::set(const units::pressure::bar_t pressure) { _pressure = pressure; }

void Compartment::update(const units::pressure::bar_t ambientPressure, const Time duration)
{
    ensure(_pressure.has_value(), "Compartment::update: pressure not initialized.");
    const units::pressure::bar_t pressureDiff =
        ambientPressure - WATER_VAPOR_PRESSURE - _pressure.value();
    const Scalar timeRatio = duration / _params.halfLife;
    _pressure.value() += pressureDiff * (1 - std::pow(2, -timeRatio.value()));
}

units::pressure::bar_t Compartment::M0() const
{
    /*
    M value plot has ambient pressure on x axis and compartment pressure on y axis
    M value forms a line with slope and y intercept forms the tolerable compartment pressure at the
    surface.

    Ptol = (Pcmp - a) * b

    Ptol = 1/b * Pcmp - a/b

    slope: 1/b
    y-intercept: a/b

    */
    ensure(_pressure.has_value(), "Compartment::update: pressure not initialized.");
    return (_pressure.value() - _params.a) * _params.b;
}

} // namespace bungee::deco::buhlmann
