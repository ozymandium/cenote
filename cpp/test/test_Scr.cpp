#include <units/unit.h>
#include <units/concepts.h>

#include <units/isq/dimensions/time.h>
#include <units/isq/dimensions/volume.h>

#include <units/isq/si/volume.h>
#include <units/isq/si/time.h>
#include <units/isq/si/prefixes.h>

#include <units/quantity.h>
#include <units/symbol_text.h>
#include <units/unit.h>


//
// Pattern matched from units/isq/dimensions/density.h
//

namespace units::isq {

template <typename Child, Unit U, typename...> struct dim_volume_rate;

template <typename Child, Unit U, DimensionOfT<dim_volume> V, DimensionOfT<dim_time> T>
struct dim_volume_rate<Child, U, V, T>
    : derived_dimension<Child, U, exponent<V, 1>, exponent<T, -1>> {
};

template <typename T>
concept VolumeRate = QuantityOfT<T, dim_volume_rate>;

} // namespace units::isq

//
// Pattern matched from units/isq/si/density.h
//

namespace units::isq::si {

// struct litre_per_minute : derived_unit<litre_per_minute, dim_volume_rate, litre, minute> {};
struct metre_cub_per_second : derived_unit<metre_cub_per_second> {};
// struct litre_per_minute : derived_unit<litre_per_minute> {};
// struct cuft_per_min : derived_unit<cuft_per_min> {};

struct dim_volume_rate
    : isq::dim_volume_rate<dim_volume_rate, metre_cub_per_second, dim_volume, dim_time> {};

template <UnitOf<dim_volume_rate> U, Representation Rep = double>
using volume_rate = quantity<dim_volume_rate, U, Rep>;

// inline namespace literals {

// // L / min
// constexpr auto operator"" _q_L_per_min(unsigned long long l)
// {
//   gsl_ExpectsAudit(std::in_range<std::int64_t>(l));
//   return volume_rate<litre_per_minute, std::int64_t>(static_cast<std::int64_t>(l));
// }
// constexpr auto operator"" _q_L_per_min(long double l) { return volume_rate<litre_per_minute, long double>(l); }

// // constexpr auto operator"" _q_cuft_per_min(unsigned long long l)
// // {
// //   gsl_ExpectsAudit(std::in_range<std::int64_t>(l));
// //   return volume_rate<cuft_per_min, std::int64_t>(static_cast<std::int64_t>(l));
// // }
// // constexpr auto operator"" _q_ft3_per_min(long double l) { return volume_rate<cuft_per_min, long double>(l); }

// }  // namespace literals

}  // namespace units::isq::si

// namespace units::aliases::isq::si::inline volume_rate {

// template<Representation Rep = double>
// using L_per_min = units::isq::si::volume_rate<units::isq::si::litre_per_minute, Rep>;

// }  // namespace units::aliases::isq::si::inline volume_rate
