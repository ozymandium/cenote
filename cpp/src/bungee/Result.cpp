#include <bungee/Buhlmann.h>
#include <bungee/Result.h>
#include <bungee/Scr.h>
#include <bungee/ensure.h>

#include <fmt/format.h>
#include <unsupported/Eigen/Splines>

#include <iostream>

using namespace units::literals;

namespace bungee {

namespace {

size_t GetNumPoints(Time duration)
{
    // check that the time increment is such that we can divide the plan cleanly in time
    // TODO: make this a static assert
    static constexpr double POINTS_PER_MINUTE = (1_min / Result::TIME_INCREMENT)();
    static_assert(POINTS_PER_MINUTE == double(int64_t(POINTS_PER_MINUTE)),
                  "pick a time increment that's a clean factor of 1 minute");
    return units::unit_cast<int64_t>(duration * POINTS_PER_MINUTE);
}

/// STL abs is not constexpr
template <typename T> constexpr auto Abs(T const& x) noexcept { return x < 0 ? -x : x; }

} // namespace

Result::Result(const Plan& plan)
{
    ensure(plan.finalized(), "plan not finalized");

    // start by figuring out the number of points
    const size_t N = GetNumPoints(plan.profile().back().time);

    // linearly space time points
    time = Eigen::VectorXd::LinSpaced(N, 0, plan.profile().back().time());
    // linearly interpolate from plan to get depths at high resolution
    depth = Interpolate(plan.time(), plan.depth(), time);
    pressure = GetPressure(plan, time, depth);
    ceiling = GetCeiling(plan, time, depth);
}

std::map<std::string, Eigen::VectorXd> Result::GetPressure(const Plan& plan,
                                                           Eigen::Ref<const Eigen::VectorXd> time,
                                                           Eigen::Ref<const Eigen::VectorXd> depth)
{
    std::map<std::string, Eigen::VectorXd> pressure;
    // get tank pressures
    // first initialize tanks
    std::map<std::string, Tank> tanks;
    for (auto const& [name, tankConfig] : plan.tanks()) {
        tanks.emplace(name, GetTankAtPressure(tankConfig.type, tankConfig.pressure));
    }
    // initialize pressure arrays to zero and copy starting pressures into the 0th slot
    for (auto const& [name, tank] : tanks) {
        pressure.emplace(name, Eigen::VectorXd::Zero(time.size()));
        pressure[name][0] = tank.pressure()();
    }
    // iterate through time decreasing pressure in whatever tank is active
    for (size_t i = 1; i < time.size(); ++i) {
        // compute the average depth and treat it as constant. smaller time increments work better
        // here.
        const Time duration(time[i] - time[i - 1]);
        const Depth avgDepth((depth[i - 1] + depth[i]) * 0.5);
        // get the amount consumed at this depth
        // FIXME: need to select working vs deco scr.
        const Volume volumeConsumed = Usage(duration, avgDepth, plan.scr().work, plan.water());
        // tank at the beginning of the increment is the tank for the duration of the increment.
        // same principle as for the broad segments in the plan.
        const std::string& activeTank = plan.getTankAtTime(Time(time[i - 1]));
        // iterate over all tanks
        for (auto& [name, tank] : tanks) {
            // if tank is active, reduce the volume by the amount consumed this increment and
            if (name == activeTank) {
                tank.decreaseVolume(volumeConsumed);
            }
            // record the new pressure at the end of the increment
            pressure[name][i] = tank.pressure()();
        }
    }
    return pressure;
}

Eigen::VectorXd Result::GetCeiling(const Plan& plan, Eigen::Ref<const Eigen::VectorXd> time,
                                   Eigen::Ref<const Eigen::VectorXd> depth)
{
    Eigen::VectorXd ceiling = Eigen::VectorXd::Zero(time.size());
    // tank name to mix

    Buhlmann model(Model::ZHL_16A);
    model.init();

    // set initial value in the 0th position
    ceiling[0] = model.ceiling(plan.water())();

    // iterate over increments
    for (size_t i = 1; i < time.size(); ++i) {
        const Time duration(time[i] - time[i - 1]);
        const Depth avgDepth((depth[i - 1] + depth[i]) * 0.5);
        const std::string& activeTank = plan.getTankAtTime(Time(time[i - 1]));
        const Mix& mix = plan.tanks().at(activeTank).mix;
        const Mix::PartialPressure partialPressure = mix.partialPressure(avgDepth, plan.water());
        model.update(partialPressure, duration);
        ceiling[i] = model.ceiling(plan.water())();
    }

    return ceiling;
}

Volume Usage(const Time duration, const Depth depth, const VolumeRate scr, const Water water)
{
    ensure(duration() > 0, "Usage: negative or zero time duration");
    ensure(scr() > 0, "negative or zero scr");
    const auto volumeRate = ScrAtDepth(scr, depth, water);
    return volumeRate * duration;
}

Eigen::VectorXd Interpolate(Eigen::Ref<const Eigen::VectorXd> xp,
                            Eigen::Ref<const Eigen::VectorXd> yp,
                            Eigen::Ref<const Eigen::VectorXd> x)
{
    ensure(xp.size() == yp.size(), "xp and yp must be same size");
    // check that xp is increasing
    for (size_t i = 1; i < xp.size(); ++i) {
        ensure(xp[i] > xp[i - 1], "Interpolate: xp must be increasing");
    }
    // check range of x
    ensure((xp[0] <= x.array()).all(), "cannot interpolate before beginning");
    ensure((x.array() <= xp.tail(1)[0]).all(), "cannot interpolate after end");

    auto FindIdx = [&](const double val) {
        for (size_t i = 0; i < x.size() - 1; ++i) {
            if ((xp[i] <= val) && (val <= xp[i + 1])) {
                return i;
            }
        }
        ensure(false, "didn't find it");
    };

    // interpolate works on value between 0.0 and 1.0
    // create normalized value
    Eigen::VectorXd y(x.size());
    for (size_t i = 0; i < x.size(); ++i) {
        const size_t j = FindIdx(x[i]);
        const double slope = (yp[j + 1] - yp[j]) / (xp[j + 1] - xp[j]);
        const double diff = x[i] - xp[j];
        y[i] = yp[j] + slope * diff;
    }
    return y;
}

} // namespace bungee
