#pragma once

#include "Mix.h"
#include "Tank.h"
#include "Water.h"
#include "custom_units.h"

#include <Eigen/Dense>

#include <optional>
#include <vector>

namespace bungee {

/// A coarse dive plan that is provided by the user. Computations are done based on this input.
/// PlanBuilder should be used to compute constructor args.
/// This may or may not include the final ascent.
class Plan {
public:
    struct Scr {
        /// SCR during the bottom portion of the dive, i.e., everything until the final ascent.
        VolumeRate work;
        /// SCR during the decompression portion of the dive, i.e., during the final ascent.
        VolumeRate deco;

        void validate() const;
    };

    /// Represents and single tank configuration at the start of the dive
    struct TankConfig {
        /// The type of tank.
        Tank::Type type;
        /// The initial pressure at the start of the dive.
        Pressure pressure;
        /// What gas is in the tank.
        Mix mix;

        void validate() const;
    };

    using TankLoadout = std::map<std::string, TankConfig>;

    /// A dive plan is simply a series of points of depth and time, with other relevant info added.
    struct Point {
        /// Time elapsed since the beginning of the dive [min]
        Time time;
        /// Distance below surface [m]
        Depth depth;
        /// Name of tank in use beginning at `time` and proceeding forward to the next point.
        std::string tank;

        /// \brief Except if not plausible.
        void validate() const;
    };

    using Profile = std::vector<Point>;

    /// \brief Construct without providing point, for use when parsing a list that doesn't require
    /// the user to specify a tank every point (only at swaps).
    ///
    Plan(Water water, const Scr& scr, const TankLoadout& tanks);

    // just for Planner to use
    void setProfile(const Profile& profile)
    {
        _profile = profile;
        _currentTank = _profile.back().tank;
    }

    /*
     * Builders
     */

    void setTank(const std::string& name);

    void addSegment(Time duration, Depth depth);

    void finalize();
    bool finalized() const { return _finalized; }

    /*
     * Getters
     */

    Water water() const { return _water; }
    const Scr& scr() const { return _scr; }
    const TankLoadout& tanks() const { return _tanks; }
    const Profile& profile() const { return _profile; }

    /// FIXME: use Eigen::Map to avoid creating new array, but will have to fix the size of the
    /// tank member in Point and switch to a different type
    ///
    /// FIXME: save these as members on finalize?
    Eigen::VectorXd time() const;
    Eigen::VectorXd depth() const;

    /// FIXME: this is an O(N) lookup. That's dogshit. Figure out a way to do O(1) lookup. Will
    /// have to index tanks in an array or something other than using strings.
    const std::string& getTankAtTime(Time time) const;

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

} // namespace bungee