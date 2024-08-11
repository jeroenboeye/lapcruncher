import hashlib
from datetime import datetime
from pathlib import Path
from typing import Callable, Self

import gpxpy
import pandas as pd
from attrs import define, field

from lapcruncher.ingest import gpx_parser
from lapcruncher.transform import enrich_pre_lap_data


@define
class Ride:
    gpx_hash: str
    time: datetime = field(repr=lambda x: x.isoformat())
    distance: float = field(converter=float)
    data: pd.DataFrame = field(repr=False)
    gpx: gpxpy.mod_gpx.GPX = field(repr=False)

    @classmethod
    def from_gpx(cls: Self, gpx_path: Path) -> Self:
        md5_hash = hashlib.md5()
        with open(gpx_path, "rb") as file:
            while chunk := file.read(4096):
                md5_hash.update(chunk)
        with open(gpx_path) as file:
            gpx = gpxpy.parse(file)
        frame = pd.DataFrame(gpx_parser(gpx))
        data = enrich_pre_lap_data(frame)
        return cls(
            gpx_hash=md5_hash.hexdigest(),
            time=gpx.time,
            distance=data.distance_km.max(),
            data=data,
            gpx=gpx,
        )


@define
class RideCollection:
    rides: list[Ride]

    @classmethod
    def from_gpx_folder(cls, path: Path):
        return cls(rides=[Ride.from_gpx(file) for file in path.glob("*.gpx")])

    def filter(self, func: Callable[[Ride], bool]) -> Self:
        return RideCollection(rides=[r for r in self.rides if func(r)])
