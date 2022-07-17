#include <bungee/Models.h>

using namespace units::literals;

namespace bungee {

extern const ModelParams ZHL_16A_MODEL_PARAMS{
    // clang-format off
    Compartment::Params::Create(4.0_min),
    Compartment::Params::Create(8.0_min),
    Compartment::Params::Create(12.5_min),
    Compartment::Params::Create(18.5_min),
    Compartment::Params::Create(27.0_min),
    Compartment::Params::Create(38.3_min),
    Compartment::Params::Create(54.3_min),
    Compartment::Params::Create(77.0_min),
    Compartment::Params::Create(109.0_min),
    Compartment::Params::Create(146.0_min),
    Compartment::Params::Create(187.0_min),
    Compartment::Params::Create(239.0_min),
    Compartment::Params::Create(305.0_min),
    Compartment::Params::Create(390.0_min),
    Compartment::Params::Create(498.0_min),
    Compartment::Params::Create(635.0_min),
    // clang-format on
};

extern const ModelParamsLookup MODEL_PARAMS_LOOKUP{
    {Model::ZHL_16A, &ZHL_16A_MODEL_PARAMS},
};

const ModelParams *GetModelParams(const Model model) { return MODEL_PARAMS_LOOKUP.at(model); }

} // namespace bungee