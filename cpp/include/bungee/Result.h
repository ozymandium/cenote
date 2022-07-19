#pragma once

#include "Plan.h"

#include "custom_units.h"
#include <Eigen/Dense>

namespace bungee {

struct Result {
    // 0.1 minutes to help avoid floating point problems
    static constexpr Time TIME_INCREMENT = units::time::second_t(6);

    /// \param[in} N number of points to allocate for all arrays (will be same sized)
    Result(const Plan& plan);

    /// time in minutes
    ///
    /// FIXME: use array instead? is it lighter weight?
    Eigen::VectorXd time;
    /// depth in meters
    Eigen::VectorXd depth;
    /// tank pressure by tank name
    std::map<std::string, Eigen::VectorXd> pressure;
};

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
Eigen::VectorXd Interpolate(Eigen::Ref<const Eigen::VectorXd> xp,
                            Eigen::Ref<const Eigen::VectorXd> yp,
                            Eigen::Ref<const Eigen::VectorXd> x);

} // namespace bungee
