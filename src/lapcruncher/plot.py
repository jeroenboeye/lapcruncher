import pandas as pd
from matplotlib import pyplot as plt

from lapcruncher.types import Coord


def plot_coord_on_route(df: pd.DataFrame, coord: Coord) -> None:
    plt.plot(df.longitude, df.latitude)
    plt.annotate("Start", (df.longitude.iloc[0], df.latitude.iloc[0]))
    plt.annotate("End", (df.longitude.iloc[-1], df.latitude.iloc[-1]))
    plt.plot(coord.lon, coord.lat, "ro")
    plt.show()
