from pathlib import Path
from typing import Iterator

import gpxpy
import numpy as np
import pandas as pd


def gpx_parser(gpx: gpxpy.mod_gpx.GPX) -> Iterator[dict]:
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                pointdict = {
                    "latitude": point.latitude,
                    "longitude": point.longitude,
                    "elevation": point.elevation,
                    "time": point.time,
                    "hr": np.nan,
                    "power": np.nan,
                }
                for extension in point.extensions:
                    if (
                        extension.tag
                        == "{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension"
                    ):
                        for child in extension:
                            if child.tag[-2:] == "hr":
                                pointdict["hr"] = int(child.text)
                    elif extension.tag == "power":
                        pointdict["power"] = int(extension.text)
                yield pointdict


def gpx_to_df(gpx_file_path: Path) -> pd.DataFrame:
    gpx = gpxpy.parse(open(gpx_file_path))
    return pd.DataFrame(gpx_parser(gpx))
