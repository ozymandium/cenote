#include <bungee/CompartmentManager.h>

namespace bungee {

CompartmentManager::CompartmentManager(const Model model) {
    const ModelParams *modelParams = GetModelParams(model);
    for (auto compartmentParams : *modelParams) {
        _compartments.push_back(Compartment(compartmentParams));
    }
}

} // namespace bungee