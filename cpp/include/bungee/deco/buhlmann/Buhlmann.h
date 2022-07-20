#pragma once

#include "CompartmentManager.h"
#include "Models.h"
#include <bungee/Water.h>

namespace bungee::deco::buhlmann {

class Buhlmann {
public:
    Buhlmann(Model model, double gf_low, double gf_high);

    /// \brief Initialize compartment to equilibrium with the surface
    void init();

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, Time duration);

    Depth ceiling(Water water) const;

private:
    CompartmentManager _compartments;
};

} // namespace bungee::deco::buhlmann
