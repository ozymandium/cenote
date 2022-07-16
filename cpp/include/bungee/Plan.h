#pragma once

#include "Mix.h"
#include "Tank.h"
#include "Water.h"
#include "custom_units.h"

#include <Eigen/Dense>

#include <optional>
#include <vector>

namespace bungee {

// /// This is used to construct the list of Point as they are added in a loop so that they don't
// /// have to be figured out in batch.
// class PlanBuilder {
// public:
//     PlanBuilder();

//     /// \brief Set the tank type that will be used for any points added.
//     void setTank(const std::string& tank);

//     /// \brief Add a point at the specified depth and time using the currently set SCR and tank.
//     ///
//     /// FIXME: allow points to be at the same time as the current point to build pure square
//     /// profiles for investigation purposes.
//     void addPoint(units::time::minute_t time, units::length::meter_t depth);

//     const std::vector<Point> get() const;

// private:
//     std::optional<std::string> _tank;
//     std::vector<Point> _points;
// };

/// A coarse dive plan that is provided by the user. Computations are done based on this input.
/// PlanBuilder should be used to compute constructor args.
/// This may or may not include the final ascent.
class Plan {

public:
    struct Scr {
        // /// Provide a constructor to prevent pybind from default initializing
        // Scr(units::volume_rate::liter_per_minute_t, units::volume_rate::liter_per_minute_t);

        /// SCR during the bottom portion of the dive, i.e., everything until the final ascent.
        units::volume_rate::liter_per_minute_t work;
        /// SCR during the decompression portion of the dive, i.e., during the final ascent.
        units::volume_rate::liter_per_minute_t deco;

        void validate() const;
    };

    /// Represents and single tank configuration at the start of the dive
    struct TankConfig {
        // /// Provide a constructor to prevent pybind from default initializing
        // TankConfig()

        /// The type of tank.
        Tank::Type type;
        /// The initial pressure at the start of the dive.
        units::pressure::bar_t pressure;
        /// What gas is in the tank.
        Mix mix;

        void validate() const;
    };

    using TankLoadout = std::map<std::string, TankConfig>;

    /// A dive plan is simply a series of points of depth and time, with other relevant info added.
    struct Point {
        /// Time elapsed since the beginning of the dive [min]
        units::time::minute_t time;
        /// Distance below surface [m]
        units::length::meter_t depth;
        /// Name of tank in use beginning at `time` and proceeding forward to the next point.
        std::string tank;

        /// \brief Assert plausibility.
        ///
        /// TODO: lock down construction instead?
        void validate() const;
    };

    using Profile = std::vector<Point>;

    /// Will finalize.
    Plan(Water water, const Scr& scr, const TankLoadout& tanks, const Profile& points);

    /*
     * API for constructing profile one point at a time.
     */

    /// \brief Construct without providing point, for use when parsing a list that doesn't require
    /// the user to specify a tank every point (only at swaps).
    ///
    Plan(Water water, const Scr& scr, const TankLoadout& tanks);

    void setTank(const std::string& name);

    void addPointFromDuration(units::time::minute_t duration, units::length::meter_t depth);
    void addPoint(units::time::minute_t time, units::length::meter_t depth);
    void addPoint(const Point& point);

    void finalize();
    bool finalized() const { return _finalized; }

    /*
     * Getters
     */

    Water water() const { return _water; }
    const Scr& scr() const { return _scr; }
    const TankLoadout& tanks() const { return _tanks; }
    const Profile& profile() const { return _profile; }

    Eigen::ArrayXd time() const;
    Eigen::ArrayXd depth() const;

private:
    const Water _water;
    const Scr _scr;
    /// Store tank configuration by the name the user gives to each tank.
    const TankLoadout _tanks;
    /// AoS vs SoA here?
    /// Lots of uses for both cases
    Profile _profile;

    std::optional<std::string> _currentTank;

    bool _finalized;
};

/// \brief Gas consumption between 2 plan points. Assume that the scr in point 0 applies throughout
/// and ignore the scr in point 1. Allows times to be equal. For changes in depth, compute at the
/// average of the two depths.
///
/// TODO: this uses average depth and a single SCR, which is suboptimal. Integrating (whether
/// analytically or numerically) would be much more accurate for large differences in depth between
/// the 2 points.
///
/// \param[in] pt0 The first point.
///
/// \param[in] pt1 The second point.
///
/// \param[in] scr SCR, assumed to be constant between pt0 and pt1.
///
/// \param[in] water The type of water, assumed to be constant betwwen pt0 and pt1.
///
/// \return Consumed gas in surface volume.
units::volume::liter_t Usage(const Plan::Point& pt0, const Plan::Point& pt1,
                             units::volume_rate::liter_per_minute_t scr, Water water);

} // namespace bungee