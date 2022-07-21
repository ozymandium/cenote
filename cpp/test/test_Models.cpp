#include "utils.h"
#include <bungee/deco/buhlmann/Models.h>

using namespace bungee::deco::buhlmann;
using namespace units::literals;

TEST(Models, ZHL_16A)
{
    struct Vals {
        size_t idx;
        double t, a, b;
    };
    // https://en.wikipedia.org/wiki/B%C3%BChlmann_decompression_algorithm
    // clang-format off
    const std::vector<Vals> TABLE {
        {0 , 4   , 1.2599, 0.5050},
        {2 , 8   , 1.0000, 0.6514},
        {3 , 12.5, 0.8618, 0.7222},
        {4 , 18.5, 0.7562, 0.7725},
        {5 , 27  , 0.6667, 0.8125},
        {6 , 38.3, 0.5933, 0.8434},
        {7 , 54.3, 0.5282, 0.8693},
        {8 , 77  , 0.4701, 0.8910},
        {9 , 109 , 0.4187, 0.9092},
        {10, 146 , 0.3798, 0.9222},
        {11, 187 , 0.3497, 0.9319},
        {12, 239 , 0.3223, 0.9403},
        {13, 305 , 0.2971, 0.9477},
        {14, 390 , 0.2737, 0.9544},
        {15, 498 , 0.2523, 0.9602},
        {16, 635 , 0.2327, 0.9653}
    };
    // clang-format on
    const CompartmentList& compartmentList = *GetCompartmentList(Model::ZHL_16A);
    for (const auto& expected : TABLE) {
        Compartment::Params params = Compartment::Params(compartmentList[expected.idx], 0.3, 0.7);
        EXPECT_EQ(params.halfLife(), expected.t);
        EXPECT_NEAR(params.a(), expected.a, 5e-5);
        EXPECT_NEAR(params.b(), expected.b, 5e-5);
    }
}
