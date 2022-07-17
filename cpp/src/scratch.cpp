#include <bungee/bungee.h>

#include <iostream>

using namespace bungee;
using namespace units::literals;

int main() {

    auto volrate = 1_L_per_min;
    std::cout << units::abbreviation(volrate) << std::endl;

}