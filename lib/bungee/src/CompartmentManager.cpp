#include <bungee/CompartmentManager.h>

namespace bungee {

CompartmentManager::CompartmentManager(const Model model) {
    const ModelParams *modelParams = GetModelParams(model);
    for (const auto& compartmentParams : *modelParams) {
        _compartments.push_back(Compartment(compartmentParams));
    }
}

void CompartmentManager::init() {
    for (auto& compartment : _compartments) {
        compartment.init()
    }
}

} // namespace bungee