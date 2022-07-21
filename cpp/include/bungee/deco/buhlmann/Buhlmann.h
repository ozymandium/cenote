#pragma once

#include "Compartment.h"
#include "Models.h"
#include <bungee/Water.h>

namespace bungee::deco::buhlmann {

class Buhlmann {
public:
    Buhlmann(Water water, Model model, double gf_low, double gf_high);

    /// \brief Initialize compartment to equilibrium with a given mixture + pressure.
    /// This is most often used to initialize compartments to an effective infinite surface
    /// interval.
    void equilibrium(const Mix::PartialPressure& partialPressure);

    /// TODO: temperature consideration
    void update(const Mix::PartialPressure& partialPressure, Time duration);

    Depth ceiling() const;

    /// Get the gradient factor if the diver were instantaneously placed into an environment
    /// with the given ambient absolute pressure. A return value of 1.0 means the controlling
    /// compartment would be at its M value. A return value of 0 means that all compartments would
    /// be on-gassing or at equilibrium. while on-gassing, GF's may reach very large negative
    /// values, so 0 is the lowest return value.
    Scalar gf(Depth depth) const;

private:
    /// Get the highest M value, i.e., the M value for the controlling compartment.
    Pressure maxM0() const;

    const Water _water;

    /// Nitrogen compartments.
    ///
    /// TODO: make a nested array for each type of gas once helium is supported.
    std::vector<Compartment> _compartments;
};

} // namespace bungee::deco::buhlmann