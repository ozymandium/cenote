#pragma once

#include <bungee/custom_units.h>

#include <optional>

namespace bungee::deco::buhlmann {

/// Tracks loading of a single inert gas (N2, He, etc) in a single tissue compartment.
///
/// This class is not aware of anything related to diving, it is purely a pressure tracker.
///
/// A note on units: Buhlmann's algorithm uses minutes for time units and bar for pressure. All time
/// constants are given in minutes in the literature and the exponential decay equations assume the
/// same. As such, bar and minutes are used here. Everywhere else in the code we typedef units so
/// that they can be changed over in the future. However, since the equations have to be in bar
/// and minutes, the typedefs are not used. In the event that the rest of the modules are switched
/// to, e.g., psi and seconds, this code will have to stay in bar and minutes.
class Compartment {
public:
    struct Params {
        /// \brief Parameters a and b are computed as a function of the time constant in minutes, so
        /// the time constant is the only argument needed.
        ///
        /// \param[in] t Half time of the gas for the given tissue compartment [min].
        ///
        /// \param[in] lo Gradient factor low, 0.0 - 1.0
        ///
        /// \param[in] hi Gradient factor high, 0.0 - 1.0
        ///
        /// \return All necessary parameters for the tissue compartment.
        Params(units::time::minute_t t);

        /// Half life
        units::time::minute_t halfLife;
        /// Coefficient `a` is the y-intercept of the M-value line
        units::pressure::bar_t a;
        /// Coefficient `b` is the reciprocal of the slope of the M-value line
        Scalar b;
    };

    /// \brief Construct compartment with params already set.
    ///
    /// \param[in] params Parameters to use.
    Compartment(const Params& params);

    /// \brief Initialize or reset the compartment pressure.
    ///
    /// \param[in] pressure Partial pressure of the gas in the compartment[bar].
    void set(units::pressure::bar_t pressure);

    Pressure pressure() const { return _pressure.value(); }

    /// \brief Update the pressure in the compartment by exposing it to a certain inert gas partial
    /// pressure for a period of time.
    ///
    /// \param[in] ambientPressure The absolute partial pressure of the inert gas within the lungs,
    /// or the "inspired" pressure [bar].
    ///
    /// \param[in] duration The amount of time for which the compartment was exposed to pressure
    /// `ambientPressure` [min].
    void constantPressureUpdate(units::pressure::bar_t ambientPressure,
                                units::time::minute_t duration);

    /// Assume ambient pressure changes linearly from start to end.
    void variablePressureUpdate(units::pressure::bar_t ambientPressureStart,
                                units::pressure::bar_t ambientPressureEnd,
                                units::time::minute_t duration);

    /// \brief The lowest tolerable pressure.
    ///
    /// TODO: optimize by computing this once in `update()`
    ///
    /// \return Minimum ambient gas pressure to which this compartment should be exposed based on
    /// the current internal gas pressure [bar].
    units::pressure::bar_t M0() const;

    /// Get the gradient factor if the compartment were instantaneously placed into an environment
    /// with the given ambient absolute pressure. A return value of 1.0 means the compartment would
    /// be at its M value. A return value of 0 means that the compartment would be at equilibrium
    /// with the environment.
    Scalar gradientAtAmbientPressure(units::pressure::bar_t ambientPressure) const;

private:
    /// Constant coefficients
    const Params _params;

    /// The absolute pressure of the inert gas [bar]. Set to nullopt on construction, and
    /// initialized by `init()`. Calling any other function before initializing this will result in
    /// an error.
    std::optional<units::pressure::bar_t> _pressure;
};

} // namespace bungee::deco::buhlmann
