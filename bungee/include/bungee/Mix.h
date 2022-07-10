#pragma once

#include "Water.h"

namespace bungee {

class Mix {
public:
    /// Partial pressures of each gas in the mix for a given ambient pressure
    struct PartialPressure {
        /// Partial pressure of oxygen [bar]
        double O2;
        /// Partial pressure of nitrogen [bar]
        double N2;
    };

    explicit Mix(double pO2);

    /// \brief Partial pressures of each gas in the mix for a given depth
    ///
    /// \param[in] depth Depth under the surface [m].
    ///
    /// \param[in] water Type of water.
    /// 
    /// \return Partial pressures of each gas
    PartialPressure partialPresure(double depth, Water water) const;

    /// Fraction of oxygen, 0.0 - 1.0 [unitless]
    const double fO2;
    /// Fraction of nitrogen, 0.0 - 1.0 [unitless]
    const double fN2;
};

} // namespace bungee