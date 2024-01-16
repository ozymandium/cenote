use crate::units::{VolumeRate,CuFtPerMin};

struct Scr {
    /// The surface consumption rate when working
    work: VolumeRate,
    /// The surface consumption rate when decompressing
    deco: VolumeRate,
}

impl Scr {
    fn new(work: VolumeRate, deco: VolumeRate) -> Result<Self, &'static str> {
        if work.get::<CuFtPerMin>() <= 0.0 {
            return Err("scr::Scr::new: work must be > 0.0");
        }
        if deco.get::<CuFtPerMin>() <= 0.0 {
            return Err("scr::Scr::new: deco must be > 0.0");
        }
        Ok(Scr { work, deco })
    }
}

#[test]
fn test_scr_new() {
    use crate::units::cuft_per_min;

    let work = cuft_per_min(1.0);
    let deco = cuft_per_min(2.0);
    let scr = Scr::new(work, deco).unwrap();
    assert_eq!(scr.work, work);
    assert_eq!(scr.deco, deco);
    assert!(Scr::new(work, cuft_per_min(0.0)).is_err());
    assert!(Scr::new(cuft_per_min(0.0), deco).is_err());
}