#pragma once

#include <optional>

namespace bungee {

/// Tracks loading of a single inert gas (N2, He,
/// etc) in a single tissue compartment.
///
/// This class is not aware of anything related to
/// diving, it is purely a pressure tracker.
///
/// A note on units: Buhlmann's algorithm uses
/// minutes for time units and bar for pressure.
/// All time constants are given in minutes in the
/// literature and the exponential decay equations
/// assume the same. As such, bar and minutes are
/// used here.
class Compartment {
public:
    struct Params {
        /// Parameters a and b are computed as a
        /// function of the time constant in
        /// minutes, so the time constant is the
        /// only argument needed. \param[in] t
        /// Half time of the gas for the given
        /// tissue compartment [min]. \return All
        /// necessary parameters for the tissue
        /// compartment.
        static Params Create(double t);

        /// Half time [min]
        double t;
        /// Coefficient `a`
        double a;
        /// Coefficient `b`
        double b;
    };

    /// \brief Construct compartment with params
    /// already set.
    ///
    /// \param[in] params Parameters to use.
    Compartment(const Params& params);

    /// \brief Create compartment for a given half
    /// time
    ///
    /// \param[in] t Half time of the gas for the
    /// given tissue compartment [min].
    Compartment(double t);

    /// \brief Initialize or reset
    /// \param[in] P Partial pressure of the gas
    /// in the compartment[bar].
    void init(double P);

    /// \brief Update the pressure in the
    /// compartment by exposing it to a certain
    /// inert gas partial pressure for a period of
    /// time.
    ///
    /// TODO: account for water vapor pressure
    /// here?
    ///
    /// \param[in] Pgas The absolute partial
    /// pressure of the inert gas within the
    /// lungs, or the "inspired" pressure [bar].
    ///
    /// \param[in] dt The amount of time for which
    /// the compartment was exposed to pressure
    /// `Pgas` [min].
    void update(double Pgas, double dt);

    /// \brief The lowest tolerable pressure.
    ///
    /// \return Minimum ambient gas pressure to
    /// which this compartment should be exposed
    /// based on the current internal gas pressure
    /// [bar].
    double ceiling() const;

private:
    const Params _params;

    /// The absolute pressure of the inert gas
    /// [bar]. Set to nullopt on construction, and
    /// initialized by `init()`. Calling any other
    /// function before initializing this will
    /// result in an error.
    std::optional<double> _P;
};

} // namespace bungee
