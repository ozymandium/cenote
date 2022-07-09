#pragma once

#include "Compartment.h"
#include "Models.h"

namespace bungee {

class CompartmentManager {
public:
    CompartmentManager(Model model);

private:
    std::vector<Compartment> _compartments;
};

} // namespace bungee