// Unit tests for the water module
use cenote::water::Water;
use dimensioned::si::{KG, M3};

#[test]
fn test_density() {
    assert_eq!(Water::Fresh.density(), 997.0474 * KG / M3);
    assert_eq!(Water::Salt.density(), 1023.6 * KG / M3);
}
