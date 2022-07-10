#include <bungee/Compartment.h>

#include <cmath>

namespace {

// skip optimizing since this only gets called in startup
double CalcCoefficientA(double t) {
    return 2. / std::cbrt(t);
}

// skip optimizing since this only gets called in startup
double CalcCoefficientB(double t) {
    return 1.005 - 1.0 / std::sqrt(t);
}

}

namespace bungee {

Compartment::Params Compartment::Params::Create(const double t)
{
    return Params{.t=t, .a=CalcCoefficientA(t), .b=CalcCoefficientB(t)};
}

Compartment::Compartment(const Params& params) : _params(params) {}

} // namespace bungee
