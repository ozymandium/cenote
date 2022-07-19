#pragma once

#include "CompartmentManager.h"
#include "Water.h"

namespace bungee {

class Buhlmann {
public:
    Buhlmann(Model model);

    /// \brief Initialize compartment to equilibrium with the surface
    void init();

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, Time duration);

    Pressure ceiling() const;
    Depth ceiling(Water water) const;

private:
    CompartmentManager _compartments;
};

} // namespace bungee
