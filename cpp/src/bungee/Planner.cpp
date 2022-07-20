#include <bungee/Planner.h>

namespace bungee {

Plan Replan(const Plan& input)
{
    Plan output(input.water(), input.scr(), input.tanks());

    output.finalize();

    return output;
}

} // namespace bungee