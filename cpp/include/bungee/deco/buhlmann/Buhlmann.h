#pragma once

#include "Compartment.h"
#include "Models.h"
#include <bungee/Mix.h>
#include <bungee/Water.h>

namespace bungee::deco::buhlmann {

class Buhlmann {
public:
    struct Params {
        Water water;
        Model model;
    };
    Buhlmann(const Params& params);

    size_t compartmentCount() const { return _compartments.size(); }

    /// \brief Initialize compartment to equilibrium with a given mixture + pressure.
    /// This is most often used to initialize compartments to an effective infinite surface
    /// interval.
    void equilibrium(const Mix::PartialPressure& partialPressure);

    void setCompartmentPressures(const std::vector<Pressure> compartmentPressures);

    /// TODO: temperature consideration
    void constantPressureUpdate(const Mix::PartialPressure& partialPressure, Time duration);
    void variablePressureUpdate(const Mix::PartialPressure& partialPressureStart,
                                const Mix::PartialPressure& partialPressureEnd, Time duration);

    /// \param[in] gf Gradient factor, [0.0, 1.0]. Pass 1 to get the depth at the M value. Pass 0
    /// to get the current pressure. But don't do either of those things because there's more
    /// efficient ways.
    Depth ceiling(double gf) const;
    std::vector<Depth> ceilings(double gf) const;

    std::vector<Pressure> M0s() const;
    Pressure M0() const;

    std::vector<Pressure> pressures() const;

    /// Get the gradient factor if the diver were instantaneously placed into an environment
    /// with the given ambient absolute pressure. A return value of 1.0 means the controlling
    /// compartment would be at its M value. A return value of 0 means that all compartments would
    /// be on-gassing or at equilibrium. while on-gassing, GF's may reach very large negative
    /// values, so 0 is the lowest return value.
    Scalar gradientAtDepth(Depth depth) const;
    std::vector<Scalar> gradientsAtDepth(Depth depth) const;

private:
    const Params _params;

    /// Nitrogen compartments.
    ///
    /// TODO: make a nested array for each type of gas once helium is supported.
    std::vector<Compartment> _compartments;
};

} // namespace bungee::deco::buhlmann
