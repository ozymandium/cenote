#include <bungee/Buhlmann.h>
#include <bungee/Constants.h>
#include <bungee/Mix.h>

namespace bungee {

Buhlmann::Buhlmann(const Water water, const Model model) : _water(water), _compartments(model) {}

void Buhlmann::init() {
    const units::length::meter_t depth(0.);
    _compartments.equilibrium(AIR.partialPressure(depth, _water));
}

void Buhlmann::update(const Mix::PartialPressure& partialPressure, units::time::minute_t time) {
    _compartments.update(partialPressure, time);
}

units::length::meter_t Buhlmann::ceiling() const {
    const auto pressure = _compartments.ceiling();
    return DepthFromPressure(pressure, _water);
}

} // namespace bungee
