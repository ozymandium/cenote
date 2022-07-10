#pragma once

#include "Water.h"

namespace bungee {

class Mix {
public:
    // struct PartialPressure {
    //     double O2;
    //     double N2;
    // };

    explicit Mix(double pO2);

    // PartialPressure atDepth(double depth, Water water);

    /// Fraction of oxygen, 0.0 - 1.0 [unitless]
    const double fO2;
    /// Fraction of nitrogen, 0.0 - 1.0 [unitless]
    const double fN2;
};

} // namespace bungee