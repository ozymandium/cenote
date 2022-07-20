#include <bungee/Constants.h>
#include <bungee/Mix.h>
#include <bungee/deco/buhlmann/Buhlmann.h>
#include <bungee/ensure.h>

namespace bungee::deco::buhlmann {

Buhlmann::Buhlmann(const Water water, const Model model, const double gf_low, const double gf_high)
: _water(water)

{
    const CompartmentList* compartmentList = GetCompartmentList(model);
    _compartments.reserve(compartmentList->size());
    for (const units::time::minute_t halfLife : *compartmentList) {
        _compartments.emplace_back(Compartment::Params(halfLife, gf_low, gf_high));
    }
    ensure(_compartments.size() == compartmentList->size(), "mismatch");
}

void Buhlmann::equilibrium(const Mix::PartialPressure& partialPressure)
{
    for (auto& compartment : _compartments) {
        compartment.set(partialPressure.N2);
    }
}

void Buhlmann::update(const Mix::PartialPressure& partialPressure, Time duration)
{
    for (auto& compartment : _compartments) {
        compartment.update(partialPressure.N2, duration);
    }
}

Depth Buhlmann::ceiling() const {
    return DepthFromPressure(maxM0(), _water);
}

Scalar Buhlmann::gf(const Depth depth) const {
    Scalar maxGf = 0;
    const Pressure ambientPressure = PressureFromDepth(depth, _water);
    for (const auto& compartment : _compartments) {
        const Scalar compartmentGf = compartment.gf(ambientPressure);
        if (compartmentGf > maxGf) {
            maxGf = compartmentGf;
        }
    }
    ensure(maxGf >= 0, "should not have gf return lower than zero");
    return maxGf;
}

Pressure Buhlmann::maxM0() const
{
    Pressure maxM0(0);
    for (const auto& compartment : _compartments) {
        const auto thisCeiling = compartment.M0();
        if (thisCeiling > maxM0) {
            maxM0 = thisCeiling;
        }
    }
}

} // namespace bungee::deco::buhlmann
