#pragma once

#include "Water.h"

namespace bungee {

class Mix {
public:
    /// Partial pressures of each gas in the mix for a given ambient pressure
    struct PartialPressure {
        /// Partial pressure of oxygen [bar]
        Pressure O2;
        /// Partial pressure of nitrogen [bar]
        Pressure N2;
    };

    /// Do not use explicit here as it prevents pybind from wrapping the ctor.
    Mix(double fO2);

    // /// Must define the copy assignment operator for pybind to work
    // Mix& operator=(const Mix& other);

    double fO2() const { return _fO2; }
    double fN2() const { return _fN2; }

    /// \brief Partial pressures of each gas in the mix for a given depth
    ///
    /// \param[in] depth Depth under the surface [m].
    ///
    /// \param[in] water Type of water.
    ///
    /// \return Partial pressures of each gas
    PartialPressure partialPressure(Depth depth, Water water) const;

private:
    void set(double fO2);

    /// Fraction of oxygen, 0.0 - 1.0 [unitless]
    ///
    /// Left non-const for mixing and fill calculations later on.
    double _fO2;
    /// Fraction of nitrogen, 0.0 - 1.0 [unitless]
    ///
    /// Left non-const for mixing and fill calculations later on.
    double _fN2;
};

/// Atmospheric Air
extern const Mix AIR;
/// Partial pressures of air at the surface
extern const Mix::PartialPressure SURFACE_AIR_PP;

} // namespace bungee