/*

scratch/prototype code in need of cleanup.
yes the whole repo is prototype code that's god awful, but this is like, real bad.

*/

#include <bungee/Planner.h>
#include <bungee/Result.h> // for Interpolate. move that
#include <bungee/deco/buhlmann/Buhlmann.h>
#include <bungee/ensure.h>
#include <bungee/utils.h>

#include <fmt/format.h>

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

    for (size_t i = 1; i < output.profile().size(); ++i) {
        const Plan::Point& start = output.profile()[i - 1];
        const Plan::Point& end = output.profile()[i];
        const Time duration = end.time - start.time;
        // use the same mix throughout. if the mix changes at the end point that is only
        // actually used *after* this interval.
        const Mix& mix = output.tanks().at(start.tank).mix;
        const Mix::PartialPressure partialPressureStart =
            mix.partialPressure(start.depth, output.water());
        if (start.depth == end.depth) {
            model.constantPressureUpdate(partialPressureStart, duration);
        }
        else {
            const Mix::PartialPressure partialPressureEnd =
                mix.partialPressure(end.depth, output.water());
            model.variablePressureUpdate(partialPressureStart, partialPressureEnd, duration);
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

    // // iteratively find the ceiling
    // auto ceilingLookup = [&]() {
    //     // initialize to just any old depth
    //     Depth ceiling = output.profile().back().depth;
    //     // FIXME: guard against infinite loops toggling between ceilings. just check on an it
    //     // counter and if it gets hit pick the lowest ceiling of the two
    //     while (true) {
    //         const double requestedGf = gfLookup(ceiling);
    //         const Depth newCeiling =
    //             units::math::ceil(model.ceiling(requestedGf) / STOP_DEPTH_INC) * STOP_DEPTH_INC;
    //         if (newCeiling == ceiling) {
    //             break;
    //         }
    //         else {
    //             ceiling = newCeiling;
    //         }
    //     }
    //     return ceiling;
    // };

    Time stopDuration = 0_min;
    size_t iteration = 0;
    while (output.profile().back().depth > 0_m) {
        ensure(output.profile().back().depth >= 0_m, "why are you planning negative depths?");

        // find the best mix for this depth
        // this doesn't need to be done every loop but whatever, it's not hurting anything right
        // now to do it unnecessarily?
        output.setTank(output.bestMix(output.profile().back().depth));

        // figure out what the ceiling is by "visiting" it with a test model copied from the current
        // model, and seeing if we're over the desired gradient factor the hypothetical model
        // arrives there.
        Depth ceiling = output.profile().back().depth;
        // for (size_t ceilingIt = 0; ceilingIt < 3; ++ceilingIt)
        size_t ceilingIt = 0;
        while (ceiling > 0_m) {
            // This loop will really only run more than twice during the ascent from the bottom
            // to the first stop. When an ascent can be made between successive stops, it will run
            // twice. When no ascent can be made, it will run once.

            // see what the ceiling would be if we ascended one step above the current ceiling.
            const Depth testCeiling = units::math::round((ceiling - STOP_DEPTH_INC)/ STOP_DEPTH_INC) * STOP_DEPTH_INC;
            // see how much time it would take to ascend, round up to nearest minute
            const Depth ascentDistance = output.profile().back().depth - testCeiling;
            // round ascent time up to the nearest minute
            const Time ascentDuration =
                units::math::ceil(ascentDistance / ASCENT_RATE / STOP_TIME_INC) * STOP_TIME_INC;

            // create hypothetical model and ascend it to the next stop
            Buhlmann testModel(model);
            // FIXME: this won't work for hypoxic mixes
            // assume the current gas is fine to use for the ascent.
            const Mix& mix = output.tanks().at(output.profile().back().tank).mix;
            const Mix::PartialPressure partialPressureCurrentDepth =
                mix.partialPressure(output.profile().back().depth, output.water());
            const Mix::PartialPressure partialPressureTestCeiling =
                mix.partialPressure(testCeiling, output.water());
            testModel.variablePressureUpdate(
                partialPressureCurrentDepth, partialPressureTestCeiling, ascentDuration);
            // have to look up the gf at the ceiling, not the current place
            const double gfAtTestCeiling = gfLookup(testCeiling);
            // once we get there, did we go too far? see what the safe depth is after having
            // traveled to this theoretical stop
            const Depth ceilingAtTestCeiling = testModel.ceiling(gfAtTestCeiling);

            if (ceilingAtTestCeiling <= testCeiling) {
                // once we get there it will be safe to get there.
                // addition floating point errors require rounding.
                ceiling = testCeiling;
            }
            else {
                // we will cross the true ceiling line getting to this stop. don't save the test
                // ceiling and abort this loop.
                break;
            }
            // FIXME: could just copy values from testCeiling over to ceiling? have a bunch of shit
            // calculated here and we just discard it to recompute it again below
        }

        // if ceiling is not less than current depth, stay for another minute
        if (ceiling >= output.profile().back().depth) {
            const std::string& activeTank = output.profile().back().tank;
            const Mix::PartialPressure partialPressure =
                output.tanks()
                    .at(activeTank)
                    .mix.partialPressure(output.profile().back().depth, output.water());
            model.constantPressureUpdate(partialPressure, STOP_TIME_INC);
            stopDuration += STOP_TIME_INC;
            // but don't record it yet because we don't know how long we'll be here and there's no
            // reason to have a ton of plan points
            continue;
        }
        // else ceiling is above the current depth

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
            const Mix& mix = output.tanks().at(output.profile().back().tank).mix;
            const Mix::PartialPressure partialPressureStart =
                mix.partialPressure(output.profile().back().depth, output.water());
            const Mix::PartialPressure partialPressureEnd =
                mix.partialPressure(ceiling, output.water());
            model.variablePressureUpdate(partialPressureStart, partialPressureEnd, ascentDuration);
        }

        // add a point to the profile for the ascent destination
        output.addSegment(ascentDuration, ceiling);
    }
    ensure(output.profile().back().depth == 0_m, 
        fmt::format("Replan: stopped somewhere other than the surface {}\n", str(output.profile().back().depth)));

    output.finalize();
    return output;
}

} // namespace bungee