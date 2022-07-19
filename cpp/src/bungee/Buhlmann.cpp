#include <bungee/Buhlmann.h>
#include <bungee/Constants.h>
#include <bungee/Mix.h>

namespace bungee {

Buhlmann::Buhlmann(const Model model) : _compartments(model) {}

void Buhlmann::init() { _compartments.equilibrium(SURFACE_AIR_PP); }

void Buhlmann::update(const Mix::PartialPressure& partialPressure, Time duration)
{
    _compartments.update(partialPressure, duration);
}

Pressure Buhlmann::ceiling() const { return _compartments.ceiling(); }

Depth Buhlmann::ceiling(const Water water) const { return DepthFromPressure(ceiling(), water); }

} // namespace bungee
