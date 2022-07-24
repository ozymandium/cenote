/*

scratch/prototype code in need of cleanup.
yes the whole repo is prototype code that's god awful, but this is like, real bad.

*/

#include <bungee/Planner.h>
#include <bungee/Result.h> // for Interpolate. move that
#include <bungee/deco/buhlmann/Buhlmann.h>
#include <bungee/ensure.h>
#include <fmt/format.h>

using namespace units::literals;
using namespace bungee::deco::buhlmann;

namespace bungee {

static constexpr Time STOP_TIME_INC = 1_min;
static constexpr Depth STOP_DEPTH_INC = 10_ft;
static constexpr auto ASCENT_RATE = 20_ft / 1_min;
static constexpr Time MODEL_TIME_INC = 1_s;

namespace {

size_t GetNumPoints(Time duration)
{
    // check that the time increment is such that we can divide the plan cleanly in time
    // TODO: make this a static assert
    // FIXME: make this generic, instead of hardcoding 1s increments. This assumes this function
    // is only used for ascending.
    static constexpr double POINTS_PER_MINUTE = (1_min / MODEL_TIME_INC)();
    static_assert(POINTS_PER_MINUTE == double(int64_t(POINTS_PER_MINUTE)),
                  "pick a time increment that's a clean factor of 1 minute");
    return units::unit_cast<int64_t>(duration * POINTS_PER_MINUTE);
}

/// \return tank name within the tank loadout
std::string BestMix(const Plan::TankLoadout& tanks, const Depth depth, const Water water)
{
    static constexpr Pressure MAX_DECO_PPO2 = 1.6_atm;
    // select tanks with ppo2 below the threshold
    std::vector<std::string> safeNames;
    std::vector<Pressure> safePpN2s;
    for (const auto& [name, config] : tanks) {
        Mix::PartialPressure partialPressure = config.mix.partialPressure(depth, water);
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

std::string str(Depth unit) { return fmt::format("{}", units::length::to_string(unit)); }
std::string str(Time unit) { return fmt::format("{}", units::time::to_string(unit)); }

} // namespace

Plan Replan(const Plan& input)
{
    // start plan with the same configuration
    Plan output(input.water(), input.scr(), input.tanks());
    output.setProfile(input.profile());

    // tank has to be set to build forward
    output.setTank(output.profile().back().tank);

    // if end point is at the surface, nothing is needed.
    if (output.profile().back().depth == 0_m) {
        output.finalize();
        return output;
    }

    // get the deco model caught up to the last point the user gave us so we know where to start
    // with the ascent
    Buhlmann model(Buhlmann::Params{
        .water = output.water(), .model = Model::ZHL_16A, .gf_low = 0.3, .gf_high = 0.7});
    // assume infinite surface interval preceding this dive.
    model.equilibrium(SURFACE_AIR_PP);

    fmt::print("running over user supplied plan\n");
    {
        // this bit is copied from Result.cpp
        const size_t N = GetNumPoints(output.profile().back().time);
        const Eigen::VectorXd timeVec =
            Eigen::VectorXd::LinSpaced(N, 0, output.profile().back().time());
        const Eigen::VectorXd depthVec = Interpolate(output.time(), output.depth(), timeVec);
        for (size_t i = 1; i < timeVec.size(); ++i) {
            const Time duration(timeVec[i] - timeVec[i - 1]);
            // ensure(duration == MODEL_TIME_INC,
            //        fmt::format("time increment not expected: {} != {}",
            //        units::time::to_string(duration),
            //        units::time::to_string(MODEL_TIME_INC)));
            // This computes pressure at the average depth.
            // dipplanner uses Schreiner equation for segments with non-constant depth, which would
            // allow using large increments
            const Depth avgDepth((depthVec[i - 1] + depthVec[i]) * 0.5);
            const std::string& activeTank = output.getTankAtTime(Time(timeVec[i - 1]));
            const Mix& mix = output.tanks().at(activeTank).mix;
            const Mix::PartialPressure partialPressure =
                mix.partialPressure(avgDepth, output.water());
            model.update(partialPressure, duration);
        }
    }
    fmt::print("User supplied plan modeled. Ascending.\n");

    Time stopDuration = 0_min;
    size_t iteration = 0;
    while (output.profile().back().depth != 0_m) {
        fmt::print("----- Iteration: {}\n", ++iteration);
        fmt::print("Current depth: {}\n", str(output.profile().back().depth));

        // find the best mix for this depth
        // this doesn't need to be done every loop but whatever, it's not hurting anything right
        // now to do it unnecessarily?
        output.setTank(BestMix(output.tanks(), output.profile().back().depth, output.water()));

        // figure out what the ceiling is
        // round ceiling up to nearest 10 feet
        const Depth ceiling = units::math::ceil(model.ceiling() / STOP_DEPTH_INC) * STOP_DEPTH_INC;
        fmt::print("Current ceiling: {}\n", str(ceiling));

        // if ceiling is not less than current depth, stay for another minute
        if (ceiling >= output.profile().back().depth) {
            const std::string& activeTank = output.profile().back().tank;
            const Mix::PartialPressure partialPressure =
                output.tanks()
                    .at(activeTank)
                    .mix.partialPressure(output.profile().back().depth, output.water());
            model.update(partialPressure, STOP_TIME_INC);
            stopDuration += STOP_TIME_INC;
            fmt::print("Can't ascend yet. Current time at this stop: {}\n", str(stopDuration));
            // but don't record it yet because we don't know how long we'll be here and there's no
            // reason to have a ton of plan points
            continue;
        }
        fmt::print("Able to ascend.\n");

        // add a point to the profile for the end of this stop
        if (stopDuration > 0_s) {
            fmt::print("Recording this stop: {} at {}\n",
                       str(stopDuration),
                       str(output.profile().back().depth));
            output.addSegment(stopDuration, output.profile().back().depth);
            // reset the stop duration so we can start fresh next loop
            stopDuration = 0_min;
        }

        // ceiling is shallower than current depth. time to ascend!
        const Depth ascentDistance = output.profile().back().depth - ceiling;
        // round ascent time up to the nearest minute
        const Time ascentDuration =
            units::math::ceil(ascentDistance / ASCENT_RATE / STOP_TIME_INC) * STOP_TIME_INC;
        fmt::print("Ascent: {} elapsed, {} distance to {}\n",
                   str(ascentDuration),
                   str(ascentDistance),
                   str(ceiling));

        // TODO: swap to deco SCR from working SCR here.

        // TODO: this waits to ascend to a stop until it is already safe to be at that stop.
        //       other planners ascend to a stop planning to arrive right when it becomes safe to 
        //       be at the stop, resulting in a steeper gradient and shorter dive. this approach 
        //       below adds extra conservatism that was not requested.

        // ascend the model
        {
            const size_t N = GetNumPoints(ascentDuration);
            const Eigen::VectorXd timeVec =
                Eigen::VectorXd::LinSpaced(N,
                                           output.profile().back().time(),
                                           output.profile().back().time() + ascentDuration());
            const Eigen::VectorXd depthVec =
                Interpolate(Eigen::Vector2d(timeVec[0], timeVec[N - 1]),
                            Eigen::Vector2d(output.profile().back().depth(), ceiling()),
                            timeVec);
            for (size_t i = 1; i < timeVec.size(); ++i) {
                // FIXME:  there are time increment problems. it doesn't matter so much for the 
                //         version of this above but might matter here.
                // ensure(Time(timeVec[i] - timeVec[i - 1]) == MODEL_TIME_INC,
                //        "time increment wongggggg");
                // This computes pressure at the average depth.
                // dipplanner uses Schreiner equation for segments with non-constant depth, which
                // would allow using large increments
                const Depth avgDepth((depthVec[i - 1] + depthVec[i]) * 0.5);
                // use tank for last stop as the ascent tank
                const Mix& mix = output.tanks().at(output.profile().back().tank).mix;
                const Mix::PartialPressure partialPressure =
                    mix.partialPressure(avgDepth, output.water());
                model.update(partialPressure, Time(timeVec[i] - timeVec[i - 1]));
            }
        }

        // add a point to the profile for the ascent destination
        output.addSegment(ascentDuration, ceiling);
    }

    ensure(output.profile().back().depth == 0_m, "stopped somewhere other than the surface");

    output.finalize();
    return output;
}

} // namespace bungee