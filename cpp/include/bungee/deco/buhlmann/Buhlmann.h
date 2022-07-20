#pragma once

#include "CompartmentManager.h"
#include "Gradient.h"
#include "Models.h"
#include <bungee/Water.h>

namespace bungee::deco::buhlmann {

class Buhlmann {
public:
    Buhlmann(Model model, const Gradient& gf);

    /// \brief Initialize compartment to equilibrium with the surface
    void init();

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, Time duration);

    Depth ceiling(Water water) const;

private:
    Gradient _gf;
    CompartmentManager _compartments;
};

} // namespace bungee::deco::buhlmann
