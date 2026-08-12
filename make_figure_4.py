import os

import geopandas as gpd
import matplotlib.pyplot as plt
import utils.stat as stat
from matplotlib.colors import ListedColormap

project_path = os.path.dirname(os.path.abspath(__file__))
tables_path = os.path.join(project_path, "Assets/Tables")
results_path = os.path.join(project_path, "Assets/Results")
fig_path = os.path.join(project_path, "Figures")
w11 = stat.load_asset("./Assets/Shapes/W11_HUC12/").to_crs(epsg=9822)
w11["centroid"] = w11["geometry"].centroid
states = stat.load_asset("./DATA/cb_2018_us_state_5m.shp").to_crs(epsg=4326)
states = states[
    states["STUSPS"].isin(
        ["CA", "WA", "OR", "ID", "MT", "UT", "AZ", "NM", "NV", "CO", "WY"]
    )
]


bap_intervals = ["<1%", "1-9.99%", "10-19.99%", "20-49.99%", "50-99.99%", "$\\geq$100%"]
bap_colors = ["#ffffb2", "#fed976", "#feb24c", "#e31a1c", "#bd0026", "#800026"]
rev_bap_colors = list(reversed(bap_colors))
bap_map = ListedColormap(bap_colors)
rev_bap_map = ListedColormap(rev_bap_colors)
rev_bap = list(reversed(bap_intervals))

eco_res_all = stat.load_asset(os.path.join(results_path, "ECO_MK_HG_L3_5070.csv"))
eco_res_all["Kendall's $\\tau$"] = eco_res_all["Kendall's $\\tau$"].astype(float)
eco_res_all["Changepoint (cp)"] = eco_res_all["Changepoint (cp)"].astype(int)


eco_res_all = eco_res_all.replace(
    {
        "Klamath Mountains/California High North Coast Range": "Klamath Mountains",
        "Arizona/New Mexico Mountains": "AZ/NM Mountains",
        "Arizona/New Mexico Plateau": "AZ/NM Plateau",
        "Eastern Cascades Slopes and Foothills": "Eastern Cascades",
        "Central Basin and Range": "Central Basin\nand Range",
        "Wasatch and Uinta Mountains": "Wasatch and\nUinta Mountains",
        "Northern Basin and Range": "Northern Basin\nand Range",
        "Northwestern Great Plains": "Northwestern\nGreat Plains",
    }
)


eco_res = eco_res_all[eco_res_all["Trend"] == "increasing"]
eco_res = eco_res[eco_res["Kendall's $\\tau$"] > 0.3]
print(eco_res["Changepoint (cp)"].mean())
eco_other = eco_res_all[eco_res_all["Trend"] != "increasing"]
plot_consume = stat.load_asset(
    os.path.join(tables_path, "POP_DS_HUC12_GROUPS_5070.csv")
)[
    [
        "FIRE_YEAR_INT",
        "huc12",
        "US_L3NAME",
        "NA_L2NAME",
        "NA_L1NAME",
        "huc12_sqkm",
        "BurnAreaEco",
        "POP_DS",
        "POP Interval",
    ]
]

plot_consume = plot_consume.replace(
    {
        "Klamath Mountains/California High North Coast Range": "Klamath Mountains",
        "Arizona/New Mexico Mountains": "AZ/NM Mountains",
        "Arizona/New Mexico Plateau": "AZ/NM Plateau",
        "Eastern Cascades Slopes and Foothills": "Eastern Cascades",
        "Central Basin and Range": "Central Basin\nand Range",
        "Wasatch and Uinta Mountains": "Wasatch and\nUinta Mountains",
        "Northern Basin and Range": "Northern Basin\nand Range",
        "Northwestern Great Plains": "Northwestern\nGreat Plains",
    }
)

