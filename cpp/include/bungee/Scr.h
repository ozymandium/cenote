#pragma once

#include "Tank.h"
#include "Water.h"
#include "custom_units.h"

namespace bungee {

units::volume_rate::liter_per_minute_t
ScrFromSac(units::pressure_rate::pounds_per_square_inch_minute_t sac, const Tank& tank);

units::pressure_rate::pounds_per_square_inch_minute_t
SacFromScr(units::volume_rate::liter_per_minute_t scr, const Tank& tank);

units::volume_rate::liter_per_minute_t ScrAtDepth(units::volume_rate::liter_per_minute_t scr,
                                                  units::length::meter_t depth, Water water);

} // namespace bungee
