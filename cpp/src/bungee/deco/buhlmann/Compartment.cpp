#include <bungee/Constants.h>
#include <bungee/deco/buhlmann/Compartment.h>
#include <bungee/ensure.h>

#include <fmt/format.h>

#include <cmath>

namespace bungee::deco::buhlmann {

Compartment::Params::Params(const units::time::minute_t t, const double lo, const double hi)
{
    // ensure(low <= high, "gf low larger than gf high");
    ensure(0 < lo, "gf low must be >0");
    ensure(lo <= 1, "gf low must be at most 100%");
    ensure(0 < hi, "gf high must be >0");
    ensure(hi <= 1, "gf high must be at most 100%");

    halfLife = t;
    a = units::pressure::bar_t(2. / std::cbrt(t()));
    b = 1.005 - 1.0 / std::sqrt(t());
    gf_low = lo;
    gf_high = hi;

    fmt::print("{:5.1f} min: a = {:06.4f}, b = {:06.4f}\n", halfLife(), a(), b());
}

Compartment::Compartment(const Params& params) : _params(params) {}

void Compartment::set(const units::pressure::bar_t pressure) { _pressure = pressure; }

void Compartment::update(const units::pressure::bar_t ambientPressure,
                         const units::time::minute_t duration)
{
    ensure(_pressure.has_value(), "Compartment::update: pressure not initialized.");
    const units::pressure::bar_t pressureDiff =
        ambientPressure - WATER_VAPOR_PRESSURE - _pressure.value();
    const Scalar timeRatio = duration / _params.halfLife;
    _pressure.value() += pressureDiff * (1 - std::pow(2, -timeRatio()));
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

Scalar Compartment::gf(units::pressure::bar_t ambientPressure) const
{
    ensure(_pressure.has_value(), "Compartment::gf: pressure not initialized.");
    // http://scubatechphilippines.com/scuba_blog/gradient-factors-dummies/
    return (_pressure.value() - ambientPressure) / (M0() - ambientPressure);
}

} // namespace bungee::deco::buhlmann
