#include <bungee/deco/buhlmann/CompartmentManager.h>

#include <bungee/ensure.h>

namespace bungee::deco::buhlmann {

CompartmentManager::CompartmentManager(const Model model, const double gf_low, const double gf_high)
{
    const CompartmentList* compartmentList = GetCompartmentList(model);
    _compartments.reserve(compartmentList->size());
    for (const units::time::minute_t halfLife : *compartmentList) {
        _compartments.emplace_back(Compartment::Params(halfLife, gf_low, gf_high));
    }
    ensure(_compartments.size() == compartmentList->size(), "mismatch");
}

void CompartmentManager::equilibrium(const Mix::PartialPressure& partialPressure)
{
    for (auto& compartment : _compartments) {
        compartment.set(partialPressure.N2);
    }
}

void CompartmentManager::update(const Mix::PartialPressure& partialPressure, const Time duration)
{
    for (auto& compartment : _compartments) {
        compartment.update(partialPressure.N2, duration);
    }
}

Pressure CompartmentManager::M0() const
{
    Pressure maxM0(0);
    for (auto& compartment : _compartments) {
        const auto thisCeiling = compartment.M0();
        if (thisCeiling > maxM0) {
            maxM0 = thisCeiling;
        }
    }
    return maxM0;
}

} // namespace bungee::deco::buhlmann