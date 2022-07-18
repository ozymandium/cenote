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

Plan::Plan(Water water, const Scr& scr, const TankLoadout& tanks)
    : _water(water), _scr(scr), _tanks(tanks), _finalized(false)
{
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

units::volume::liter_t Usage(const Plan::Point& pt0, const Plan::Point& pt1,
                             const units::volume_rate::liter_per_minute_t scr, const Water water)
{
    ensure(pt0.time <= pt1.time, "second point before first point");
    ensure(scr.value() > 0, "negative or zero scr");
    const auto duration = pt1.time - pt0.time;
    const auto avgDepth = (pt0.depth + pt1.depth) * 0.5;
    const auto volumeRate = ScrAtDepth(scr, avgDepth, water);
    return volumeRate * duration;
}

} // namespace bungee
