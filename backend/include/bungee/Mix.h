#pragma once

#include "Water.h"

namespace bungee {

class Mix {
public:
    /// Partial pressures of each gas in the mix for a given ambient pressure
    struct PartialPressure {
        /// Partial pressure of oxygen [bar]
        units::pressure::bar_t O2;
        /// Partial pressure of nitrogen [bar]
        units::pressure::bar_t N2;
    };

    explicit Mix(double fO2);

    /// \brief Partial pressures of each gas in the mix for a given depth
    ///
    /// \param[in] depth Depth under the surface [m].
    ///
    /// \param[in] water Type of water.
    ///
    /// \return Partial pressures of each gas
    PartialPressure partialPressure(units::length::meter_t depth, Water water) const;

    /// Fraction of oxygen, 0.0 - 1.0 [unitless]
    const double fO2;
    /// Fraction of nitrogen, 0.0 - 1.0 [unitless]
    const double fN2;
};

/// Atmospheric Air
extern const Mix AIR;
/// Partial pressures of air at the surface
extern const Mix::PartialPressure SURFACE_AIR_PP;

} // namespace bungee