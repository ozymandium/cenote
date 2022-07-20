#include <bungee/deco/buhlmann/Models.h>

using namespace units::literals;

namespace bungee::deco::buhlmann {

// https://www.shearwater.com/wp-content/uploads/2019/05/understanding_m-values.pdf

extern const CompartmentList ZHL_16A_COMPARTMENT_LIST{
    // Compartment 1 is subdivided into 1a and 1b. 1a is 4 min, 1b is 5 min.
    // some sources indicate it's an either/or thing, it adds conservatism to simply use both
    // together.
    // Subsurface uses a 5 minute fastest compartment instead of a 4 minute fastest compartment.
    4.0_min,
    5.0_min,
    8.0_min,
    12.5_min,
    18.5_min,
    27.0_min,
    38.3_min,
    54.3_min,
    77.0_min,
    109.0_min,
    146.0_min,
    187.0_min,
    239.0_min,
    305.0_min,
    390.0_min,
    498.0_min,
    635.0_min,
};

extern const CompartmentListLookup COMPARTMENT_LIST_LOOKUP{
    {Model::ZHL_16A, &ZHL_16A_COMPARTMENT_LIST},
};

const CompartmentList* GetCompartmentList(const Model model)
{
    return COMPARTMENT_LIST_LOOKUP.at(model);
}

} // namespace bungee::deco::buhlmann