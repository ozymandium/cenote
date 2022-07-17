#pragma once

#include "Tank.h"
#include "Water.h"
#include "custom_units.h"

namespace bungee {

VolumeRate ScrFromSac(PressureRate sac, const Tank& tank);

PressureRate SacFromScr(VolumeRate scr, const Tank& tank);

VolumeRate ScrAtDepth(VolumeRate scr, Depth depth, Water water);

} // namespace bungee
