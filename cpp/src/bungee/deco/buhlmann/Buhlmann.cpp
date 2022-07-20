#include <bungee/Constants.h>
#include <bungee/Mix.h>
#include <bungee/deco/buhlmann/Buhlmann.h>

namespace bungee::deco::buhlmann {

Buhlmann::Buhlmann(const Model model, const double gf_low, const double gf_high)
    : _compartments(model, gf_low, gf_high)
{
}

void Buhlmann::init() { _compartments.equilibrium(SURFACE_AIR_PP); }

void Buhlmann::update(const Mix::PartialPressure& partialPressure, Time duration)
{
    _compartments.update(partialPressure, duration);
}

Depth Buhlmann::ceiling(const Water water) const
{
    return DepthFromPressure(_compartments.M0(), water);
}

} // namespace bungee::deco::buhlmann
