import os

from matplotlib.patches import Patch
import numpy as np
import utils.stat as stat
from matplotlib.colors import ListedColormap
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import time

start = time.time()


def categorize_percent(percent):
    if percent < 1:
        return "<1%"
    elif percent < 10:
        return "1-9.99%"
    elif percent < 20:
        return "10-19.99%"
    elif percent < 50:
        return "20-49.99%"
    elif percent < 100:
        return "50-99.99%"
    else:
        return "$\\geq$100%"


project_path = os.path.dirname(os.path.abspath(__file__))
shapes_path = os.path.join(project_path, "Assets/Shapes")
tables_path = os.path.join(project_path, "Assets/Tables")
figs_path = os.path.join(project_path, "Figures")
w11 = stat.load_asset("./Assets/Shapes/W11_HUC12/").to_crs(epsg=9822)
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

water_colors = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"]
water_intervals = ["20th", "40th", "60th", "80th", "99th"]
rev_water_colors = list(reversed(water_colors))
water_map = ListedColormap(water_colors)
rev_water_map = ListedColormap(rev_water_colors)
rev_water = list(reversed(water_intervals))

pop_colors = ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08519c", "#08306b"]
pop_intervals = [
    "0",
    "<100",
    "100-999",
    "1,000-9,999",
    "10,000-99,999",
    "$\\geq100,000$",
]
rev_pop_colors = list(reversed(pop_colors))
pop_map = ListedColormap(pop_colors)
rev_pop_map = ListedColormap(rev_pop_colors)
rev_pop = list(reversed(pop_intervals))


print(f"{time.time() - start:0.1f}")
plot_consume = stat.load_asset("./Assets/Tables/POP_DS_HUC12_GROUPS_5070.csv")[
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
plot_consume["BAP Interval"] = plot_consume["BurnAreaPercentage"].apply(
    categorize_percent
)
plot_consume["BAP Interval"] = pd.Series(plot_consume["BAP Interval"], dtype="category")
plot_consume["POP Interval"] = pd.Series(plot_consume["POP Interval"], dtype="category")

plot_consume["BAP Interval"] = plot_consume["BAP Interval"].cat.set_categories(
    bap_intervals, ordered=True
)
plot_consume["POP Interval"] = plot_consume["POP Interval"].cat.set_categories(
    pop_intervals, ordered=True
)

plot_consume = plot_consume.merge(w11[["huc12", "geometry"]], on="huc12")
plot_consume = gpd.GeoDataFrame(plot_consume, geometry="geometry")
plot_consume = plot_consume.to_crs(epsg=4326)
print(f"{time.time() - start:0.1f}")

presum = 0
postsum = 0


# --- build huc12-level pre/post means ---
pop_res = stat.load_asset("./Assets/Results/POP_DS_RESULTS_5070.csv")
pop_res["Changepoint (cp)"] = pop_res["Changepoint (cp)"].astype(int)

cp_year = pop_res[pop_res["Trend"] == "increasing"]["Changepoint (cp)"].min()

pop_huc12 = (
    plot_consume[plot_consume["POP_DS"] > 999]
    .assign(period=lambda d: np.where(d["FIRE_YEAR_INT"] < cp_year, "pre", "post"))
    .groupby(["huc12", "period"], as_index=False)
    .agg(
        POP_DS=("POP_DS", "mean"),
        geometry=("geometry", "first"),
    )
)

# wide table: one row per huc12
pop_diff = pop_huc12.pivot(
    index="huc12", columns="period", values="POP_DS"
).reset_index()

# attach geometry once
geom = plot_consume[["huc12", "geometry"]].drop_duplicates("huc12")
pop_diff = pop_diff.merge(geom, on="huc12", how="left")
pop_diff = gpd.GeoDataFrame(pop_diff, geometry="geometry", crs=plot_consume.crs)

# difference metrics
pop_diff["diff_abs"] = pop_diff["post"] - pop_diff["pre"]
pop_diff["diff_pct"] = ((pop_diff["post"] - pop_diff["pre"]) / pop_diff["pre"]) * 100

# optional: classify presence/absence
pop_diff["change_class"] = np.select(
    [
        pop_diff["pre"].isna() & pop_diff["post"].notna(),
        pop_diff["pre"].notna() & pop_diff["post"].isna(),
        pop_diff["diff_abs"] == 0,
    ],
    [
        "Turn of the Century",
        "Mid to late 20th Century",
        "No Increase",
    ],
    default="No data",
)
change_colors = {
    "Mid to late 20th Century": "#b2182b",
    "No Increase": "#969696",
    "Turn of the Century": "#252525",
}


fig_chg, ax_chg = plt.subplots(1, 1, figsize=(10, 12))

states.plot(ax=ax_chg, facecolor="grey", alpha=0.07)

for cls, color in change_colors.items():
    subset = pop_diff[pop_diff["change_class"] == cls]
    if len(subset):
        subset.plot(
            ax=ax_chg,
            facecolor=color,
            edgecolor="none",
            alpha=0.9,
            label=cls,
        )

states.plot(ax=ax_chg, facecolor="None", edgecolor="black", lw=2, alpha=0.3)

ax_chg.set_xlim(-128.6, -102)
ax_chg.set_ylim(31, 49.5)
legend_order = [
    "Mid to late 20th Century",
    "Turn of the Century",
    "No Increase",
]

ax_chg.set_xlabel("Longitude", fontsize=18)
ax_chg.set_ylabel("Latitude", fontsize=18)

ax_chg.tick_params(
    axis="x",
    labelsize=16,
    which="both",
)
ax_chg.tick_params(
    axis="y",
    labelsize=16,
    which="both",
)

handles = [
    Patch(facecolor=change_colors[cls], edgecolor="none", label=cls)
    for cls in legend_order
    if (pop_diff["change_class"] == cls).any()
]

if handles:
    ax_chg.legend(handles=handles, frameon=False, fontsize=14, loc="lower left")
else:
    print("No change classes present; skipping change-class legend.")
fig_chg.savefig(os.path.join(figs_path, "POP_DS_GEO_CHANGE_CLASS"), dpi=300)
