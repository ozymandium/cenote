#pragma once

#include "CompartmentManager.h"

namespace bungee {

class Buhlmann {
public:
    Buhlmann(Model model);

private:
    CompartmentManager _compartments;
};

} // namespace bungee
