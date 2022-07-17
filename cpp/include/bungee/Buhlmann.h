#pragma once

#include "CompartmentManager.h"

namespace bungee {

class Buhlmann {
public:
    Buhlmann(Model model);

    /// \brief Initialize compartment to equilibrium with the surface
    void init();

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, Time time);

    Pressure ceiling() const;

private:
    CompartmentManager _compartments;
};

} // namespace bungee
