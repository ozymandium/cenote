#include <bungee/deco/buhlmann/Models.h>

using namespace units::literals;

namespace bungee::deco::buhlmann {

// https://www.shearwater.com/wp-content/uploads/2019/05/understanding_m-values.pdf

extern const ModelParams ZHL_16A_MODEL_PARAMS{
    // Compartment 1 is subdivided into 1a and 1b. 1a is 4 min, 1b is 5 min.
    // some sources indicate it's an either/or thing, it adds conservatism to simply use both
    // together.
    // Subsurface uses a 5 minute fastest compartment instead of a 4 minute fastest compartment.
    Compartment::Params::Create(4.0_min),
    Compartment::Params::Create(5.0_min),
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
};

extern const ModelParamsLookup MODEL_PARAMS_LOOKUP{
    {Model::ZHL_16A, &ZHL_16A_MODEL_PARAMS},
};

const ModelParams *GetModelParams(const Model model) { return MODEL_PARAMS_LOOKUP.at(model); }

} // namespace bungee::deco::buhlmann