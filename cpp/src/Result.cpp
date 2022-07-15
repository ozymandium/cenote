#include <bungee/Result.h>

namespace bungee {

static_assert(units::math::round(units::time::minute_t(1) / Result::TIME_INC) ==
                  units::time::minute_t(1) / Result::TIME_INC,
              "pick a time increment that's a clean factor of 1 minute");

Result::Result(const Plan& plan) : _plan(plan)
{
    _plan.validate();

    // start by figuring out the number of points
    const units::time::minute_t duration = plan.points.back().time - plan.points.front().time;
    const size_t N = (duration / TIME_INC).value() + 1;
}

} // namespace bungee
