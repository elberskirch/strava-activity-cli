"""Data models for Strava activities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Activity:
    """Represents a Strava activity."""

    id: int
    name: str
    type: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    start_date: datetime
    start_date_local: datetime
    average_speed: float | None = None
    max_speed: float | None = None
    average_heartrate: float | None = None
    max_heartrate: float | None = None
    description: str | None = None
    calories: float | None = None
    gear_id: str | None = None
    trainer: bool = False
    commute: bool = False
    private: bool = False

    @classmethod
    def from_strava_activity(cls, activity: Any) -> "Activity":
        """Create Activity from stravalib Activity object.

        Args:
            activity: stravalib Activity object

        Returns:
            Activity instance
        """

        # Helper to extract seconds from timedelta or int
        def get_seconds(value):
            if value is None:
                return 0
            if hasattr(value, "total_seconds"):
                return int(value.total_seconds())
            return int(value)

        # Extract activity type - handle both string and RelaxedActivityType
        activity_type = activity.type
        if hasattr(activity_type, "root"):
            activity_type = activity_type.root
        else:
            activity_type = str(activity_type)

        return cls(
            id=activity.id,
            name=activity.name,
            type=activity_type,
            distance=float(activity.distance) if activity.distance else 0.0,
            moving_time=get_seconds(activity.moving_time),
            elapsed_time=get_seconds(activity.elapsed_time),
            total_elevation_gain=float(activity.total_elevation_gain)
            if activity.total_elevation_gain
            else 0.0,
            start_date=activity.start_date,
            start_date_local=activity.start_date_local,
            average_speed=float(activity.average_speed) if activity.average_speed else None,
            max_speed=float(activity.max_speed) if activity.max_speed else None,
            average_heartrate=float(activity.average_heartrate)
            if activity.average_heartrate
            else None,
            max_heartrate=float(activity.max_heartrate) if activity.max_heartrate else None,
            description=getattr(activity, "description", None),
            calories=float(activity.calories) if getattr(activity, "calories", None) else None,
            gear_id=getattr(activity, "gear_id", None),
            trainer=getattr(activity, "trainer", False),
            commute=getattr(activity, "commute", False),
            private=getattr(activity, "private", False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert activity to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the activity
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "distance": self.distance,
            "moving_time": self.moving_time,
            "elapsed_time": self.elapsed_time,
            "total_elevation_gain": self.total_elevation_gain,
            "start_date": self.start_date.isoformat(),
            "start_date_local": self.start_date_local.isoformat(),
            "average_speed": self.average_speed,
            "max_speed": self.max_speed,
            "average_heartrate": self.average_heartrate,
            "max_heartrate": self.max_heartrate,
            "description": self.description,
            "calories": self.calories,
            "gear_id": self.gear_id,
            "trainer": self.trainer,
            "commute": self.commute,
            "private": self.private,
        }

    def format_table_row(self) -> dict[str, str]:
        """Format activity for table display.

        Returns:
            Dictionary with formatted strings for display
        """
        distance_km = self.distance / 1000
        hours = self.moving_time // 3600
        minutes = (self.moving_time % 3600) // 60

        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        return {
            "ID": str(self.id),
            "Date": self.start_date_local.strftime("%Y-%m-%d %H:%M"),
            "Name": self.name,
            "Type": self.type,
            "Distance": f"{distance_km:.2f} km",
            "Time": time_str,
            "Elevation": f"{self.total_elevation_gain:.0f} m",
        }
