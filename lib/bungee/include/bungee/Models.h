#pragma once

#include "Compartment.h"

#include <map>
#include <vector>

namespace bungee {

enum class Model { ZHL_16A, COUNT };

using ModelParams = std::vector<Compartment::Params>;
using ModelParamsLookup = std::map<Model, ModelParams>;

extern const ModelParams ZHL_16A_MODEL_PARAMS;
extern const ModelParamsLookup MODEL_PARAMS_LOOKUP;

const ModelParams& GetModelParams(Model model);

} // namespace bungee