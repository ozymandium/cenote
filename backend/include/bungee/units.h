#pragma once

#include <units.h>

namespace units {

// namespace volume_rate {

// using liters_per_minute = 

// }

UNIT_ADD(volume_rate, liters_per_minute, liters_per_minute, L_per_min,
         compound_unit<volume::liters, inverse<time::minute>>)
UNIT_ADD_CATEGORY_TRAIT(volume_rate)

UNIT_ADD(pressure_rate, pounds_per_square_inch_per_minute, pounds_per_square_inch_per_minute,
         psi_per_min, compound_unit<pressure::pounds_per_square_inch, inverse<time::minute>>)
UNIT_ADD_CATEGORY_TRAIT(pressure_rate)

} // namespace units
