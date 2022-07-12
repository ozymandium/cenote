#pragma once

#include "Tank.h"
#include "Water.h"
#include "units.h"

namespace bungee {

units::volume_rate::liters_per_minute
ScrFromSac(const Tank& tank, units::pressure_rate::pounds_per_square_inch_per_minute sac);

units::pressure_rate::pounds_per_square_inch_per_minute
SacFromScr(const Tank& tank, units::volume_rate::liters_per_minute scr);

units::volume_rate::liters_per_minute ScrAtDepth(units::volume_rate::liters_per_minute scr,
                                                 units::length::meter_t depth, Water water);

} // namespace bungee
