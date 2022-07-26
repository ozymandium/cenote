#include <bungee/Constants.h>
#include <bungee/deco/buhlmann/Compartment.h>
#include <bungee/ensure.h>
#include <bungee/utils.h>

#include <fmt/format.h>

#include <cmath>

namespace bungee::deco::buhlmann {

Compartment::Params::Params(const units::time::minute_t t)
{
    halfLife = t;
    a = units::pressure::bar_t(2. / std::cbrt(t()));
    b = 1.005 - 1.0 / std::sqrt(t());
}

Compartment::Compartment(const Params& params) : _params(params) {}

void Compartment::set(const units::pressure::bar_t pressure) { _pressure = pressure; }

void Compartment::constantPressureUpdate(const units::pressure::bar_t ambientPressure,
                                         const units::time::minute_t duration)
{
    ensure(_pressure.has_value(), "Compartment::update: pressure not initialized.");
    const units::pressure::bar_t pressureDiff =
        ambientPressure - WATER_VAPOR_PRESSURE - _pressure.value();
    const Scalar timeRatio = duration / _params.halfLife;
    _pressure.value() += pressureDiff * (1 - std::pow(2, -timeRatio()));
}

void Compartment::variablePressureUpdate(units::pressure::bar_t ambientPressureStart,
                                         units::pressure::bar_t ambientPressureEnd,
                                         units::time::minute_t duration)
{
    const size_t N = GetNumPoints(duration);
    const Eigen::VectorXd timeVec = Eigen::VectorXd::LinSpaced(N, 0, duration());
    const double ambientPressureSlope = (ambientPressureEnd - ambientPressureStart)() / duration();
    const Eigen::VectorXd ambientPressureVec =
        ambientPressureSlope * timeVec.array() + ambientPressureStart();
    for (size_t i = 1; i < N; ++i) {
        const units::time::minute_t thisDuration(timeVec[i] - timeVec[i - 1]);
        const units::pressure::bar_t ambientPressureAvg(
            (ambientPressureVec[i] + ambientPressureVec[i - 1]) * 0.5);
        constantPressureUpdate(ambientPressureAvg, thisDuration);
    }
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
    ensure(_pressure.has_value(), "Compartment::M0: pressure not initialized.");
    return (_pressure.value() - _params.a) * _params.b;
}

Scalar Compartment::gradientAtAmbientPressure(units::pressure::bar_t ambientPressure) const
{
    ensure(_pressure.has_value(), "Compartment::gf: pressure not initialized.");
    // http://scubatechphilippines.com/scuba_blog/gradient-factors-dummies/
    return (_pressure.value() - ambientPressure) / (_pressure.value() - M0());
}

} // namespace bungee::deco::buhlmann
