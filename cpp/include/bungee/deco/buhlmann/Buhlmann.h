#pragma once

#include "CompartmentManager.h"
#include <bungee/Water.h>
#include "Models.h"

namespace bungee::deco::buhlmann {

class Buhlmann {
public:
    Buhlmann(Model model);

    /// \brief Initialize compartment to equilibrium with the surface
    void init();

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, Time duration);

    Depth ceiling(Water water) const;

private:
    CompartmentManager _compartments;
};

} // namespace bungee
