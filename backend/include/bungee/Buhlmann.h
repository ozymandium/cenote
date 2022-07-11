#pragma once

#include "CompartmentManager.h"

namespace bungee {

class Buhlmann {
public:
    Buhlmann(Water water, Model model);

    /// \brief Initialize compartment to equilibrium with the surface
    void init();

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, units::time::minute_t time);

    units::length::meter_t ceiling() const;

private:
    const Water _water;
    CompartmentManager _compartments;
};

} // namespace bungee