plot_consume["FIRE_YEAR_INT"] = plot_consume["FIRE_YEAR_INT"].astype(int)
plot_consume["POP_DS"] = plot_consume["POP_DS"].astype(float)
plot_consume["BurnAreaEco"] = plot_consume["BurnAreaEco"].astype(float)
plot_consume["huc12_sqkm"] = plot_consume["huc12_sqkm"].astype(float)
plot_consume = (
    plot_consume.groupby(
        [
            "FIRE_YEAR_INT",
            "huc12",
            "huc12_sqkm",
            "US_L3NAME",
            "NA_L2NAME",
            "NA_L1NAME",
            "POP_DS",
            "POP Interval",
        ]
    )
    .sum()
    .reset_index()
)
plot_consume["BurnAreaPercentage"] = (
    plot_consume["BurnAreaEco"] / plot_consume["huc12_sqkm"]
) * 100
plot_consume_inc = plot_consume[plot_consume["US_L3NAME"].isin(eco_res["US_L3NAME"])]
plot_consume_inc = plot_consume_inc.merge(w11[["huc12", "centroid"]], on="huc12")
plot_consume_inc = gpd.GeoDataFrame(plot_consume_inc, geometry="centroid")
plot_consume_inc = plot_consume_inc.to_crs(epsg=4326)
# plot_consume_other = plot_consume_other.merge(w11[["huc12", "centroid"]], on="huc12")
# plot_consume_other = gpd.GeoDataFrame(plot_consume_other, geometry="centroid")
# plot_consume_other = plot_consume_other.to_crs(epsg=4326)


fig, (pre_ax, post_ax) = plt.subplots(1, 2, figsize=(18, 16), sharex=True, sharey=True)
states.plot(ax=pre_ax, facecolor="grey", alpha=0.5)
# plot_consume_other.plot(ax=ax, markersize=20, alpha=0.2, color="black")
cp_year = int(eco_res["Changepoint (cp)"].mean())
plot_consume_inc[plot_consume_inc["FIRE_YEAR_INT"] < cp_year].plot(
    ax=pre_ax,
    column="US_L3NAME",
    markersize=13,
    alpha=0.5,
    cmap="tab20b",
    legend=True,
    legend_kwds={
        "fontsize": 14,
        "title": "Ecoregion (Level 3)",
        "title_fontsize": 16,
        "loc": "lower center",
        "ncols": 5,
        "markerscale": 1.5,
        "handlelength": 0.1,
        "fancybox": False,
        "frameon": False,
        "labelspacing": 0.8,
        "bbox_to_anchor": (0.97, -0.3),
    },
)
pre_ax.tick_params(
    axis="x",
    labelsize=16,
    which="both",
)
pre_ax.tick_params(
    axis="y",
    labelsize=16,
    which="both",
)

pre_ax.text(-125, 31.3, "Mid to Late 20th Century", fontsize=18)
pre_ax.set_ylabel("Latitude", fontsize=18)
fig.text(0.5, 0.3, "Longitude", ha="center", fontsize=18)

states.plot(ax=pre_ax, facecolor="none", edgecolor="black", lw=2, alpha=0.5)
leg3 = pre_ax.get_legend()
for lh in leg3.legend_handles:
    lh.set_alpha(1)
pre_ax.set_xlim(-125.2, -102)
pre_ax.set_ylim(31, 49.5)


states.plot(ax=post_ax, facecolor="grey", alpha=0.5)
# plot_consume_other.plot(ax=ax, markersize=20, alpha=0.2, color="black")
plot_consume_inc[plot_consume_inc["FIRE_YEAR_INT"] > 1976].plot(
    ax=post_ax,
    column="US_L3NAME",
    markersize=13,
    alpha=0.5,
    cmap="tab20b",
)
post_ax.tick_params(
    axis="x",
    labelsize=16,
    which="both",
)
post_ax.tick_params(
    axis="y",
    labelsize=16,
    which="both",
)
post_ax.text(-125, 31.3, "Turn of the Century", fontsize=18)
states.plot(ax=post_ax, facecolor="none", edgecolor="black", lw=2, alpha=0.5)
fig.subplots_adjust(top=0.97, bottom=0.15, wspace=0, hspace=0)

fig.savefig(os.path.join(fig_path, "ECO_GEO.png"), dpi=300)
