#pragma once

#include "Compartment.h"
#include "Models.h"
#include <bungee/Water.h>

namespace bungee::deco::buhlmann {

class Buhlmann {
public:
    Buhlmann(Model model, double gf_low, double gf_high);

    /// \brief Initialize compartment to equilibrium with a given mixture + pressure.
    /// This is most often used to initialize compartments to an effective infinite surface interval.
    void equilibrium(const Mix::PartialPressure& partialPressure);

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, Time duration);

    Depth ceiling(Water water) const;

private:
    /// Nitrogen compartments.
    ///
    /// TODO: make a nested array for each type of gas once helium is supported.
    std::vector<Compartment> _compartments;
};

} // namespace bungee::deco::buhlmann
