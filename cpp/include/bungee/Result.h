#pragma once

#include "Plan.h"

#include "custom_units.h"
#include <Eigen/Dense>

namespace bungee {

struct Result {
    struct Deco {
        /// FIXME this is trashy
        void resize(size_t timeCount, size_t compartmentCount);

        /// Minimum depth for decompression model
        Eigen::VectorXd ceiling;
        /// the gradient (0-1)
        Eigen::VectorXd gradient;

        Eigen::MatrixXd M0s;
        Eigen::MatrixXd tissuePressures;
        Eigen::MatrixXd ceilings;
        Eigen::MatrixXd gradients;
    };

    /// \param[in} N number of points to allocate for all arrays (will be same sized)
    Result(const Plan& plan);

    Eigen::VectorXd GetAmbientPressure(const Plan& plan, Eigen::Ref<const Eigen::VectorXd> depth);

    /// FIXME: need to select working vs deco scr.
    static std::map<std::string, Eigen::VectorXd>
    GetTankPressure(const Plan& plan, Eigen::Ref<const Eigen::VectorXd> time,
                    Eigen::Ref<const Eigen::VectorXd> depth);

    /// FIXME: this assumes that the model units are the same as the units in the rest of bungee,
    /// whereas the model stuff was left explicit instead of typedef'd explicitly to allow them
    /// to potentially be different in the future.
    static Deco GetDeco(const Plan& plan, Eigen::Ref<const Eigen::VectorXd> time,
                        Eigen::Ref<const Eigen::VectorXd> depth);

    /// time in minutes
    ///
    /// FIXME: use array instead? is it lighter weight?
    Eigen::VectorXd time;
    /// depth in meters
    Eigen::VectorXd depth;
    /// in bar
    Eigen::VectorXd ambientPressure;
    /// tank pressure by tank name
    std::map<std::string, Eigen::VectorXd> tankPressure;

    Deco deco;
};

/// \brief Gas consumption between 2 plan points. Assume that the scr in point 0 applies throughout
/// and ignore the scr in point 1. Allows times to be equal. For changes in depth, compute at the
/// average of the two depths.
///
/// TODO: this uses average depth and a single SCR, which is suboptimal. Integrating (whether
/// analytically or numerically) would be much more accurate for large differences in depth between
/// the 2 points.
///
/// \param[in] duration Amount of time spent at depth
///
/// \param[in] depth Depth, assumed to be constant for all of `duration`.
///
/// \param[in] scr SCR, assumed to be constant between pt0 and pt1.
///
/// \param[in] water The type of water, assumed to be constant betwwen pt0 and pt1.
///
/// \return Consumed gas in surface volume.
Volume Usage(Time duration, Depth depth, VolumeRate scr, Water water);

} // namespace bungee
