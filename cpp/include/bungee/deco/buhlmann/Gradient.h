#pragma once

#include <bungee/Water.h>
#include <bungee/custom_units.h>
#include <optional>

namespace bungee::deco::buhlmann {

class Gradient {
public:
    Gradient(double low, double high);

    double low() const { return _low; }
    double high() const { return _high; }

    // void ascendFrom(Pressure ambientPressure);

    // Scalar at(Pressure ambientPressure) const;

private:
    const Scalar _low;
    const Scalar _high;

    // std::optional<Depth> _ascentStart;
    std::optional<Scalar> _slope;
};

} // namespace bungee::deco::buhlmann