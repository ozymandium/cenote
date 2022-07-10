#include <bungee/Buhlmann.h>
#include <bungee/Constants.h>
#include <bungee/Mix.h>

namespace bungee {

Buhlmann::Buhlmann(const Model model) : _compartments(model) {}

// void Buhlmann::init() {
//     // _compartments.equilibrium(Air, SURFACE_PRESSURE_BAR);
// }

} // namespace bungee
