/*

scratch/prototype code in need of cleanup.
yes the whole repo is prototype code that's god awful, but this is like, real bad.

*/

#include <bungee/Planner.h>
#include <bungee/Result.h> // for Interpolate. move that
#include <bungee/deco/buhlmann/Buhlmann.h>
#include <bungee/ensure.h>
#include <bungee/utils.h>

using namespace units::literals;
using namespace bungee::deco::buhlmann;

namespace bungee {

Plan Replan(const Plan& input)
{
    // start plan with the same configuration
    Plan output(input.water(), input.gf(), input.scr(), input.tanks());
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
    Buhlmann model(Buhlmann::Params{.water = output.water(), .model = Model::ZHL_16A});
    // assume infinite surface interval preceding this dive.
    model.equilibrium(SURFACE_AIR_PP);

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

    // do the ascent

    // get the gf at a given depth based on the last point, which will be where the gf slop is set.
    // have to capture by value since we are getting a reference to the last point in the profile
    //
    // TODO: make this a class method of Plan after the replan function is moved to Plan. This
    // requires making the ascentBeginDepth a class member.
    const Depth ascentBeginDepth = output.profile().back().depth;
    auto gfLookup = [&](const Depth depth) {
        const double depthFraction = (depth / ascentBeginDepth)();
        return (output.gf().low - output.gf().high) * depthFraction + output.gf().high;
    };

    // iteratively find the ceiling
    auto ceilingLookup = [&]() {
        // initialize to just any old depth
        Depth ceiling = output.profile().back().depth;
        // FIXME: guard against infinite loops toggling between ceilings. just check on an it counter
        // and if it gets hit pick the lowest ceiling of the two
        while (true) {
            const double requestedGf = gfLookup(ceiling);
            const Depth newCeiling = units::math::ceil(model.ceiling(requestedGf) / STOP_DEPTH_INC) * STOP_DEPTH_INC;
            if (newCeiling == ceiling) {
                break;
            } else {
                ceiling = newCeiling;
            }
        }
        return ceiling;
    };

    Time stopDuration = 0_min;
    size_t iteration = 0;
    while (output.profile().back().depth != 0_m) {

        // find the best mix for this depth
        // this doesn't need to be done every loop but whatever, it's not hurting anything right
        // now to do it unnecessarily?
        output.setTank(output.bestMix(output.profile().back().depth));

        // figure out what the ceiling is
        // round ceiling up to nearest 10 feet
        const Depth ceiling = ceilingLookup();

        // if ceiling is not less than current depth, stay for another minute
        if (ceiling >= output.profile().back().depth) {
            const std::string& activeTank = output.profile().back().tank;
            const Mix::PartialPressure partialPressure =
                output.tanks()
                    .at(activeTank)
                    .mix.partialPressure(output.profile().back().depth, output.water());
            model.update(partialPressure, STOP_TIME_INC);
            stopDuration += STOP_TIME_INC;
            // but don't record it yet because we don't know how long we'll be here and there's no
            // reason to have a ton of plan points
            continue;
        }

        // add a point to the profile for the end of this stop
        if (stopDuration > 0_s) {
            output.addSegment(stopDuration, output.profile().back().depth);
            // reset the stop duration so we can start fresh next loop
            stopDuration = 0_min;
        }

        // ceiling is shallower than current depth. time to ascend!
        const Depth ascentDistance = output.profile().back().depth - ceiling;
        // round ascent time up to the nearest minute
        const Time ascentDuration =
            units::math::ceil(ascentDistance / ASCENT_RATE / STOP_TIME_INC) * STOP_TIME_INC;

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