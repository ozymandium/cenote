#include <bungee/Mix.h>

namespace bungee {

Mix::Mix(const double fO2)
: fO2(fO2)
, fN2(1.0 - fO2)
{}

}