#pragma once

#include <units.h>

namespace units {

namespace category {

typedef base_unit<detail::meter_ratio<3>, std::ratio<0>, std::ratio<-1>> volume_rate_unit;
typedef base_unit<detail::meter_ratio<-1>, std::ratio<1>, std::ratio<-3>> pressure_rate_unit;

} // namespace category

/*
 * Volume rate
 */
UNIT_ADD(volume_rate, cubic_meter_per_second, cubic_meters_per_second, cu_m_per_s,
         unit<std::ratio<1>, units::category::volume_rate_unit>)
UNIT_ADD(volume_rate, liter_per_minute, liters_per_minute, L_per_min,
         compound_unit<volume::liters, inverse<time::minutes>>)
UNIT_ADD(volume_rate, cubic_foot_per_minute, cubic_feet_per_minute, cu_ft_per_min,
         compound_unit<volume::cubic_foot, inverse<time::minutes>>)
UNIT_ADD_CATEGORY_TRAIT(volume_rate)

/*
 * Pressure rate
 */
UNIT_ADD(pressure_rate, pascal_per_second, pascals_per_second, Pa_per_s,
         unit<std::ratio<1>, units::category::pressure_rate_unit>)
UNIT_ADD(pressure_rate, pounds_per_square_inch_minute, pounds_per_square_inch_minute, psi_per_min,
         compound_unit<pressure::pounds_per_square_inch, inverse<time::minutes>>)
UNIT_ADD(pressure_rate, bar_per_minute, bar_per_minute, bar_per_min,
         compound_unit<pressure::bar, inverse<time::minutes>>)
UNIT_ADD_CATEGORY_TRAIT(pressure_rate)

} // namespace units

namespace bungee {

using Acceleration = units::acceleration::meters_per_second_squared_t;
using Density = units::density::kilograms_per_cubic_meter_t;
using Depth = units::length::meter_t;
using Pressure = units::pressure::bar_t;
using PressureRate = units::pressure_rate::bar_per_minute_t;
using Volume = units::volume::liter_t;
using VolumeRate = units::volume_rate::liter_per_minute_t;
using Time = units::time::minute_t;
using Scalar = units::dimensionless::dimensionless_t;

} // namespace bungee