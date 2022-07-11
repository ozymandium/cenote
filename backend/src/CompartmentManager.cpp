#include <bungee/CompartmentManager.h>

#include <cassert>

namespace bungee {

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

void CompartmentManager::update(const Mix::PartialPressure& partialPressure,
                                const units::time::minute_t time)
{
    for (auto& compartment : _compartments) {
        compartment.update(partialPressure.N2, time);
    }
}

units::pressure::bar_t CompartmentManager::ceiling() const
{
    auto maxCeiling = _compartments[0].ceiling();
    for (auto& compartment : _compartments) {
        const auto thisCeiling = compartment.ceiling();
        if (thisCeiling > maxCeiling) {
            maxCeiling = thisCeiling;
        }
    }
    return maxCeiling;
}

} // namespace bungee