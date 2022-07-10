#include <bungee/Models.h>

namespace bungee {

extern const ModelParams ZHL_16A_MODEL_PARAMS{
    // clang-format off
    Compartment::Params::Create(4),
    Compartment::Params::Create(8),
    Compartment::Params::Create(12.5),
    Compartment::Params::Create(18.5),
    Compartment::Params::Create(27),
    Compartment::Params::Create(38.3),
    Compartment::Params::Create(54.3),
    Compartment::Params::Create(77),
    Compartment::Params::Create(109),
    Compartment::Params::Create(146),
    Compartment::Params::Create(187),
    Compartment::Params::Create(239),
    Compartment::Params::Create(305),
    Compartment::Params::Create(390),
    Compartment::Params::Create(498),
    Compartment::Params::Create(635),
    // clang-format on
};

extern const ModelParamsLookup MODEL_PARAMS_LOOKUP{
    {Model::ZHL_16A, &ZHL_16A_MODEL_PARAMS},
};

const ModelParams *GetModelParams(const Model model) { return MODEL_PARAMS_LOOKUP.at(model); }

} // namespace bungee