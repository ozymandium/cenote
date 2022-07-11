namespace bungee {

Tank::Tank(units::pressure::bar_t pressure) : _pressure(pressure) {}

Tank Tank::CreateFull() { return Tank(ServicePressure); }

units::volume::liter_t Tank::ServiceVolume() {
    return VolumeAtPressure(EmptyVolume, ServicePressure, ZFactor);
}

units::volume::liter_t Tank::volume() const {
    return VolumeAtPressure(EmptyVolume, pressure(), ZFactor);
}

void Tank::decreasePressure(units::pressure::bar_t diff) { pressureChange(-diff); }

void Tank::decreaseVolume(units::volume::liter_t diff) { volumeChange(-diff); }

void Tank::pressureChange(units::pressure::bar_t diff) { _pressure += diff; }

void Tank::volumeChange(units::volume::liter_t diff) {
    // FIXME
    pressureChange(diff / ServiceVolume() * units::pressure::atmosphere_t(1.0));
}

} // namespace bungee