#include <bungee/Constants.h>
#include <bungee/Plan.h>
#include <bungee/Scr.h>
#include <bungee/ensure.h>

using namespace units::literals;

namespace bungee {

void Plan::Scr::validate() const
{
    ensure(work > 0_L_per_min, "must have positive working SCR");
    ensure(deco > 0_L_per_min, "must have positive working SCR");
}

void Plan::TankConfig::validate() const { ensure(pressure > 0_bar, "starting with an empty tank"); }

void Plan::Point::validate() const
{
    ensure(time.value() >= 0, "negative time");
    ensure(depth.value() >= 0, "negative depth");
}

Plan::Plan(Water water, const GradientFactor& gf, const Scr& scr, const TankLoadout& tanks)
    : _water(water), _gf(gf), _scr(scr), _tanks(tanks), _finalized(false)
{
    // ensure(low <= high, "gf low larger than gf high");
    ensure(0 < _gf.low, "gf low must be > 0");
    ensure(_gf.low <= 1, "gf low must be at most 100%");
    ensure(0 < _gf.high, "gf high must be > 0");
    ensure(_gf.high <= 1, "gf high must be at most 100%");

    // water doesn't need checking
    // check scr
    _scr.validate();
    // check tank config
    for (auto const& [name, tank] : tanks) {
        tank.validate();
    }
}

void Plan::setTank(const std::string& name)
{
    ensure(_tanks.contains(name), "unknown tank");
    _currentTank = name;
    if (_profile.empty()) {
        _profile.emplace_back(0_s, 0_m, name);
    }
    else {
        _profile.back().tank = name;
    }
}

void Plan::addSegment(Time duration, Depth endDepth)
{
    ensure(duration > 0_s, "negative segment duration");
    ensure(duration() == units::unit_cast<int64_t>(duration),
           "duration must be in integer minutes");
    ensure(_currentTank.has_value(), "current tank not set");
    ensure(!_profile.empty(), "points empty. setting current tank should have set this.");
    ensure(!_finalized, "finalized already");
    const Time time = _profile.back().time + duration;
    ensure(time > _profile.back().time, "negative segment duration");
    _profile.emplace_back(time, endDepth, _currentTank.value());
}

void Plan::finalize()
{
    // water doesn't need validation
    // scr/tank already validated
    // points were validated as they were added
    ensure(_profile.size() > 1, "need at least 2 poins");
    _finalized = true;
}

Eigen::VectorXd Plan::time() const
{
    Eigen::VectorXd data(_profile.size());
    for (size_t i = 0; i < _profile.size(); ++i) {
        data(i) = _profile[i].time();
    }
    return data;
}

Eigen::VectorXd Plan::depth() const
{
    Eigen::VectorXd data(_profile.size());
    for (size_t i = 0; i < _profile.size(); ++i) {
        data(i) = _profile[i].depth();
    }
    return data;
}

const std::string& Plan::getTankAtTime(const Time time) const
{
    ensure(_profile.front().time <= time, "getTankAtTime: time is before beginning of dive");
    ensure(time <= _profile.back().time, "getTankAtTime: time is after end of dive");
    for (size_t i = 0; i < _profile.size() - 1; ++i) {
        if ((_profile[i].time <= time) && (time <= _profile[i + 1].time)) {
            return _profile[i].tank;
        }
    }
    ensure(false, "couldn't find tank");
}

std::string Plan::bestMix(const Depth depth) const
{
    // select tanks with ppo2 below the threshold
    std::vector<std::string> safeNames;
    std::vector<Pressure> safePpN2s;
    for (const auto& [name, config] : _tanks) {
        Mix::PartialPressure partialPressure = config.mix.partialPressure(depth, _water);
        if (partialPressure.O2 <= MAX_DECO_PPO2) {
            safeNames.push_back(name);
            safePpN2s.push_back(partialPressure.N2);
        }
        // todo: check for hypoxia here also
    }
    // pick the remaining tank with the lowest nitrogen content
    const auto it = std::min_element(safePpN2s.begin(), safePpN2s.end());
    // todo: pick one with the most remaining pressure to solve for multiple cylinders with the
    // same mixes
    return safeNames[size_t(it - safePpN2s.begin())];
}

} // namespace bungee
