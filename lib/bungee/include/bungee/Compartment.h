#pragma once

namespace bungee {

class Compartment {
public:
    Compartment(double t, double a, double b);

    /// Half time in minutes
    const double t;
    /// Coefficient `a`
    const double a;
    /// Coefficient `b`
    const double b;
};

} // namespace bungee
