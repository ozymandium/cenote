#include <bungee/Result.h>
#include <bungee/ensure.h>

using namespace units::literals;

namespace bungee {

namespace {

size_t GetNumPoints(units::time::minute_t duration) {
    // check that the time increment is such that we can divide the plan cleanly in time
    // TODO: make this a static assert
    static constexpr units::dimensionless::dimensionless_t POINTS_PER_MINUTE = 1_min / Result::TIME_INCREMENT;
    ensure(units::math::round(POINTS_PER_MINUTE) == POINTS_PER_MINUTE,
              "pick a time increment that's a clean factor of 1 minute");
    return units::unit_cast<int64_t> (duration * POINTS_PER_MINUTE);  
}

}

Result GetResult(const Plan& plan)
{

    ensure(plan.finalized(), "plan not finalized");

    // start by figuring out the number of points
    const Plan::Profile& profile = plan.profile();
    const units::time::minute_t duration = profile.back().time - profile.front().time;
    const size_t N = GetNumPoints(duration);

    return Result();
}

} // namespace bungee
