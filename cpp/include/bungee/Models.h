#pragma once

#include "Compartment.h"

#include <map>
#include <vector>

namespace bungee {

enum class Model { ZHL_16A };

using ModelParams = std::vector<Compartment::Params>;

extern const ModelParams ZHL_16A_MODEL_PARAMS;

using ModelParamsLookup = std::map<Model, const ModelParams *>;

extern const ModelParamsLookup MODEL_PARAMS_LOOKUP;

const ModelParams *GetModelParams(Model model);

} // namespace bungee