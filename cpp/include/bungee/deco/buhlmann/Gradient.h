#pragma once

#include <bungee/custom_units.h>
#include <optional>

namespace bungee::deco::buhlmann {

class Gradient {
public:
    Gradient(double low, double high);

    void ascendFrom(Depth depth);

    double at(Depth depth) const;

private:
    const double _low;
    const double _high;

    // std::optional<Depth> _ascentStart;
    std::optional<double> _slope;
};

} // namespace bungee::deco::buhlmann