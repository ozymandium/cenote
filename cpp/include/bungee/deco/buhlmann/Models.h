#pragma once

#include "Compartment.h"

#include <map>
#include <vector>

namespace bungee::deco::buhlmann {

enum class Model {
    /// Original 16 compartment model from 1990 with 4 minute fastest compartment (1)
    ZHL_16A,
    /// Original 16 compartment model from 1990 with 5 minute fastest compartment (1b)
    ZHL_16A_1b
};

using ModelParams = std::vector<Compartment::Params>;

extern const ModelParams ZHL_16A_MODEL_PARAMS;
extern const ModelParams ZHL_16A_1b_MODEL_PARAMS;

using ModelParamsLookup = std::map<Model, const ModelParams *>;

extern const ModelParamsLookup MODEL_PARAMS_LOOKUP;

const ModelParams *GetModelParams(Model model);

} // namespace bungee