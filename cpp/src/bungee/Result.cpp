#include <bungee/Result.h>
#include <bungee/ensure.h>

#include <unsupported/Eigen/Splines>

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

/// returns a percentage (0.1 = 10%)
constexpr double PercentDiff(const double val, const double expected)
{
    return Abs((val - expected) / expected);
}

} // namespace

Result::Result(const size_t N) : time(N), depth(N) {}

Result GetResult(const Plan& plan)
{
    ensure(plan.finalized(), "plan not finalized");

    // start by figuring out the number of points
    const size_t N = GetNumPoints(plan.profile().back().time);

    Result result(N);

    // linearly space time points
    result.time = Eigen::ArrayXd::LinSpaced(N, 0, plan.profile().back().time());
    result.depth = Interpolate(plan.time(), plan.depth(), result.time);

    return result;
}

Eigen::ArrayXd Interpolate(Eigen::Ref<const Eigen::ArrayXd> xp, Eigen::Ref<const Eigen::ArrayXd> yp,
                           Eigen::Ref<const Eigen::ArrayXd> x)
{
    using Spline2d = Eigen::Spline<double, 2>;

    Eigen::Matrix2Xd data;
    data << xp, yp;

    // interpolate works on value between 0.0 and 1.0
    // create normalized value
    const double xpRange = xp.maxCoeff() - xp.minCoeff();
    const Eigen::ArrayXd xn = (xp - xp.minCoeff()) / xpRange;

    const Spline2d spline = Eigen::SplineFitting<Spline2d>::Interpolate(data, 2);
    Eigen::ArrayXd y(x.size());
    for (size_t i = 0; i < x.size(); ++i) {
        const Eigen::ArrayXd res = spline(xn[i]);
        ensure(PercentDiff(res(1), x[i]) < 1e-12,
               "interpolated value doesn't match expected value");
        y[i] = res(1);
    }
    return y;
}

} // namespace bungee
