#pragma once

#include "Compartment.h"
#include "Mix.h"
#include "Models.h"

namespace bungee {

class CompartmentManager {
public:
    CompartmentManager(Model model);

    /// \brief Initialize the compartments to a state where they are at equilibrium with the ambient
    /// environment.
    ///
    /// TODO: add a version to initialize to a specific compartment state, e.g., for repetitive
    /// dives.
    void equilibrium(const Mix::PartialPressure& partialPressure);

    void update(const Mix::PartialPressure& partialPressure, const Time duration);

    Pressure ceiling() const;

private:
    /// Nitrogen compartments.
    ///
    /// TODO: make a nested array for each type of gas once helium is supported.
    std::vector<Compartment> _compartments;
};

} // namespace bungee