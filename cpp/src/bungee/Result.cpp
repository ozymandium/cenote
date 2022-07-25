#include <bungee/Constants.h>
#include <bungee/Result.h>
#include <bungee/Scr.h>
#include <bungee/deco/buhlmann/Buhlmann.h>
#include <bungee/ensure.h>
#include <bungee/utils.h>

#include <iostream>

using namespace units::literals;

namespace bungee {

namespace {

/// STL abs is not constexpr
template <typename T> constexpr auto Abs(T const& x) noexcept { return x < 0 ? -x : x; }

template <typename Unit> Eigen::VectorXd UnitsVecToEigen(const std::vector<Unit>& vec)
{
    Eigen::VectorXd eigen(vec.size());
    for (size_t i = 0; i < vec.size(); ++i) {
        eigen(i) = vec[i]();
    }
    return eigen;
}

} // namespace

void Result::Deco::resize(size_t timeCount, size_t compartmentCount)
{
    ceiling = Eigen::VectorXd::Zero(timeCount);
    gradient = Eigen::VectorXd::Zero(timeCount);

    M0s = Eigen::MatrixXd::Zero(compartmentCount, timeCount);
    tissuePressures = Eigen::MatrixXd::Zero(compartmentCount, timeCount);
    ceilings = Eigen::MatrixXd::Zero(compartmentCount, timeCount);
    gradients = Eigen::MatrixXd::Zero(compartmentCount, timeCount);
}

Result::Result(const Plan& plan)
{
    ensure(plan.finalized(), "plan not finalized");

    // start by figuring out the number of points
    const size_t N = GetNumPoints(plan.profile().back().time);

    // linearly space time points
    time = Eigen::VectorXd::LinSpaced(N, 0, plan.profile().back().time());
    // linearly interpolate from plan to get depths at high resolution
    depth = Interpolate(plan.time(), plan.depth(), time);
    ambientPressure = GetAmbientPressure(plan, depth);
    tankPressure = GetTankPressure(plan, time, depth);
    deco = GetDeco(plan, time, depth);
}

Eigen::VectorXd Result::GetAmbientPressure(const Plan& plan,
                                           Eigen::Ref<const Eigen::VectorXd> depth)
{
    Eigen::VectorXd ret(depth.rows());
    for (size_t i = 0; i < ret.rows(); ++i) {
        ret[i] = PressureFromDepth(Depth(depth[i]), plan.water())();
    }
    return ret;
}

std::map<std::string, Eigen::VectorXd>
Result::GetTankPressure(const Plan& plan, Eigen::Ref<const Eigen::VectorXd> time,
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

Result::Deco Result::GetDeco(const Plan& plan, Eigen::Ref<const Eigen::VectorXd> time,
                             Eigen::Ref<const Eigen::VectorXd> depth)
{
    using namespace deco::buhlmann;
    Buhlmann model(Buhlmann::Params{
        .water = plan.water(), .model = Model::ZHL_16A, .gf_low = 0.3, .gf_high = 0.7});
    // assume infinite surface interval preceding this dive.
    model.equilibrium(SURFACE_AIR_PP);

    Deco data;
    data.resize(time.size(), model.compartmentCount());

    // set initial value in the 0th position
    data.ceiling[0] = model.ceiling()();
    data.gradient[0] = model.gf(Depth(depth[0]));

    data.M0s.col(0) = UnitsVecToEigen(model.M0s());
    data.tissuePressures.col(0) = UnitsVecToEigen(model.pressures());
    data.ceilings.col(0) = UnitsVecToEigen(model.ceilings());
    data.gradients.col(0) = UnitsVecToEigen(model.gfs(Depth(depth[0])));

    // iterate over increments
    for (size_t i = 1; i < time.size(); ++i) {
        const Time duration(time[i] - time[i - 1]);
        // This computes pressure at the average depth.
        // dipplanner uses Schreiner equation for segments with non-constant depth, which would
        // allow using large increments
        const Depth avgDepth((depth[i - 1] + depth[i]) * 0.5);
        const std::string& activeTank = plan.getTankAtTime(Time(time[i - 1]));
        const Mix& mix = plan.tanks().at(activeTank).mix;
        const Mix::PartialPressure partialPressure = mix.partialPressure(avgDepth, plan.water());
        model.update(partialPressure, duration);
        data.ceiling[i] = model.ceiling()();
        data.gradient[i] = model.gf(Depth(depth[i]));
        data.M0s.col(i) = UnitsVecToEigen(model.M0s());
        data.tissuePressures.col(i) = UnitsVecToEigen(model.pressures());
        data.ceilings.col(i) = UnitsVecToEigen(model.ceilings());
        data.gradients.col(i) = UnitsVecToEigen(model.gfs(Depth(depth[i])));
    }

    return data;
}

Volume Usage(const Time duration, const Depth depth, const VolumeRate scr, const Water water)
{
    ensure(duration() > 0, "Usage: negative or zero time duration");
    ensure(scr() > 0, "negative or zero scr");
    const auto volumeRate = ScrAtDepth(scr, depth, water);
    return volumeRate * duration;
}

} // namespace bungee
