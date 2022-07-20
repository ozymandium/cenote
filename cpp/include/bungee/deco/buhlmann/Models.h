#pragma once

#include "Compartment.h"
#include <bungee/custom_units.h>

#include <map>
#include <vector>

namespace bungee::deco::buhlmann {

enum class Model {
    /// Original 16 compartment model from 1990 with 4 minute fastest compartment (1)
    ZHL_16A,
};

using CompartmentList = std::vector<Time>;
using CompartmentListLookup = std::map<Model, const CompartmentList*>;

extern const CompartmentList ZHL_16A_COMPARTMENT_LIST;
extern const CompartmentListLookup COMPARTMENT_LIST_LOOKUP;

const CompartmentList* GetCompartmentList(Model model);

} // namespace bungee::deco::buhlmann