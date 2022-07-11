#include <bungee/Buhlmann.h>
#include <bungee/Constants.h>
#include <bungee/Mix.h>

namespace bungee {

Buhlmann::Buhlmann(const Model model) : _compartments(model) {}

void Buhlmann::init() { _compartments.equilibrium(SURFACE_AIR_PP); }

void Buhlmann::update(const Mix::PartialPressure& partialPressure, units::time::minute_t time) {
    _compartments.update(partialPressure, time);
}

units::pressure::bar_t Buhlmann::ceiling() const { return _compartments.ceiling(); }

} // namespace bungee
