import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from lapcruncher.types import Coord


def plot_coord_on_route(df: pd.DataFrame, coord: Coord) -> None:
    plt.plot(df.longitude, df.latitude)
    plt.annotate("Start", (df.longitude.iloc[0], df.latitude.iloc[0]))
    plt.annotate("End", (df.longitude.iloc[-1], df.latitude.iloc[-1]))
    plt.plot(coord.lon, coord.lat, "ro")
    plt.show()


def plot_route_with_hue_param(df: pd.DataFrame, hue: str) -> None:
    """
    Plot the route with a parameter, i.e. power, speed, etc.

    To support laps the coordinates are rounded to 4 decimal places
    and the hue parameter averaged.
    """
    grouped_df = (
        df.assign(
            longitude=lambda x: x.longitude.round(4),
            latitude=lambda x: x.latitude.round(4),
        )
        .groupby(["longitude", "latitude"])[hue]
        .mean()
        .reset_index()
    )
    sns.scatterplot(
        data=grouped_df,
        x="longitude",
        y="latitude",
        hue=hue,
        linewidth=0,
        s=6,
        palette="RdYlBu_r",
    )
    plt.show()
