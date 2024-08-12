import pandas as pd
from geopy.distance import geodesic

from lapcruncher.types import Coord


def _calculate_distance_between_points(row: dict[str, float]) -> float:
    # Pair of coordinates for current and previous points
    coords_current = (row["latitude"], row["longitude"])
    coords_previous = (row["prev_latitude"], row["prev_longitude"])

    # Calculate distance using geodesic function
    return geodesic(coords_previous, coords_current).kilometers


def calculate_distance_km(df: pd.DataFrame) -> pd.Series:
    coord_df = df[["latitude", "longitude"]].copy()
    coord_df["prev_latitude"] = coord_df["latitude"].shift(
        1, fill_value=coord_df["latitude"].iloc[0]
    )
    coord_df["prev_longitude"] = coord_df["longitude"].shift(
        1, fill_value=coord_df["longitude"].iloc[0]
    )
    # Calculate distance for each row
    return coord_df.apply(_calculate_distance_between_points, axis=1).cumsum()


def enrich_pre_lap_data(df: pd.DataFrame) -> pd.DataFrame:
    df["distance_km"] = calculate_distance_km(df)
    df["power_4th_power"] = df.rolling(30).power.mean() ** 4
    df["power_above_1000W"] = df.power >= 1000
    df["power_below_1000W_above_800W"] = (df.power < 1000) & (df.power >= 800)
    df["power_below_800W_above_600W"] = (df.power < 800) & (df.power >= 600)
    return df


def detect_and_add_lap(df: pd.DataFrame, finish_coord: Coord) -> pd.DataFrame:
    df["distance_to_finish"] = df.apply(
        lambda row: geodesic(
            (row["latitude"], row["longitude"]), (finish_coord.lat, finish_coord.lon)
        ).meters,
        axis=1,
    )
    df["delta_distance_to_finish"] = df["distance_to_finish"].diff()
    df["passby"] = (
        (df["delta_distance_to_finish"].shift(-1) > 0)
        != (df["delta_distance_to_finish"] > 0)
    ) & (df["distance_to_finish"] < 25)
    df["lap"] = df["passby"].cumsum()
    df.drop(
        columns=["distance_to_finish", "delta_distance_to_finish", "passby"],
        inplace=True,
    )
    return df


def enrich_laps(df: pd.DataFrame) -> pd.DataFrame:
    df = (
        df.groupby("lap")
        .agg(
            time_start=("time", "min"),
            time_end=("time", "max"),
            distance_start_km=("distance_km", "min"),
            distance_km=("distance_km", "max"),
            hr_mean=("hr", "mean"),
            hr_max=("hr", "max"),
            power_mean=("power", "mean"),
            power_std=("power", "std"),
            power_max=("power", "max"),
            power_4th_power_mean=("power_4th_power", "mean"),
            seconds_power_above_1000W=("power_above_1000W", "sum"),
            seconds_power_below_1000W_above_800W=(
                "power_below_1000W_above_800W",
                "sum",
            ),
            seconds_power_below_800W_above_600W=("power_below_800W_above_600W", "sum"),
            temperature=("temperature", "mean"),
        )
        .assign(
            duration=lambda x: x["time_end"] - x["time_start"],
            normalized_power=lambda x: (x["power_4th_power_mean"] ** (1 / 4)).round(1),
            hr_mean=lambda x: x["hr_mean"].round(1),
            power_mean=lambda x: x["power_mean"].round(1),
            power_std=lambda x: x["power_std"].round(1),
            lap_distance_km=lambda x: (x["distance_km"] - x["distance_start_km"]),
            speed_mean=lambda x: (
                x["lap_distance_km"] / (x["duration"].dt.total_seconds() / 3600)
            ).round(1),
            temperature=lambda x: x["temperature"].round(1),
        )
        .drop(
            columns=[
                "time_start",
                "time_end",
                "power_4th_power_mean",
                "distance_start_km",
            ]
        )
        .pipe(lambda x: x.loc[x["duration"] > pd.Timedelta("1 minute")])
    )
    return df
