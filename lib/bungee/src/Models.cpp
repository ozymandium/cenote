#include <bungee/Models.h>

namespace bungee {

extern const ModelParams ZHL_16A_MODEL_PARAMS{
    // clang-format off
    Compartment::Params{.t=4,    .a=1.2599, .b=0.5050},
    Compartment::Params{.t=8,    .a=1.0000, .b=0.6514},
    Compartment::Params{.t=12.5, .a=0.8618, .b=0.7222},
    Compartment::Params{.t=18.5, .a=0.7562, .b=0.7725},
    Compartment::Params{.t=27,   .a=0.6667, .b=0.8125},
    Compartment::Params{.t=38.3, .a=0.5933, .b=0.8434},
    Compartment::Params{.t=54.3, .a=0.5282, .b=0.8693},
    Compartment::Params{.t=77,   .a=0.4701, .b=0.8910},
    Compartment::Params{.t=109,  .a=0.4187, .b=0.9092},
    Compartment::Params{.t=146,  .a=0.3798, .b=0.9222},
    Compartment::Params{.t=187,  .a=0.3497, .b=0.9319},
    Compartment::Params{.t=239,  .a=0.3223, .b=0.9403},
    Compartment::Params{.t=305,  .a=0.2971, .b=0.9477},
    Compartment::Params{.t=390,  .a=0.2737, .b=0.9544},
    Compartment::Params{.t=498,  .a=0.2523, .b=0.9602},
    Compartment::Params{.t=635,  .a=0.2327, .b=0.9653},
    // clang-format on
};

extern const ModelParamsLookup MODEL_PARAMS_LOOKUP{
    {Model::ZHL_16A, ZHL_16A_MODEL_PARAMS},
};

const ModelParams& GetModelParams(const Model model) { return MODEL_PARAMS_LOOKUP.at(model); }

} // namespace bungee