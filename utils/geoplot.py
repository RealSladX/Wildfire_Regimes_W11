import geopandas as gpd
from matplotlib.patches import Patch
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import pycollection.asset_manager.paths as paths
from shapely import get_coordinates
import palettable.colorbrewer.sequential as seqs

plt.rcParams["xtick.labelsize"] = "xx-large"
plt.rcParams["ytick.labelsize"] = "xx-large"
plt.rcParams["axes.labelsize"] = "xx-large"
plt.rcParams["legend.fontsize"] = "large"

seqs_cmaps = {
    "Blues": seqs.Blues_9.mpl_colormap,
    "Reds": seqs.Reds_9.mpl_colormap,
    "Greens": seqs.Greens_9.mpl_colormap,
}

save_path = paths.figures_path


def plot_polygon_collection(
    ax,
    geoms,
    label,
    facecolor=None,
    edgecolor="black",
    alpha=1.0,
    linewidth=0.1,
    **kwargs,
):
    """Plot a collection of Polygon geometries"""
    patches = []

    for poly in geoms:
        a = get_coordinates(poly)  # if values is not None:
        patches.append(Polygon(a))

    patches = PatchCollection(
        patches,
        facecolor=facecolor,
        linewidth=linewidth,
        edgecolor=edgecolor,
        alpha=alpha,
        **kwargs,
    )
    proxy_patches = Patch(facecolor=facecolor, label=label)
    ax.add_collection(patches, autolim=True)
    ax.autoscale_view()
    ax.legend(handles=[proxy_patches])
    plt.savefig(save_path / f"{label}.png", dpi=300)
    return patches


def geoplot(gpdf_path, label, color, ax):
    geoms = gpd.read_file(gpdf_path).to_crs(epsg=4326)
    col = plot_polygon_collection(ax, geoms.geometry, label, facecolor=color)


def geoplot_var(gpdf_path, column, cmap, ax):
    geoms = (
        gpd.read_file(gpdf_path)
        .to_crs(epsg=4326)
        .plot(ax=ax, column=column, cmap=seqs_cmaps[cmap])
    )
