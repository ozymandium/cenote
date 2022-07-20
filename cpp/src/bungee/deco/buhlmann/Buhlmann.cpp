#include <bungee/Constants.h>
#include <bungee/Mix.h>
#include <bungee/deco/buhlmann/Buhlmann.h>
#include <bungee/ensure.h>

namespace bungee::deco::buhlmann {

Buhlmann::Buhlmann(const Model model, const double gf_low, const double gf_high)
{
    const CompartmentList* compartmentList = GetCompartmentList(model);
    _compartments.reserve(compartmentList->size());
    for (const units::time::minute_t halfLife : *compartmentList) {
        _compartments.emplace_back(Compartment::Params(halfLife, gf_low, gf_high));
    }
    ensure(_compartments.size() == compartmentList->size(), "mismatch");
}

void Buhlmann::equilibrium(const Mix::PartialPressure& partialPressure)
{
    for (auto& compartment : _compartments) {
        compartment.set(partialPressure.N2);
    }
}

void Buhlmann::update(const Mix::PartialPressure& partialPressure, Time duration)
{
    for (auto& compartment : _compartments) {
        compartment.update(partialPressure.N2, duration);
    }
}

Depth Buhlmann::ceiling(const Water water) const
{
    Pressure maxM0(0);
    for (auto& compartment : _compartments) {
        const auto thisCeiling = compartment.M0();
        if (thisCeiling > maxM0) {
            maxM0 = thisCeiling;
        }
    }
    return DepthFromPressure(maxM0, water);
}

} // namespace bungee::deco::buhlmann
