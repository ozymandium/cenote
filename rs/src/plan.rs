use crate::mix::{Mix, AIR};
use crate::units::{meter, min, Depth, Time, VolumeRate};
use crate::water::Water;

/// A dive plan is a series of points that describe the dive.
struct Point {
    /// Time elapsed since the beginning of the dive
    time: Time,
    /// Depth at this point
    depth: Depth,
    /// Breathing gas at this point, which will be used from now until the next point
    mix: Mix,
}

/// A segment is the time between two Points. The user inputs segments, and points are generated
/// from the segments.
struct Segment {
    /// How long this segment lasts
    duration: Time,
    /// The depth at the end of this segment, assuming linear change in depth over time
    end_depth: Depth,
    /// The gas that is used for this segment
    mix: Mix,
}

struct Profile {
    /// Water is assumed to be constant throughout the dive
    water: Water,
    /// The points that make up the profile
    points: Vec<Point>,
}

impl Profile {
    fn new(water: Water, segments: Vec<Segment>) -> Result<Self, &'static str> {
        if segments.len() == 0 {
            return Err("plan::Profile::new: segments is empty");
        }
        let first_segment = segments
            .first()
            .expect("plan::Profile::new: segments is empty");
        let mut points = vec![Point {
            time: min(0.0),
            depth: meter(0.0),
            mix: first_segment.mix.clone(),
        }];
        for segment in segments {
            // First, get the details from the last point without keeping a mutable reference
            let (last_time, last_mix) = points
                .last()
                .map(|p| (p.time, p.mix.clone()))
                .expect("plan::Profil e::new: points is empty");
            // Then, push the new point
            points.push(Point {
                time: last_time + segment.duration,
                depth: segment.end_depth,
                mix: segment.mix.clone(),
            });
        }
        Ok(Profile { water, points })
    }
}
