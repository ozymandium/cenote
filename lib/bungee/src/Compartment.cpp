#include <bungee/Compartment.h>
#include <bungee/Constants.h>

#include <cmath>

namespace {

// skip optimizing since this only gets called in startup
double CalcCoefficientA(double t) { return 2. / std::cbrt(t); }

// skip optimizing since this only gets called in startup
double CalcCoefficientB(double t) { return 1.005 - 1.0 / std::sqrt(t); }

} // namespace

namespace bungee {

Compartment::Params Compartment::Params::Create(const double t) {
    return Params{.t = t, .a = CalcCoefficientA(t), .b = CalcCoefficientB(t)};
}

Compartment::Compartment(const Params& params) : _params(params) {}

Compartment::Compartment(const double t) : _params(Params::Create(t)) {}

void Compartment::init(const double P) { _P = P; }

void Compartment::update(const double Pgas, const double dt) {
    assert(_P.has_value()); 
    const double dP = Pgas - _P.value();
    _P.value() += dP * (1 - std::pow(2, -dt/_params.t));
}

double Compartment::ceiling() const {
    assert(_P.has_value());
    return (_P.value() - _params.a) * _params.b;
}

} // namespace bungee
