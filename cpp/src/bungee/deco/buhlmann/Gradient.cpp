#include <bungee/deco/buhlmann/Gradient.h>
#include <bungee/ensure.h>

namespace bungee::deco::buhlmann {

Gradient::Gradient(const double low, const double high) : _low(low), _high(high)
{
    ensure(low <= high, "gf low larger than gf high");
    ensure(0.01 <= low, "gf low must be at least 1%");
    ensure(low <= 1.0, "gf low must be at most 100%");
    ensure(0.01 <= high, "gf high must be at least 1%");
    ensure(high <= 1.0, "gf high must be at most 100%");
}

void Gradient::ascendFrom(const Depth depth)
{
    // _ascentStart = depth;
    _slope = (_high - _low) / depth();
}

double Gradient::at(const Depth depth) const
{
    if (_slope.has_value()) {
        return _slope.value() * depth() + _low;
    }
    else {
        return _low;
    }
}

} // namespace bungee::deco::buhlmann
