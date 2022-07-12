#pragma once

#include "CompartmentManager.h"

namespace bungee {

class Buhlmann {
public:
    Buhlmann(Model model);

    /// \brief Initialize compartment to equilibrium with the surface
    void init();

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, units::time::minute_t time);

    units::pressure::bar_t ceiling() const;

private:
    CompartmentManager _compartments;
};

} // namespace bungee
