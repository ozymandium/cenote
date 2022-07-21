#include "utils.h"
#include <bungee/deco/buhlmann/Buhlmann.h>

using namespace bungee;
using namespace bungee::deco::buhlmann;

class TestGetters : public ::testing::Test {
public:
    void SetUp()
    {
        buhlmann =
            std::make_shared<Buhlmann>(Buhlmann::Params{Water::SALT, Model::ZHL_16A, 1.0, 1.0});
        std::vector<Pressure> pressures(buhlmann->compartmentCount());
        for (size_t i = 0; i < pressures.size(); ++i) {
            pressures[i] = units::pressure::bar_t(i);
        }
        buhlmann->setCompartmentPressures(pressures);
    }
    std::shared_ptr<Buhlmann> buhlmann;
};

TEST_F(TestGetters, M0s)
{
    const std::vector<Pressure> m0s = buhlmann->M0s();
    ASSERT_EQ(m0s.size(), buhlmann->compartmentCount());
    for (size_t i = 0; i < buhlmann->compartmentCount(); ++i) {
        const Compartment::Params params(GetCompartmentList(Model::ZHL_16A)->at(i), 1.0, 1.0);
        const Pressure expectedM0 = (Pressure(i) - params.a) * params.b;
        EXPECT_EQ(m0s[i], expectedM0);
    }
}

TEST_F(TestGetters, M0)
{
    const std::vector<Pressure> m0s = buhlmann->M0s();
    EXPECT_EQ(buhlmann->M0(), m0s.back());
}

TEST_F(TestGetters, gfs) {}
