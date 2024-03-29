#include <bungee/custom_units.h>
#include <bungee/ensure.h>
#include <bungee/utils.h>

using namespace units::literals;

namespace bungee {

size_t GetNumPoints(Time duration)
{
    // check that the time increment is such that we can divide the plan cleanly in time
    // TODO: make this a static assert
    // FIXME: make this generic, instead of hardcoding 1s increments. This assumes this function
    // is only used for ascending.
    static constexpr double POINTS_PER_MINUTE = (1_min / MODEL_TIME_INC)();
    static_assert(POINTS_PER_MINUTE == double(int64_t(POINTS_PER_MINUTE)),
                  "GetNumPoints: pick a time increment that's a clean factor of 1 minute");
    ensure(duration > 0_s, "GetNumPoints: negative duration");
    return units::unit_cast<int64_t>(duration * POINTS_PER_MINUTE);
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