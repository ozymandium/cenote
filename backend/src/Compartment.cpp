#include <bungee/Compartment.h>

#include <cassert>
#include <cmath>

namespace {

// skip optimizing since this only gets called in startup
double CalcCoefficientA(double t) { return 2. / std::cbrt(t); }

// skip optimizing since this only gets called in startup
double CalcCoefficientB(double t) { return 1.005 - 1.0 / std::sqrt(t); }

} // namespace

namespace bungee {

Compartment::Params Compartment::Params::Create(const units::time::minute_t t) {
    return Params{
        .t = t.value(), .a = CalcCoefficientA(t.value()), .b = CalcCoefficientB(t.value())};
}

Compartment::Compartment(const Params& params) : _params(params) {}

Compartment::Compartment(const units::time::minute_t t) : _params(Params::Create(t)) {}

void Compartment::init(const units::pressure::bar_t P) { _pressure = P.value(); }

void Compartment::update(const units::pressure::bar_t ambientPressure,
                         const units::time::minute_t time) {
    assert(_pressure.has_value());
    const double dP = ambientPressure.value() - _pressure.value();
    _pressure.value() += dP * (1 - std::pow(2, -time.value() / _params.t));
}

units::pressure::bar_t Compartment::ceiling() const {
    assert(_pressure.has_value());
    return units::pressure::bar_t((_pressure.value() - _params.a) * _params.b);
}

} // namespace bungee
