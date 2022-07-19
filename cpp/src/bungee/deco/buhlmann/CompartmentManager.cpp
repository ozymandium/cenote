#include <bungee/deco/buhlmann/CompartmentManager.h>

#include <cassert>

namespace bungee::deco::buhlmann {

CompartmentManager::CompartmentManager(const Model model)
{
    const ModelParams *modelParams = GetModelParams(model);
    _compartments.reserve(modelParams->size());
    for (const auto& compartmentParams : *modelParams) {
        _compartments.push_back(Compartment(compartmentParams));
    }
    assert(_compartments.size() == modelParams->size());
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

} // namespace bungee