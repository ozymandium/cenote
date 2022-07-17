#pragma once

#include "Plan.h"

#include <Eigen/Dense>
#include "custom_units.h"

namespace bungee {

struct Result {
    // 0.1 minutes to help avoid floating point problems
    static constexpr Time TIME_INCREMENT = units::time::second_t(6);

    /// \param[in} N number of points to allocate for all arrays (will be same sized)
    Result(size_t N);

    /// time in minutes
    Eigen::ArrayXd time;
    /// depth in meters
    Eigen::ArrayXd depth;
};

Result GetResult(const Plan& plan);

/// \brief 1d interpolation
///
/// \param[in] data
///    [ x1, x2, ..., xM ]
///    [ y1, y2, ..., yM ]
///
/// \param[in] x
///    [ x1, x2, ..., xN ]
///
/// \return interpolated y data corresponding to x
Eigen::ArrayXd Interpolate(Eigen::Ref<const Eigen::ArrayXd> xp, Eigen::Ref<const Eigen::ArrayXd> yp,
                           Eigen::Ref<const Eigen::ArrayXd> x);

} // namespace bungee
