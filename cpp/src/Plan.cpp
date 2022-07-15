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

Plan::Plan(Water water, const Scr& scr, const TankLoadout& tanks, const std::vector<Point>& points)
    : Plan(water, scr, tanks)
{
    for (auto point : points) {
        addPoint(point);
    }
    finalize();
}

Plan::Plan(Water water, const Scr& scr, const TankLoadout& tanks)
    : _water(water), _scr(scr), _tanks(tanks), _finalized(false)
{
    _scr.validate();
    for (auto const& [name, tank] : tanks) {
        tank.validate();
    }
}

void Plan::setTank(const std::string& name)
{
    ensure(_tanks.contains(name), "unknown tank");
    _currentTank = name;
}

void Plan::addPointFromDuration(units::time::minute_t duration, units::length::meter_t depth)
{
    ensure(!_points.empty(), "can't add first point from duration");
    addPoint(_points.back().time + duration, depth);
}

void Plan::addPoint(units::time::minute_t time, units::length::meter_t depth)
{
    ensure(_currentTank.has_value(), "current tank not set");
    addPoint(Point{time, depth, _currentTank.value()});
}

void Plan::addPoint(const Point& point)
{
    ensure(!_finalized, "finalized already");
    // checks
    if (_points.empty()) {
        ensure(point.time == 0_min, "first point must start at zero time");
        ensure(point.depth == 0_m, "first point must be start at the surface");
    }
    else {
        // for now, only allow points that increase in time, add on pure square profile support
        // later.
        ensure(point.time > _points.back().time, "each point must increase in time");
        // for now, keep time denominated in integer minutes to keep things simple
        ensure(point.time.value() == units::unit_cast<int64_t>(point.time), "time must be in integer (whole) minutes");
    }
    ensure(_tanks.contains(point.tank), "unknown tank name");
    _points.push_back(point);
}

void Plan::finalize()
{
    // water doesn't need validation
    // scr/tank already validated
    // points were validated as they were added
    ensure(_points.size() > 1, "need at least 2 poins");
    _finalized = true;
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
