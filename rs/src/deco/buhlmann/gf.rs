/// Gradient Factors
pub struct Gf {
    pub lo: f64,
    pub hi: f64,
}

impl Gf {
    pub fn new(lo: f64, hi: f64) -> Result<Self, &'static str> {
        if lo <= 0.0 || lo > 1.0 {
            return Err("Gf::new: lo must be 0.0 <= lo <= 1.0");
        }
        if hi <= 0.0 || hi > 1.0 {
            return Err("Gf::new: hi must be 0.0 <= hi <= 1.0");
        }
        if lo > hi {
            return Err("Gf::new: lo must be <= hi");
        }
        Ok(Gf { lo, hi })
    }
}
